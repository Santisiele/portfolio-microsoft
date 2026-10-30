import json
import logging
import time

from flask import g, request, session

logger = logging.getLogger("cartera")
SKIPPED_PREFIXES = ("/static",)
NO_SESSION = "sin sesion"


def start_request():
    g.started_at = time.perf_counter()
    g.audit = {}


def record(**fields):
    g.audit = {**getattr(g, "audit", {}), **fields}


def count_by(rows, column):
    counts = {}
    for row in rows:
        key = str(row.get(column) or "sin dato")
        counts[key] = counts.get(key, 0) + 1
    return counts


def _user():
    claims = session.get("user") or {}
    return claims.get("preferred_username") or claims.get("name") or NO_SESSION


def log_request(response):
    if request.path.startswith(SKIPPED_PREFIXES):
        return response
    entry = {
        "usuario": _user(),
        "ruta": request.path,
        "estado": response.status_code,
        "ms": round((time.perf_counter() - getattr(g, "started_at", time.perf_counter())) * 1000),
    }
    entry.update(getattr(g, "audit", {}))
    logger.info(json.dumps(entry, ensure_ascii=False))
    return response
