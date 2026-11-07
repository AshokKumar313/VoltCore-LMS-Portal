"""
========================================================================================
VoltCore Apex Academia - Structured JSON Logger & Safe Error Response Formatter
Anna University / MIT Campus Standards (Department of Electronics Engineering)
----------------------------------------------------------------------------------------
Module: backend/structured_logger.py
Platform Lead / Systems Architect: Ashok Kumar A (2023MITEC042)
Institution: Madras Institute of Technology (MIT) Campus, Anna University, Chromepet

Purpose:
  1. Structured JSON Logging:
     - ISO 8601 UTC timestamps, log level, message, correlation_id, client_id.
     - Latency tracking in milliseconds.
     - Automatic recursive redaction of sensitive credentials and private fields.
  2. Safe Error Messaging:
     - Intercepts uncaught exceptions and internal errors.
     - Produces sanitized, consistent client error responses with unique incident IDs.
     - Prevents leakage of internal stack traces, DB connection strings, and local file paths.
  3. Passive Resource Consumption:
     - Zero background workers, lightweight string serialization.
========================================================================================
"""

import os
import sys
import json
import uuid
import time
import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Union


REDACTED_KEYS = {
    "password", "passwd", "secret", "token", "jwt", "key", "api_key",
    "authorization", "auth", "cookie", "set-cookie", "private_key",
    "access_token", "refresh_token", "session_id", "pin"
}


def sanitize_payload(obj: Any) -> Any:
    """
    Recursively scans and redacts sensitive credentials, tokens, and keys from log structures.
    """
    if isinstance(obj, dict):
        sanitized = {}
        for k, v in obj.items():
            if any(re_k in k.lower() for re_k in REDACTED_KEYS):
                sanitized[k] = "[REDACTED_CREDENTIAL]"
            elif isinstance(v, (dict, list)):
                sanitized[k] = sanitize_payload(v)
            else:
                sanitized[k] = v
        return sanitized
    elif isinstance(obj, list):
        return [sanitize_payload(item) for item in obj]
    return obj


class StructuredLogger:
    """Enterprise JSON structured logger formatted for cloud-native ingestion."""

    def __init__(self, service_name: str = "voltcore_apex_api"):
        self.service_name = service_name

    def _emit(
        self,
        level: str,
        message: str,
        correlation_id: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
        client_id: Optional[str] = None,
        duration_ms: Optional[float] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """Constructs and returns structured log entry dictionary."""
        combined_extra = dict(extra) if extra else {}
        if kwargs:
            combined_extra.update(kwargs)
        entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "service": self.service_name,
            "level": level.upper(),
            "message": message,
            "correlation_id": correlation_id or f"req_{uuid.uuid4().hex[:12]}",
            "client_id": client_id or "ANONYMOUS"
        }
        if duration_ms is not None:
            entry["duration_ms"] = round(duration_ms, 2)
        if combined_extra:
            entry["context"] = sanitize_payload(combined_extra)
        return entry

    def info(self, message: str, **kwargs) -> Dict[str, Any]:
        return self._emit("INFO", message, **kwargs)

    def warn(self, message: str, **kwargs) -> Dict[str, Any]:
        return self._emit("WARN", message, **kwargs)

    def error(self, message: str, **kwargs) -> Dict[str, Any]:
        return self._emit("ERROR", message, **kwargs)

    def security(self, message: str, **kwargs) -> Dict[str, Any]:
        return self._emit("SECURITY", message, **kwargs)


class SafeErrorHandler:
    """
    Generates sanitized error payloads preventing leakage of internal stack traces,
    database schemas, or host filesystem paths.
    """

    SAFE_ERROR_MAP = {
        400: ("INVALID_REQUEST", "The submitted request was malformed or missing required parameters."),
        401: ("UNAUTHORIZED", "Authentication credentials are required to access this resource."),
        403: ("FORBIDDEN", "You do not have permission to perform the requested action."),
        404: ("RESOURCE_NOT_FOUND", "The requested educational module or resource was not found."),
        429: ("RATE_LIMIT_EXCEEDED", "Request quota exceeded. Please wait before submitting further queries."),
        500: ("INTERNAL_SERVER_ERROR", "An internal error occurred while processing the request."),
        503: ("SERVICE_UNAVAILABLE", "The requested background engine is temporarily unavailable.")
    }

    @classmethod
    def format_client_error(
        cls,
        status_code: int = 500,
        custom_message: Optional[str] = None,
        correlation_id: Optional[str] = None,
        internal_exception: Optional[Exception] = None
    ) -> Dict[str, Any]:
        """
        Builds safe JSON response for client.
        Never embeds Python stack trace, internal path, or database details.
        """
        err_code, default_msg = cls.SAFE_ERROR_MAP.get(
            status_code,
            ("GENERIC_ERROR", "An unexpected error occurred.")
        )
        msg = custom_message or default_msg

        # Filter out potential internal path leaks from custom message
        if any(leak in msg.lower() for leak in ["traceback", "c:\\", "/app/", "line ", "syntaxerror", "sqlite3"]):
            msg = default_msg

        cid = correlation_id or f"inc_{uuid.uuid4().hex[:12]}"

        # Log internal detail securely on backend
        if internal_exception:
            structured_logger.error(
                f"Internal exception intercepted: {type(internal_exception).__name__}: {str(internal_exception)}",
                correlation_id=cid,
                extra={"status_code": status_code, "raw_error": str(internal_exception)}
            )

        return {
            "status": "ERROR",
            "error_code": err_code,
            "message": msg,
            "correlation_id": cid,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }


# Global singleton instances
structured_logger = StructuredLogger()
safe_error_handler = SafeErrorHandler()
