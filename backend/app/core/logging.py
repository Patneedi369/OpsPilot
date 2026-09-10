import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any

from app.core.correlation import get_request_id

SENSITIVE_KEYS = {
    "password",
    "hashed_password",
    "secret",
    "secret_key",
    "token",
    "access_token",
    "authorization",
    "jwt",
    "api_key",
}


def sanitize_val(key: str, val: Any) -> Any:
    if any(s in key.lower() for s in SENSITIVE_KEYS):
        return "***REDACTED***"
    if isinstance(val, dict):
        return {k: sanitize_val(k, v) for k, v in val.items()}
    if isinstance(val, list):
        return [sanitize_val(key, item) for item in val]
    return val


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        req_id = get_request_id() or getattr(record, "request_id", None)
        payload: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        if req_id:
            payload["request_id"] = req_id

        reserved = set(logging.LogRecord("", 0, "", 0, "", (), None).__dict__.keys())
        reserved.update({"message", "asctime"})

        for key, value in record.__dict__.items():
            if key not in reserved and key not in payload:
                payload[key] = sanitize_val(key, value)

        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)

        return json.dumps(payload, ensure_ascii=True, default=str)


def configure_logging(level: str) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter())
    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level.upper())
