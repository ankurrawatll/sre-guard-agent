import os
from dotenv import load_dotenv
from tools.log_tools import fetch_recent_logs
from tools.github_tools import fetch_file_content, create_github_pr

load_dotenv()

# Ensure Gemini API key is configured
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing in .env file.")

os.environ["GEMINI_API_KEY"] = GEMINI_API_KEY

try:
    from google.adk import Agent, Workflow
    
    # 1. Triage Agent (Gemini 2.5 Flash for fast log parsing & file isolation)
    triage_agent = Agent(
        name="triage_agent",
        model="gemini-2.5-flash",
        instruction=(
            "You are an expert SRE Triage Specialist. Analyze the provided error log or query Cloud Logging. "
            "Isolate the faulty file path, exact line number, and error type. Summarize your findings clearly."
        ),
        tools=[fetch_recent_logs, fetch_file_content]
    )

    # 2. Fix Agent (Gemini 2.5 Pro for deep code synthesis & PR generation)
    fix_agent = Agent(
        name="fix_agent",
        model="gemini-2.5-pro",
        instruction=(
            "You are an expert DevOps Software Engineer. Based on the triage report, write clean, robust code "
            "that fixes the bug handling null/undefined checks or edge cases. "
            "Use the create_github_pr tool to push a fix branch and open a Pull Request."
        ),
        tools=[fetch_file_content, create_github_pr]
    )

    # 3. Autonomous Workflow
    sre_workflow = Workflow(
        name="sre_workflow",
        edges=[("START", triage_agent, fix_agent)]
    )

except Exception as adk_err:
    # Direct fallback using google-genai SDK if ADK package is loading
    import google.genai as genai
    
    print(f"Note: Running via direct Gemini SDK: {adk_err}")
    
    class SREAgentFallback:
        def __init__(self):
            self.client = genai.Client(api_key=GEMINI_API_KEY)
            
        def run(self, prompt: str):
            logs = fetch_recent_logs()
            
            # Step 1: Triage
            triage_prompt = f"Analyze these application logs and identify the faulty file and line:\n{logs}"
            triage_res = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=triage_prompt
            )
            triage_summary = triage_res.text
            
            # Step 2: Fix & PR
            fix_prompt = f"""
Based on this triage analysis:
{triage_summary}

Write the corrected code fix and describe what changes were made.
"""
            fix_res = self.client.models.generate_content(
                model="gemini-2.5-pro",
                contents=fix_prompt
            )
            
            return {
                "triage": triage_summary,
                "fix": fix_res.text,
                "logs": logs
            }
            
    sre_workflow = SREAgentFallback()

if __name__ == "__main__":
    print("--- 🚀 Starting SRE-Guard Autonomous Agent Run ---")
    result = sre_workflow.run("Investigate the 500 error in mygurukuledu backend service and open a GitHub PR with a fix.")
    print("\n--- ✅ SRE-Guard Result ---")
    print(result)
