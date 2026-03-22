from app.models.jobs import JobStatus
from app.models.tool_inputs import GenerateImageInput, JobLookupInput
from app.tools._common import execute_tool


def test_mock_job_lifecycle(runtime_services):
    provider, jobs = runtime_services
    accepted = execute_tool('generate_image', GenerateImageInput(prompt='test'), provider.generate_image, jobs)
    assert accepted['status'] == JobStatus.queued.value

    status_one = execute_tool('get_job_status', JobLookupInput(job_id=accepted['job_id']), provider.get_job_status, jobs)
    assert status_one['status'] == JobStatus.processing.value
    assert status_one['progress'] == 50

    status_two = execute_tool('get_job_status', JobLookupInput(job_id=accepted['job_id']), provider.get_job_status, jobs)
    assert status_two['status'] == JobStatus.completed.value
    assert status_two['result_url'].endswith('.bin')
