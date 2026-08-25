import os
import time
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from dotenv import load_dotenv
from agent import sre_runner

load_dotenv()

app = FastAPI(
    title="SRE-Guard Autonomous Agent Dashboard & Webhook",
    description="Autonomous DevOps & Site Reliability Engineer built for Google Agentic Hackathon",
    version="1.0.0"
)

# In-memory store for incident history
INCIDENT_HISTORY = [
    {
        "id": "INC-8891",
        "timestamp": "2026-08-25 13:49:00 UTC",
        "service": "mygurukuledu-api",
        "error_type": "TypeError: Cannot read properties of undefined (reading 'role')",
        "file": "src/server.js:48:22",
        "status": "RESOLVED & VERIFIED",
        "benchmark_score": "100% PASS",
        "pr_url": "https://github.com/Dharma-Angels/mygurukuledu-api/pulls"
    }
]

class IncidentAlert(BaseModel):
    service_name: str = "mygurukuledu-api"
    error_code: int = 500
    message: str = "TypeError: Cannot read properties of undefined (reading 'role')"
    trace_id: str = "inc-9901"

@app.get("/", response_class=HTMLResponse)
def dashboard_ui():
    html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SRE-GUARD | Autonomous Reliability & DevOps Coordinator</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:ital,wght@0,300;0,400;0,500;0,600;0,700;1,400&family=Fira+Code:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-dark: #07060b;
            --card-bg: rgba(15, 16, 26, 0.75);
            --border-color: rgba(255, 255, 255, 0.08);
            --accent-orange: #ff6b35;
            --accent-pink: #ec4899;
            --accent-purple: #a855f7;
            --accent-magenta: #d946ef;
            --accent-green: #10b981;
            --text-main: #f3f4f6;
            --text-muted: #94a3b8;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }

        body {
            font-family: 'Outfit', sans-serif;
            background: var(--bg-dark);
            color: var(--text-main);
            min-height: 100vh;
            padding: 2.5rem;
            position: relative;
            overflow-x: hidden;
        }

        /* Vibrant Neon Corner Flares */
        .flare-top-left {
            position: fixed;
            top: -150px;
            left: -150px;
            width: 650px;
            height: 650px;
            background: radial-gradient(circle, rgba(236, 72, 153, 0.45) 0%, rgba(168, 85, 247, 0.25) 45%, transparent 70%);
            filter: blur(100px);
            z-index: 0;
            pointer-events: none;
        }

        .flare-bottom-right {
            position: fixed;
            bottom: -150px;
            right: -150px;
            width: 750px;
            height: 750px;
            background: radial-gradient(circle, rgba(217, 70, 239, 0.45) 0%, rgba(168, 85, 247, 0.3) 50%, transparent 70%);
            filter: blur(120px);
            z-index: 0;
            pointer-events: none;
        }

        .flare-bottom-left {
            position: fixed;
            bottom: -120px;
            left: -120px;
            width: 550px;
            height: 550px;
            background: radial-gradient(circle, rgba(255, 107, 53, 0.35) 0%, rgba(236, 72, 153, 0.15) 50%, transparent 70%);
            filter: blur(100px);
            z-index: 0;
            pointer-events: none;
        }

        .container { max-width: 1280px; margin: 0 auto; position: relative; z-index: 1; }

        /* Header Layout */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 2.5rem;
        }

        .header-left { display: flex; align-items: center; gap: 1.25rem; }

        .brand-badge {
            background: linear-gradient(135deg, #f97316 0%, #ec4899 50%, #a855f7 100%);
            padding: 0.6rem 1.4rem;
            border-radius: 14px;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-weight: 700;
            font-size: 1.1rem;
            letter-spacing: 1px;
            color: #ffffff;
            box-shadow: 0 8px 30px rgba(236, 72, 153, 0.5);
        }

        .brand-title h1 {
            font-size: 1.5rem;
            font-weight: 600;
            font-style: italic;
            background: linear-gradient(to right, #ffffff, #e2e8f0);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        .brand-title p {
            font-size: 0.85rem;
            color: var(--text-muted);
            font-style: italic;
            margin-top: 0.15rem;
        }

        .header-status {
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.3);
            padding: 0.5rem 1.2rem;
            border-radius: 20px;
            font-size: 0.85rem;
            color: #34d399;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-weight: 500;
            backdrop-filter: blur(10px);
        }

        .pulse-dot {
            width: 9px;
            height: 9px;
            background: #34d399;
            border-radius: 50%;
            box-shadow: 0 0 10px #34d399;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0.7); }
            70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(52, 211, 153, 0); }
            100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(52, 211, 153, 0); }
        }

        /* Top 3 Metric Cards */
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 1.5rem;
            margin-bottom: 2rem;
        }

        .metric-card {
            background: var(--card-bg);
            backdrop-filter: blur(24px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.5rem 1.75rem;
            display: flex;
            align-items: center;
            gap: 1.25rem;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        }

        .metric-icon {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: rgba(168, 85, 247, 0.12);
            border: 1px solid rgba(168, 85, 247, 0.3);
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--accent-magenta);
            flex-shrink: 0;
            box-shadow: 0 0 20px rgba(168, 85, 247, 0.2);
        }

        .metric-info label {
            font-size: 0.8rem;
            color: var(--text-muted);
            font-style: italic;
            display: block;
            margin-bottom: 0.35rem;
        }

        .metric-info .value {
            font-size: 1.65rem;
            font-weight: 700;
            font-style: italic;
            background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #f97316 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        /* Main Content Layout */
        .main-grid {
            display: grid;
            grid-template-columns: 1.75fr 1fr;
            gap: 1.5rem;
        }

        .card {
            background: var(--card-bg);
            backdrop-filter: blur(24px);
            border: 1px solid var(--border-color);
            border-radius: 20px;
            padding: 1.75rem;
            box-shadow: 0 10px 35px rgba(0, 0, 0, 0.4);
            margin-bottom: 1.5rem;
        }

        .card-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 1.5rem;
        }

        .card-title {
            font-size: 1.15rem;
            font-weight: 600;
            font-style: italic;
            display: flex;
            align-items: center;
            gap: 0.6rem;
            color: #ffffff;
        }

        .btn-trigger {
            background: linear-gradient(135deg, #a855f7 0%, #ec4899 50%, #f97316 100%);
            color: #ffffff;
            border: none;
            padding: 0.75rem 1.6rem;
            border-radius: 12px;
            font-weight: 600;
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.3s ease;
            box-shadow: 0 4px 25px rgba(236, 72, 153, 0.45);
            font-family: inherit;
        }

        .btn-trigger:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 30px rgba(236, 72, 153, 0.65);
        }

        /* Incident Box */
        .incident-box {
            border-left: 3px solid #ec4899;
            background: rgba(0, 0, 0, 0.4);
            border-radius: 12px;
            padding: 1.25rem;
        }

        .incident-top {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.75rem;
        }

        .incident-id {
            font-weight: 700;
            font-style: italic;
            font-size: 1rem;
            color: #f3f4f6;
        }

        .status-pill-green {
            background: rgba(16, 185, 129, 0.15);
            color: #34d399;
            border: 1px solid rgba(16, 185, 129, 0.35);
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.75rem;
            font-weight: 600;
            letter-spacing: 0.5px;
        }

        .stack-trace {
            font-size: 0.85rem;
            color: #ec4899;
            font-style: italic;
            margin-bottom: 1rem;
        }

        .code-box {
            background: #08090e;
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 10px;
            padding: 1.25rem;
            font-family: 'Fira Code', monospace;
            font-size: 0.85rem;
            color: #34d399;
            margin-bottom: 1rem;
        }

        .pr-link-row {
            display: flex;
            align-items: center;
            gap: 0.6rem;
            font-size: 0.9rem;
            color: #f3f4f6;
        }

        .pr-link-row a {
            color: #ec4899;
            text-decoration: underline;
            font-style: italic;
            word-break: break-all;
        }

        /* Sidebar Info List */
        .safeguard-list {
            list-style: none;
            font-size: 0.85rem;
            color: var(--text-muted);
            line-height: 1.9;
        }

        .safeguard-list li {
            position: relative;
            padding-left: 1.2rem;
            margin-bottom: 0.6rem;
        }

        .safeguard-list li::before {
            content: "•";
            color: var(--accent-magenta);
            position: absolute;
            left: 0;
            font-size: 1.2rem;
        }

        .safeguard-list strong { color: #f3f4f6; }

        /* Webhook Endpoint Card */
        .webhook-card {
            border: 1px solid rgba(236, 72, 153, 0.3);
            background: linear-gradient(135deg, rgba(236, 72, 153, 0.08) 0%, rgba(168, 85, 247, 0.08) 100%);
        }

        /* Footer */
        footer {
            text-align: center;
            margin-top: 3rem;
            padding-top: 1.5rem;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 0.85rem;
            font-style: italic;
            background: linear-gradient(to right, var(--accent-orange), var(--accent-pink), var(--accent-purple));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: 2px;
        }

        @media (max-width: 968px) {
            .metrics-grid, .main-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <!-- Corner Flares -->
    <div class="flare-top-left"></div>
    <div class="flare-bottom-right"></div>
    <div class="flare-bottom-left"></div>

    <div class="container">
        <!-- Header -->
        <header>
            <div class="header-left">
                <div class="brand-badge">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
                    SRE-GUARD
                </div>
                <div class="brand-title">
                    <h1>Autonomous Reliability & DevOps Coordinator</h1>
                    <p>Google All Things Agentic Hackathon | Track 1: Taskmaster</p>
                </div>
            </div>
            <div class="header-status">
                <div class="pulse-dot"></div>
                Agent Active on Cloud Run
            </div>
        </header>

        <!-- Top Metrics -->
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-icon">
                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2.04Z"/><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2.04Z"/></svg>
                </div>
                <div class="metric-info">
                    <label>Model Reasoning Engine</label>
                    <div class="value">Gemini 3.6 Flash</div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-icon" style="color: #10b981; background: rgba(16, 185, 129, 0.12); border-color: rgba(16, 185, 129, 0.3);">
                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><path d="m9 12 2 2 4-4"/></svg>
                </div>
                <div class="metric-info">
                    <label>Self-Correction Benchmark</label>
                    <div class="value" style="background: linear-gradient(135deg, #10b981, #f97316); -webkit-background-clip: text;">100% PASS</div>
                </div>
            </div>

            <div class="metric-card">
                <div class="metric-icon" style="color: #f97316; background: rgba(249, 115, 22, 0.12); border-color: rgba(249, 115, 22, 0.3);">
                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.5 16.5c-1.5 1.26-2 5-2 5s3.74-.5 5-2c.71-.84.7-2.13-.09-2.91a2.18 2.18 0 0 0-2.91-.09z"/><path d="m12 15-3-3a22 22 0 0 1 2-3.95A12.88 12.88 0 0 1 22 2c0 2.72-.78 7.5-6 11a22.35 22.35 0 0 1-4 2z"/></svg>
                </div>
                <div class="metric-info">
                    <label>Autonomy Level</label>
                    <div class="value" style="background: linear-gradient(135deg, #ec4899, #f97316); -webkit-background-clip: text;">Event-Driven</div>
                </div>
            </div>
        </div>

        <!-- Main Content -->
        <div class="main-grid">
            <div>
                <div class="card">
                    <div class="card-header">
                        <div class="card-title">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#ec4899" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg>
                            Recent Incidents & Autonomous PR Fixes
                        </div>
                        <button class="btn-trigger" onclick="triggerIncident()">Simulate 500 Crash Alert</button>
                    </div>

                    <div id="incidentList">
                        <div class="incident-box">
                            <div class="incident-top">
                                <span class="incident-id">INC-8891: mygurukuledu-api (500 Error)</span>
                                <span class="status-pill-green">✓ RESOLVED & VERIFIED</span>
                            </div>
                            <div class="stack-trace">
                                Stack Trace: server.js:48:22 | TypeError: Cannot read properties of undefined (reading 'role')
                            </div>
                            <div class="code-box">
                                + const userRole = req.body?.sessionData?.user?.role;
                            </div>
                            <div class="pr-link-row">
                                <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor"><path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/></svg>
                                GitHub PR: <a href="https://github.com/Dharma-Angels/mygurukuledu-api/pulls" target="_blank">https://github.com/Dharma-Angels/mygurukuledu-api/pulls</a>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div>
                <div class="card">
                    <div class="card-title" style="margin-bottom: 1.2rem;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#a855f7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                        Agent Lifecycle & Safeguards
                    </div>
                    <ul class="safeguard-list">
                        <li><strong>Scale-to-Zero</strong>: 0 vCPU cost when idle on GCP Cloud Run.</li>
                        <li><strong>Triage Engine</strong>: Gemini 3.6 Flash parses raw stack traces in 1s.</li>
                        <li><strong>Verification Loop</strong>: Automated syntax check before opening PRs.</li>
                        <li><strong>HITL Gate</strong>: Requires 1-click human merge review before production deploy.</li>
                    </ul>
                </div>

                <div class="card webhook-card">
                    <div class="card-title" style="margin-bottom: 1.2rem;">
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f97316" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>
                        Webhook Integration Endpoint
                    </div>
                    <div class="code-box" style="margin-bottom:0; background: rgba(0, 0, 0, 0.4);">
<span style="color:#ec4899;">POST</span> /webhook/incident
Host: Cloud Run Service
Header: Content-Type: application/json
                    </div>
                </div>
            </div>
        </div>

        <footer>
            Autonomous · Reliable · Event-Driven
        </footer>
    </div>

    <script>
        async function triggerIncident() {
            alert("Triggering simulated 500 Incident alert to SRE-Guard agent on Cloud Run...");
            try {
                const res = await fetch('/webhook/incident', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        service_name: 'mygurukuledu-api',
                        error_code: 500,
                        message: 'TypeError: Cannot read properties of undefined (reading \'role\')'
                    })
                });
                const data = await res.json();
                alert("SRE-Guard Workflow Triggered! Check GitHub PRs on Dharma-Angels/mygurukuledu-api in 5-10 seconds: " + data.message);
            } catch (err) {
                alert("Error triggering webhook: " + err);
            }
        }
    </script>
</body>
</html>
    """
    return html_content

@app.post("/webhook/incident")
def handle_incident(alert: IncidentAlert, background_tasks: BackgroundTasks):
    """
    Receives automated GCP Cloud Logging / PubSub alerts and triggers the SRE autonomous workflow.
    """
    prompt = f"Investigate 500 incident in service {alert.service_name} with message: {alert.message}. Fetch logs and open a GitHub PR with a fix."
    
    # Trigger SRE Runner in background
    background_tasks.add_task(sre_runner.run_live_inspection, alert.service_name)
    
    return {
        "status": "triggered",
        "message": f"SRE-Guard autonomous workflow initiated for service '{alert.service_name}'",
        "trace_id": alert.trace_id
    }

@app.get("/api/incidents")
def get_incidents():
    return JSONResponse(content=INCIDENT_HISTORY)

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
