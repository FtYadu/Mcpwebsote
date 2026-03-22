"""Batch workflow execution with dependency resolution for AI agents."""

from __future__ import annotations

from copy import deepcopy
from typing import Any
from uuid import uuid4

from app.models.errors import DigenError, ErrorDetail
from app.models.tool_inputs import WorkflowSubmissionInput, WorkflowTaskInput
from app.models.tool_outputs import WorkflowExecutionOutput, WorkflowTaskResult
from app.runtime.tool_registry import ToolRegistry


class WorkflowService:
    """Executes chained tool invocations with task dependency support."""

    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def execute(self, submission: WorkflowSubmissionInput) -> WorkflowExecutionOutput:
        workflow_id = f'workflow-{uuid4().hex[:12]}'
        tasks_by_id = {task.id: task for task in submission.tasks}
        results: dict[int, WorkflowTaskResult] = {}

        for task in submission.tasks:
            self._validate_dependencies(task, tasks_by_id)
            blocked_dependency = next((dep for dep in task.depends_on if results[dep].status != 'completed'), None)
            if blocked_dependency is not None:
                results[task.id] = WorkflowTaskResult(
                    id=task.id,
                    tool=task.tool,
                    status='skipped',
                    error=ErrorDetail(code='DEPENDENCY_FAILED', message=f'Task {task.id} was skipped because dependency {blocked_dependency} did not complete.', retryable=False),
                )
                continue
            try:
                resolved_payload = self._resolve_payload(task.parameters, results)
                output = self._registry.execute(task.tool, resolved_payload)
                if output.get('error') is not None:
                    detail = ErrorDetail.model_validate(output['error'])
                    results[task.id] = WorkflowTaskResult(id=task.id, tool=task.tool, status='failed', output=output, error=detail)
                else:
                    results[task.id] = WorkflowTaskResult(id=task.id, tool=task.tool, status='completed', output=output)
            except DigenError as exc:
                results[task.id] = WorkflowTaskResult(id=task.id, tool=task.tool, status='failed', error=exc.detail)

        overall = 'completed' if all(result.status == 'completed' for result in results.values()) else 'failed'
        return WorkflowExecutionOutput(workflow_id=workflow_id, status=overall, tasks=list(results.values()))

    def _validate_dependencies(self, task: WorkflowTaskInput, tasks_by_id: dict[int, WorkflowTaskInput]) -> None:
        for dependency in task.depends_on:
            if dependency not in tasks_by_id:
                raise DigenError('UNKNOWN_DEPENDENCY', f'Task {task.id} depends on undefined task {dependency}.', False)
            if dependency >= task.id:
                raise DigenError('INVALID_DEPENDENCY_ORDER', 'Dependencies must reference an earlier task id.', False)

    def _resolve_payload(self, payload: dict[str, Any], results: dict[int, WorkflowTaskResult]) -> dict[str, Any]:
        working = deepcopy(payload)
        return self._resolve_value(working, results)

    def _resolve_value(self, value: Any, results: dict[int, WorkflowTaskResult]) -> Any:
        if isinstance(value, dict):
            return {key: self._resolve_value(item, results) for key, item in value.items()}
        if isinstance(value, list):
            return [self._resolve_value(item, results) for item in value]
        if isinstance(value, str) and value.startswith('$tasks.'):
            return self._lookup_reference(value, results)
        return value

    def _lookup_reference(self, reference: str, results: dict[int, WorkflowTaskResult]) -> Any:
        parts = reference.split('.')
        if len(parts) < 3 or parts[0] != '$tasks':
            raise DigenError('INVALID_REFERENCE', f'Invalid workflow reference {reference!r}.', False)
        task_id = int(parts[1])
        result = results.get(task_id)
        if result is None or result.output is None:
            raise DigenError('MISSING_REFERENCE', f'Workflow reference {reference!r} could not be resolved.', False)
        current: Any = result.output
        for part in parts[2:]:
            if not isinstance(current, dict) or part not in current:
                raise DigenError('MISSING_REFERENCE', f'Workflow reference {reference!r} could not be resolved.', False)
            current = current[part]
        return current
