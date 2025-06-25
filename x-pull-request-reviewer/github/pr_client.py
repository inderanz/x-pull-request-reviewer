import os
import requests

GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN')
GITHUB_API_URL = os.environ.get('GITHUB_API_URL', 'https://api.github.com')


def post_pr_comment(repo, pr_number, body):
    """Post a general comment to a GitHub pull request."""
    if not GITHUB_TOKEN:
        return "[ERROR] GITHUB_TOKEN not set. Cannot post PR comment."
    url = f"{GITHUB_API_URL}/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
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
    if not GITHUB_TOKEN:
        return "[ERROR] GITHUB_TOKEN not set. Cannot post line comment."
    url = f"{GITHUB_API_URL}/repos/{repo}/pulls/{pr_number}/comments"
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
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