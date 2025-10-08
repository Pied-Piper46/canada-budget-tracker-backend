from plaid.model.item_get_request import ItemGetRequest
from fastapi import HTTPException
from ..api.plaid.client import get_plaid_client
import logging

logger = logging.getLogger(__name__)

class PlaidError(HTTPException):
    def __init__(self, status_code: int, error_code: str, message: str):
        detail = {
            "error_code": error_code,
            "message": message
        }
        super().__init__(status_code=status_code, detail=detail)

def check_item_status(access_token: str) -> bool:

    client = get_plaid_client()
    request = ItemGetRequest(access_token=access_token)

    try:
        response = client.item_get(request)
        item_error = response["item"].get("error")
        if item_error and item_error.get("error_code") == "ITEM_LOGIN_REQUIRED":
            logger.warning(f"Item requires login: {access_token[:10]}...")
            raise PlaidError(
                status_code=400,
                error_code="ITEM_LOGIN_REQUIRED",
                message="Need to re-authenticate."
            )
        logger.info(f"Item status valid: {access_token[:10]}...")
        return True
    except PlaidError:
        raise
    except Exception as e:
        logger.error(f"Failed to check item status: {str(e)}")
        raise PlaidError(
            status_code=500,
            error_code="ITEM_STATUS_CHECK_FAILED",
            message=f"Failed to check item status: {str(e)}"
        )