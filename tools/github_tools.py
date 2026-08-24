import os
import base64
import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def get_github_headers():
    return {
        "Authorization": f"Bearer {GITHUB_TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

def fetch_file_content(repo_owner: str, repo_name: str, file_path: str, branch: str = "main") -> str:
    """
    Fetches the raw content of a specific file from a GitHub repository.
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={branch}"
    response = requests.get(url, headers=get_github_headers())
    
    if response.status_code == 200:
        data = response.json()
        content = base64.b64decode(data["content"]).decode("utf-8")
        return content
    else:
        return f"Error fetching file: {response.status_code} - {response.text}"

def create_github_pr(repo_owner: str, repo_name: str, file_path: str, proposed_code: str, pr_title: str, pr_body: str, base_branch: str = "main") -> str:
    """
    Creates a new git branch, updates a file with proposed_code, and opens a Pull Request on GitHub.
    """
    headers = get_github_headers()
    
    # 1. Get base branch SHA
    ref_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/ref/heads/{base_branch}"
    ref_res = requests.get(ref_url, headers=headers)
    if ref_res.status_code != 200:
        return f"Failed to get base branch reference: {ref_res.text}"
    
    base_sha = ref_res.json()["object"]["sha"]
    
    # 2. Create a new branch
    import time
    new_branch = f"sre-guard-fix-{int(time.time())}"
    create_ref_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs"
    create_ref_res = requests.post(create_ref_url, headers=headers, json={
        "ref": f"refs/heads/{new_branch}",
        "sha": base_sha
    })
    
    if create_ref_res.status_code not in (200, 201):
        return f"Failed to create new branch {new_branch}: {create_ref_res.text}"
    
    # 3. Get existing file SHA (if it exists)
    file_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/contents/{file_path}?ref={new_branch}"
    file_res = requests.get(file_url, headers=headers)
    file_sha = file_res.json().get("sha") if file_res.status_code == 200 else None
    
    # 4. Commit updated file to new branch
    encoded_content = base64.b64encode(proposed_code.encode("utf-8")).decode("utf-8")
    commit_payload = {
        "message": f"fix(sre-guard): {pr_title}",
        "content": encoded_content,
        "branch": new_branch
    }
    if file_sha:
        commit_payload["sha"] = file_sha
        
    put_res = requests.put(file_url, headers=headers, json=commit_payload)
    if put_res.status_code not in (200, 201):
        return f"Failed to commit file fix: {put_res.text}"
    
    # 5. Open Pull Request
    pr_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    pr_res = requests.post(pr_url, headers=headers, json={
        "title": f"[SRE-Guard Autonomous Fix] {pr_title}",
        "body": pr_body,
        "head": new_branch,
        "base": base_branch
    })
    
    if pr_res.status_code in (200, 201):
        pr_data = pr_res.json()
        return f"SUCCESS: Pull Request #{pr_data.get('number')} created successfully: {pr_data.get('html_url')}"
    else:
        return f"Failed to create Pull Request: {pr_res.text}"
