from plaid.model.item_get_request import ItemGetRequest
from fastapi import HTTPException
from ..api.plaid.client import get_plaid_client
import logging

logger = logging.getLogger(__name__)

def check_item_status(access_token: str) -> bool:

    client = get_plaid_client()
    request = ItemGetRequest(access_token=access_token)

    try:
        response = client.item_get(request)
        item_error = response["item"].get("error")
        if item_error and item_error.get("error_code") == "ITEM_LOGIN_REQUIRED":
            logger.warning(f"Item requires login: {access_token[:10]}...")
            raise HTTPException(status_code=400, detail="Item login required. Please re-authenticate via Plaid Link update mode.")
        logger.info(f"Item status valid: {access_token[:10]}...")
        return True
    except Exception as e:
        if hasattr(e, 'error_code') and e.error_code == 'ITEM_LOGIN_REQUIRED':
            logger.warning(f"Item requires login: {access_token[:10]}...")
            raise HTTPException(status_code=400, detail="Item login required. Please re-authenticate via Plaid Link update mode.")
        logger.error(f"Failed to check item status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to check item status: {str(e)}")