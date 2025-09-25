from plaid.api import plaid_api
from plaid import Configuration, ApiClient, Environment
from ...config.settings import settings

def get_plaid_client() -> plaid_api.PlaidApi:
    config = Configuration(
        host=(
        Environment.Sandbox if settings.PLAID_ENV == "sandbox" else
        Environment.Development if settings.PLAID_ENV == "development" else
        Environment.Production if settings.PLAID_ENV == "production" else
        Environment.Sandbox
    ),
        api_key={
            "clientId": settings.PLAID_CLIENT_ID,
            "secret": settings.PLAID_SECRET,
        }
    )
    api_client = ApiClient(configuration=config)
    client = plaid_api.PlaidApi(api_client)

    return (client)