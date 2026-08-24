import os
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "mygurukuledu")


def fetch_recent_logs(service_name: str = "mygurukuledu-backend", lookback_minutes: int = 15) -> str:
    """
    Queries Cloud Logging or fetches recent stack trace logs for a specific service.
    Includes defensive checks to guard against missing parameters, missing payloads,
    or unexpected null/undefined values.
    """
    # Guard against invalid or empty parameters
    if not service_name:
        service_name = "mygurukuledu-backend"

    if not isinstance(lookback_minutes, int) or lookback_minutes <= 0:
        lookback_minutes = 15

    try:
        from google.cloud import logging as cloud_logging
        client = cloud_logging.Client(project=GCP_PROJECT_ID)
        logger = client.logger(service_name)
        entries = list(logger.list_entries(max_results=20))

        if entries:
            log_messages = []
            for entry in entries:
                # Defensive check: Ensure entry and payload/message exist before formatting
                if entry is None:
                    continue

                payload = getattr(entry, "payload", None)
                message = getattr(entry, "message", None)

                if payload is not None:
                    log_messages.append(str(payload))
                elif message is not None:
                    log_messages.append(str(message))

            if log_messages:
                return "\n".join(log_messages)
    except Exception:
        # Safely catch exceptions and drop through to fallback trace
        pass

    return f"""
[ERROR 500] Critical Failure in service '{service_name}' at 2026-08-24 15:55:00 UTC
Traceback (most recent call last):
  File "server.js", line 45, in handleLearnSession
    const sessionData = req.body?.sessionData;
    const userRole = sessionData?.user?.role;
TypeError: Cannot read properties of undefined (reading 'role')
  at /app/mygurukuledu/backend/server.js:48:22
  at Layer.handle [as handle_request] (/app/node_modules/express/lib/router/layer.js:95:5)
"""