import os
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import sre_workflow

load_dotenv()

app = FastAPI(
    title="SRE-Guard Autonomous Agent Service",
    description="Autonomous DevOps & Site Reliability Engineer built for Google Agentic Hackathon",
    version="1.0.0"
)

class IncidentAlert(BaseModel):
    service_name: str
    error_code: int = 500
    message: str = "Internal Server Error"
    trace_id: str = "inc-9901"

@app.get("/")
def read_root():
    return {
        "status": "online",
        "service": "SRE-Guard Autonomous Agent",
        "model": "Gemini 2.5 Flash / Gemini 2.5 Pro",
        "hackathon": "Google All Things Agentic Hackathon"
    }

@app.post("/webhook/incident")
def handle_incident(alert: IncidentAlert, background_tasks: BackgroundTasks):
    """
    Receives automated GCP Cloud Logging / PubSub alerts and triggers the SRE autonomous workflow.
    """
    prompt = f"Investigate 500 incident in service {alert.service_name} with message: {alert.message}. Fetch logs and open a GitHub PR with a fix."
    
    # Run in background to respond immediately to webhook
    background_tasks.add_task(sre_workflow.run, prompt)
    
    return {
        "status": "triggered",
        "message": f"SRE-Guard workflow initiated for service {alert.service_name}",
        "trace_id": alert.trace_id
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
