import requests
import os
import json
import re

OLLAMA_HOST = os.environ.get('LLM_HOST', 'http://localhost')
OLLAMA_PORT = os.environ.get('LLM_PORT', '11434')
OLLAMA_MODEL = os.environ.get('LLM_MODEL', 'codellama')
OLLAMA_URL = f"{OLLAMA_HOST}:{OLLAMA_PORT}/api/generate"

PROMPT_MAX_CHARS = 4000  # Further reduce prompt size

REVIEW_PROMPT_TEMPLATE = '''
You are an expert code reviewer. For the following diff, return actionable review suggestions in this strict format:
- For each issue: LINE:<line_number> COMMENT:<comment>
- For overall summary: SUMMARY:<summary>
Only output lines in this format. Do not add any extra text or explanation.

Example:
LINE:12 COMMENT: Use input validation here.
LINE:45 COMMENT: Avoid hardcoded credentials.
SUMMARY: Overall, the code is well-structured but needs better error handling.

DIFF:
{diff}
'''


def summarize_diff(diff, max_chars=2000):
    """Summarize or chunk the diff if it's too large for the LLM."""
    if len(diff) <= max_chars:
        return diff
    # Simple heuristic: take the first and last N lines
    lines = diff.splitlines()
    n = max_chars // 2 // 80  # Approximate lines for half the max chars
    summary = '\n'.join(lines[:n]) + '\n...\n' + '\n'.join(lines[-n:])
    return summary[:max_chars]


def extract_review_comments(llm_output):
    """Extracts (line, comment) pairs and summary from LLM output in strict format."""
    line_comments = []
    summary = None
    for line in llm_output.splitlines():
        m = re.match(r'LINE:(\d+) COMMENT:(.+)', line)
        if m:
            line_comments.append((int(m.group(1)), m.group(2).strip()))
        elif line.startswith('SUMMARY:'):
            summary = line[len('SUMMARY:'):].strip()
    return line_comments, summary


def fallback_extract_suggestions(llm_output):
    """Extract line comments and summary from plain text LLM output using regex/heuristics."""
    line_comments = []
    summary = None
    
    # Try strict format first
    for l in llm_output.splitlines():
        if l.strip().startswith('LINE:') and 'COMMENT:' in l:
            try:
                parts = l.split('COMMENT:')
                line_part = parts[0].replace('LINE:', '').strip()
                comment = parts[1].strip()
                if ':' in line_part:
                    file_path, line_num = line_part.split(':', 1)
                    file_path = file_path.strip()
                    line_num = int(line_num.strip())
                else:
                    file_path = None
                    line_num = int(line_part.strip())
                # Accept any reasonable line number since agent will map it
                if 1 <= line_num <= 100000:
                    line_comments.append((file_path, line_num, comment))
            except Exception:
                continue
        elif l.strip().startswith('SUMMARY:'):
            summary = l.replace('SUMMARY:', '').strip()
    
    # Try the trained model format: "LINE 5 COMMENT: ..."
    if not line_comments:
        for l in llm_output.splitlines():
            # Match "LINE 5 COMMENT: ..." format
            m = re.match(r'\s*LINE\s+(\d+)\s+COMMENT:\s*(.+)', l, re.IGNORECASE)
            if m:
                line_num = int(m.group(1))
                comment = m.group(2).strip()
                # Accept any reasonable line number since agent will map it
                if 1 <= line_num <= 100000:
                    line_comments.append((None, line_num, comment))
    
    # Fallback: regex for 'line <num>:' or 'Line <num>:'
    if not line_comments:
        for l in llm_output.splitlines():
            m = re.match(r'\s*line\s*(\d+)\s*[:\-]\s*(.+)', l, re.IGNORECASE)
            if m:
                line_num = int(m.group(1))
                comment = m.group(2).strip()
                # Accept any reasonable line number since agent will map it
                if 1 <= line_num <= 100000:
                    line_comments.append((None, line_num, comment))
    
    # Fallback: look for bullet points or numbered lists
    if not line_comments:
        for l in llm_output.splitlines():
            m = re.match(r'\s*[\*-]\s*(.+)', l)
            if m:
                comment = m.group(1).strip()
                line_comments.append((None, 1, comment))
    
    # Fallback: use first paragraph as summary
    if not summary:
        paras = [p.strip() for p in llm_output.split('\n\n') if p.strip()]
        if paras:
            summary = paras[0]
    
    return line_comments, summary


def query_ollama_for_review(prompt, diff):
    """
    Query Ollama for code review with improved parsing
    """
    model = os.environ.get('LLM_MODEL', 'codellama-trained-20250624_193347:latest')
    print(f"[LLM DEBUG] Using model: {model}")
    
    try:
        response = requests.post('http://localhost:11434/api/generate', 
                               json={
                                   'model': model,
                                   'prompt': prompt,
                                   'stream': False
                               })
        
        if response.status_code != 200:
            print(f"[LLM ERROR] HTTP {response.status_code}: {response.text}")
            return [], "Error: LLM service unavailable"
        
        result = response.json()
        llm_response = result.get('response', '').strip()
        
        print(f"[LLM DEBUG] Raw response length: {len(llm_response)}")
        print(f"[LLM DEBUG] Response preview: {llm_response[:200]}...")
        
        # Parse line comments and summary
        line_comments = []
        summary = ""
        
        lines = llm_response.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('LINE ') and 'COMMENT:' in line:
                # Extract line number and comment
                try:
                    # Format: LINE X COMMENT: [comment]
                    parts = line.split('COMMENT:', 1)
                    if len(parts) == 2:
                        line_part = parts[0].strip()
                        comment = parts[1].strip()
                        
                        # Extract line number
                        line_num_match = re.search(r'LINE (\d+)', line_part)
                        if line_num_match:
                            line_num = int(line_num_match.group(1))
                            line_comments.append((None, line_num, comment))
                        else:
                            # If no line number, use None
                            line_comments.append((None, None, comment))
                except Exception as e:
                    print(f"[LLM DEBUG] Error parsing line comment: {e}")
                    continue
                    
            elif line.startswith('SUMMARY:'):
                summary = line.split('SUMMARY:', 1)[1].strip()
        
        # If no structured comments found, try to extract from free text
        if not line_comments and not summary:
            print("[LLM DEBUG] No structured comments found, attempting free text extraction...")
            
            # Look for security-related keywords in the response
            security_keywords = [
                'hardcoded', 'password', 'credential', 'eval', 'injection',
                'security', 'vulnerability', 'unsafe', 'dangerous'
            ]
            
            found_issues = []
            for keyword in security_keywords:
                if keyword.lower() in llm_response.lower():
                    found_issues.append(f"Found {keyword} issue")
            
            if found_issues:
                summary = f"Potential issues detected: {', '.join(found_issues[:3])}"
                # Create a generic comment for the first line
                line_comments.append((None, 1, "Security review needed - check for vulnerabilities"))
        
        print(f"[LLM DEBUG] Parsed {len(line_comments)} line comments")
        print(f"[LLM DEBUG] Summary: {summary}")
        
        return line_comments, summary
        
    except Exception as e:
        print(f"[LLM ERROR] Exception: {e}")
        return [], f"Error: {str(e)}"


def query_ollama(prompt, model=None):
    """Send a prompt to the Ollama server and return the response text. Truncate if too large."""
    model = model or OLLAMA_MODEL
    prompt_len = len(prompt)
    if prompt_len > PROMPT_MAX_CHARS:
        print(f"[WARN] LLM prompt too large ({prompt_len} chars), truncating to {PROMPT_MAX_CHARS}.")
        prompt = prompt[:PROMPT_MAX_CHARS]
        print("[INFO] PR is too large for a single LLM call. Consider chunked review or summarization.")
    print(f"[LLM DEBUG] Using model: {model}, prompt size: {len(prompt)} chars")
    try:
        response = requests.post(OLLAMA_URL, json={"model": model, "prompt": prompt}, timeout=120)
        response.raise_for_status()
        try:
            return response.json().get("response", "")
        except Exception as e:
            print(f"[LLM WARN] Response not valid JSON, returning raw text. Error: {e}")
            return response.text
    except Exception as e:
        print(f"[LLM ERROR] Model: {model}, prompt size: {len(prompt)}")
        print(f"[LLM ERROR] Prompt (start): \n{prompt[:500]}\n...")
        print(f"[LLM ERROR] {e}")
        return f"[ERROR] Ollama LLM: {e}" 