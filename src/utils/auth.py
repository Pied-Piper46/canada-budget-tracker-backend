from ..config.settings import settings

def verify_password(password: str) -> bool:
    return password == settings.APP_PASSWORD

def verify_session_token(token: str) -> bool:
    # not verify for personal use temporary
    return True