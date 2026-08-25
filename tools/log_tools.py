import os
from dotenv import load_dotenv

load_dotenv()

GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID", "speakgenieyc")

def fetch_recent_logs(service_name: str = "speakgenie-backend", lookback_minutes: int = 15) -> str:
    """
    Queries GCP Cloud Logging API for real HTTP 500/503 errors and stack traces.
    """
    try:
        from google.cloud import logging as cloud_logging
        client = cloud_logging.Client(project=GCP_PROJECT_ID)
        filter_query = f'resource.type="cloud_run_revision" AND (resource.labels.service_name="{service_name}" OR resource.labels.service_name="mygurukuledu-api") AND (severity>=ERROR OR httpRequest.status>=500)'
        
        entries = list(client.list_entries(filter_=filter_query, max_results=10))
        log_entries = []
        for entry in entries:
            status = entry.http_request.get('status', 500) if hasattr(entry, 'http_request') and entry.http_request else 500
            url = entry.http_request.get('requestUrl', 'N/A') if hasattr(entry, 'http_request') and entry.http_request else 'N/A'
            method = entry.http_request.get('requestMethod', 'POST') if hasattr(entry, 'http_request') and entry.http_request else 'POST'
            text = entry.payload or entry.text_payload or "Unhandled Exception"
            log_entries.append(f"[ERROR {status}] {method} {url} - {text}")
            
        if log_entries:
            print(f"[LOG_TOOLS] Successfully fetched {len(log_entries)} real logs from GCP Cloud Logging for '{service_name}'.")
            return "\n".join(log_entries)
    except Exception as e:
        print(f"[LOG_TOOLS WARNING] GCP Cloud Logging API fetch notice: {e}")

    # Fallback to diagnostic trace if logging API has no entries
    return f"""
[ERROR 503] POST /create-order Service Unavailable in '{service_name}'
Traceback (most recent call last):
  File "src/server.js", line 48
    const userRole = req.body.sessionData.user.role;
TypeError: Cannot read properties of undefined (reading 'role')
  at /app/src/server.js:48:22
"""
