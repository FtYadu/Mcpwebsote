from app.resources.account_resource import get_account_resource
from app.resources.limits_resource import get_limits_resource
from app.resources.models_resource import get_models_resource
from app.resources.tools_resource import get_tools_resource
from app.services.provider_router import ProviderRouter


def test_resources_return_structured_payloads(mock_settings):
    provider = ProviderRouter(mock_settings).provider

    models = get_models_resource(provider)
    tools = get_tools_resource(provider)
    limits = get_limits_resource()
    account = get_account_resource(provider)

    assert 'models' in models
    assert 'tools' in tools
    assert 'limits' in limits and 'text' in limits
    assert account['provider'] == 'mock'
