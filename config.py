import os
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

TENANT_ID     = os.environ["TENANT_ID"]
CLIENT_ID     = os.environ["CLIENT_ID"]
CLIENT_SECRET = os.environ["CLIENT_SECRET"]

FLASK_SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "change-this-in-env")

AUTHORITY = f"https://login.microsoftonline.com/{TENANT_ID}"

ENVIRONMENTS = {
    "DHF":        os.environ.get("DHF_URL",        "").rstrip("/"),
    "CONFINANCE": os.environ.get("CONFINANCE_URL", "").rstrip("/"),
}

def scope_for(url: str) -> str:
    return f"{url}/user_impersonation"

def server_for(url: str) -> str:
    return urlparse(url).hostname

def database_for(url: str) -> str:
    return urlparse(url).hostname.split(".")[0]

LOGIN_SCOPES = [scope_for(next(iter(ENVIRONMENTS.values())))]