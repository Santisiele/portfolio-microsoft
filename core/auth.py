import msal
from flask import session

from config import CLIENT_ID, CLIENT_SECRET, AUTHORITY, LOGIN_SCOPES


def _load_cache() -> msal.SerializableTokenCache:
    cache = msal.SerializableTokenCache()
    if session.get("token_cache"):
        cache.deserialize(session["token_cache"])
    return cache


def _save_cache(cache: msal.SerializableTokenCache):
    if cache.has_state_changed:
        session["token_cache"] = cache.serialize()


def _msal_app(cache=None) -> msal.ConfidentialClientApplication:
    return msal.ConfidentialClientApplication(
        CLIENT_ID, authority=AUTHORITY,
        client_credential=CLIENT_SECRET, token_cache=cache,
    )


def build_auth_flow(redirect_uri: str) -> dict:
    return _msal_app().initiate_auth_code_flow(LOGIN_SCOPES, redirect_uri=redirect_uri)


def complete_auth_flow(flow: dict, request_args) -> dict:
    cache = _load_cache()
    result = _msal_app(cache).acquire_token_by_auth_code_flow(flow, dict(request_args))
    _save_cache(cache)
    return result


def get_access_token(scope: str) -> str | None:
    cache = _load_cache()
    app = _msal_app(cache)
    accounts = app.get_accounts()
    if not accounts:
        return None
    result = app.acquire_token_silent([scope], account=accounts[0])
    _save_cache(cache)
    if result and "access_token" in result:
        return result["access_token"]
    return None