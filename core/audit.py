import json
import logging
import os
import time
from datetime import date

from flask import g, request, session

logger = logging.getLogger("cartera")
logger.setLevel(logging.INFO)
SKIPPED_PREFIXES = ("/static",)
NO_SESSION = "sin sesion"
FILE_FORMAT = "%(asctime)s %(message)s"


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


class MonthlyFileHandler(logging.Handler):
    def __init__(self, directory):
        super().__init__()
        self.directory = directory

    def path(self, today=None):
        name = "cartera-" + (today or date.today()).strftime("%Y-%m") + ".log"
        return os.path.join(self.directory, name)

    def emit(self, record):
        try:
            os.makedirs(self.directory, exist_ok=True)
            with open(self.path(), "a", encoding="utf-8") as handle:
                handle.write(self.format(record) + "\n")
        except Exception:
            self.handleError(record)


def setup_file_logging(directory):
    if not directory:
        return None
    if any(isinstance(h, MonthlyFileHandler) for h in logger.handlers):
        return None
    handler = MonthlyFileHandler(directory)
    handler.setFormatter(logging.Formatter(FILE_FORMAT))
    logger.addHandler(handler)
    return handler
