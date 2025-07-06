import os
import requests
import getpass

GITHUB_API_URL = os.environ.get('GITHUB_API_URL', 'https://api.github.com')

def get_github_token():
    token = os.environ.get('GITHUB_TOKEN')
    if not token:
        print('[INFO] GITHUB_TOKEN not set. Please enter your GitHub token (input hidden):')
        token = getpass.getpass('GitHub Token: ')
        os.environ['GITHUB_TOKEN'] = token
    return token

def get_pr_metadata(repo, pr_number):
    """Fetch PR metadata (base and head branch names) from GitHub."""
    token = get_github_token()
    if not token:
        return None
    url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    try:
        resp = requests.get(url, headers=headers, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        return {
            'base_branch': data['base']['ref'],
            'head_branch': data['head']['ref'],
            'head_repo_clone_url': data['head']['repo']['clone_url'],
            'base_repo_clone_url': data['base']['repo']['clone_url'],
        }
    except Exception as e:
        print(f"[ERROR] Failed to fetch PR metadata: {e}")
        return None

def post_pr_comment(repo, pr_number, body):
    """Post a general comment to a GitHub pull request."""
    token = get_github_token()
    if not token:
        return "[ERROR] GITHUB_TOKEN not set. Cannot post PR comment."
    url = f"{GITHUB_API_URL}/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    payload = {"body": body}
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return f"[INFO] Comment posted to PR #{pr_number}."
    except Exception as e:
        return f"[ERROR] Failed to post PR comment: {e}"

def post_line_comment(repo, pr_number, body, commit_id, path, line):
    """Post a line-specific review comment to a GitHub pull request."""
    token = get_github_token()
    if not token:
        return "[ERROR] GITHUB_TOKEN not set. Cannot post line comment."
    url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}/comments"
    headers = {
        'Authorization': f'token {token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    payload = {
        "body": body,
        "commit_id": commit_id,
        "path": path,
        "line": line,
        "side": "RIGHT"
    }
    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        resp.raise_for_status()
        return f"[INFO] Line comment posted to {path} line {line} in PR #{pr_number}."
    except Exception as e:
        return f"[ERROR] Failed to post line comment: {e}" 