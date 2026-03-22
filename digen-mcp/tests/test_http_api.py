from fastapi.testclient import TestClient


def test_healthz_reports_dependencies_and_tool_count(test_client: TestClient):
    response = test_client.get('/healthz')
    assert response.status_code == 200
    payload = response.json()
    assert payload['database']['ok'] is True
    assert payload['redis']['backend'] == 'memory'
    assert payload['tools']['count'] >= 10


def test_tools_endpoint_exposes_registry_metadata(test_client: TestClient):
    response = test_client.get('/tools')
    assert response.status_code == 200
    tools = response.json()['tools']
    names = {tool['name'] for tool in tools}
    assert 'generate_image' in names
    assert 'summarize_text' in names
    summary_tool = next(tool for tool in tools if tool['name'] == 'summarize_text')
    assert summary_tool['category'] == 'text'
    assert 'properties' in summary_tool['input_schema']


def test_workflow_endpoint_resolves_dependency_references(test_client: TestClient):
    response = test_client.post(
        '/jobs',
        json={
            'tasks': [
                {'id': 1, 'tool': 'generate_image', 'parameters': {'prompt': 'sunrise'}},
                {'id': 2, 'tool': 'get_job_status', 'depends_on': [1], 'parameters': {'job_id': '$tasks.1.job_id'}},
            ]
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload['status'] == 'completed'
    assert payload['tasks'][1]['output']['status'] == 'processing'


def test_websocket_receives_job_updates(test_client: TestClient):
    accepted = test_client.post('/tools/generate_image/invoke', json={'prompt': 'aurora'}).json()
    with test_client.websocket_connect(f"/ws/jobs/{accepted['job_id']}") as websocket:
        initial = websocket.receive_json()
        assert initial['job_id'] == accepted['job_id']
        test_client.post('/tools/get_job_status/invoke', json={'job_id': accepted['job_id']})
        websocket.send_text('poll')
        update = websocket.receive_json()
        assert update['status'] in {'processing', 'completed'}
