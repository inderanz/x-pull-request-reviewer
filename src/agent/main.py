import os
import click
from . import git_utils
from .static_analysis import analyze_directory
from .diff_utils import parse_unified_diff, chunk_diff_by_file_and_hunk
from .change_manager import ChangeManager
from .suggestion_parser import parse_suggestions_from_llm, extract_code_changes_from_suggestions
from ..llm.review_prompt import build_review_prompt, build_actionable_suggestions_prompt
from ..llm.unified_client import get_llm_client, query_llm_for_review
from ..github.pr_client import post_pr_comment, post_line_comment, get_pr_metadata
from ..review.security import security_issues_in_diff
from ..review.compliance import compliance_issues_in_diff
from ..review.best_practices import best_practices_in_diff
from ..review.dependency import analyze_dependencies
from ..review.test_coverage import analyze_test_coverage
from ..review.documentation import analyze_documentation
import re
import shutil
import glob
import mimetypes
import time
import sys


def extract_repo_url_from_pr_url(pr_url):
    """Extract repository URL from GitHub PR URL"""
    # Pattern: https://github.com/org/repo/pull/NUMBER
    match = re.match(r'https://github\.com/([^/]+/[^/]+)/pull/\d+', pr_url)
    if match:
        org_repo = match.group(1)
        return f"https://github.com/{org_repo}.git"
    return None


def get_latest_commit_sha(repo_dir, branch):
    import subprocess
    result = subprocess.run(['git', 'rev-parse', branch], cwd=repo_dir, capture_output=True, text=True)
    if result.returncode == 0:
        return result.stdout.strip()
    return None


def apply_suggested_changes(change_manager: ChangeManager, suggestions: list, repo_dir: str) -> list:
    """Apply suggested changes and track them in the change manager."""
    applied_changes = []
    
    for suggestion in suggestions:
        if suggestion['type'] in ['file_change', 'line_change']:
            file_path = suggestion['file_path']
            full_path = os.path.join(repo_dir, file_path)
            
            if os.path.exists(full_path):
                try:
                    with open(full_path, 'r') as f:
                        lines = f.readlines()
                    
                    line_num = suggestion['line_number']
                    if 1 <= line_num <= len(lines):
                        current_line = lines[line_num - 1].strip()
                        
                        # For now, we'll add a TODO comment as a placeholder
                        # In a real implementation, you might want to use the LLM to generate actual code
                        suggested_line = f"# TODO: {suggestion['reason']}\n{current_line}"
                        
                        change_id = change_manager.apply_change(
                            full_path, line_num, suggested_line, suggestion['reason']
                        )
                        
                        if change_id > 0:
                            applied_changes.append({
                                'id': change_id,
                                'suggestion': suggestion,
                                'file_path': full_path,
                                'line_number': line_num
                            })
                
                except Exception as e:
                    click.echo(f"[WARNING] Could not apply change to {file_path}: {e}")
    
    return applied_changes


def interactive_change_management(change_manager: ChangeManager, llm_response: str, repo_dir: str, diff: str) -> str:
    """Handle interactive change management with user input."""
    click.echo("\n" + "="*80)
    click.echo("INTERACTIVE CHANGE MANAGEMENT")
    click.echo("="*80)
    
    # Parse suggestions from LLM response
    suggestions = parse_suggestions_from_llm(llm_response, diff)
    
    if not suggestions:
        click.echo("No actionable suggestions found in the review.")
        return llm_response
    
    # Display parsed suggestions
    parser = type('Parser', (), {'suggestions': suggestions})()
    parser.display_suggestions = lambda: None  # We'll handle display manually
    
    actionable_suggestions = [s for s in suggestions if s['type'] in ['file_change', 'line_change']]
    general_suggestions = [s for s in suggestions if s['type'] == 'general']
    
    if actionable_suggestions:
        click.echo(f"\n📝 ACTIONABLE CHANGES ({len(actionable_suggestions)}):")
        for i, suggestion in enumerate(actionable_suggestions, 1):
            click.echo(f"\n  [{i}] {suggestion['file_path']}:{suggestion['line_number']}")
            click.echo(f"      Reason: {suggestion['reason']}")
            if suggestion['current_line']:
                click.echo(f"      Current: {suggestion['current_line']}")
    
    if general_suggestions:
        click.echo(f"\n💡 GENERAL SUGGESTIONS ({len(general_suggestions)}):")
        for i, suggestion in enumerate(general_suggestions, 1):
            click.echo(f"\n  [{i}] {suggestion['reason']}")
    
    # Ask user if they want to apply changes
    if actionable_suggestions:
        click.echo("\n" + "-"*80)
        click.echo("CHANGE APPLICATION OPTIONS")
        click.echo("-"*80)
        click.echo("You can apply specific changes using the following options:")
        click.echo("• Enter suggestion ID (e.g., '1') to apply a specific change")
        click.echo("• Enter 'all' to apply all suggested changes")
        click.echo("• Enter 'none' to skip all changes")
        click.echo("• Enter multiple IDs separated by commas (e.g., '1,3,5')")
        
        while True:
            try:
                choice = click.prompt("\nEnter your choice", type=str, default="none").strip().lower()
                
                if choice == "none":
                    click.echo("No changes applied.")
                    break
                
                elif choice == "all":
                    applied_changes = apply_suggested_changes(change_manager, actionable_suggestions, repo_dir)
                    click.echo(f"Applied {len(applied_changes)} changes.")
                    break
                
                else:
                    # Handle multiple IDs or single ID
                    ids = [id.strip() for id in choice.split(",")]
                    selected_suggestions = []
                    
                    for id_str in ids:
                        try:
                            suggestion_id = int(id_str) - 1  # Convert to 0-based index
                            if 0 <= suggestion_id < len(actionable_suggestions):
                                selected_suggestions.append(actionable_suggestions[suggestion_id])
                            else:
                                click.echo(f"[ERROR] Invalid suggestion ID: {id_str}")
                        except ValueError:
                            click.echo(f"[ERROR] Invalid suggestion ID: {id_str}")
                    
                    if selected_suggestions:
                        applied_changes = apply_suggested_changes(change_manager, selected_suggestions, repo_dir)
                        click.echo(f"Applied {len(applied_changes)} changes.")
                        break
                    else:
                        click.echo("[ERROR] No valid suggestions were selected. Please try again.")
                        continue
                        
            except click.Abort:
                click.echo("Operation cancelled by user.")
                break
    
    # Now handle reversion if any changes were applied
    applied_changes = change_manager.get_applied_changes()
    if applied_changes:
        click.echo("\n" + "-"*80)
        click.echo("CHANGE REVERSION")
        click.echo("-"*80)
        click.echo("Some changes have been applied. You can now revert specific changes if needed.")
        
        revert_result = change_manager.interactive_revert_prompt()
        click.echo(f"\n[INFO] {revert_result}")
    
    # Generate updated review summary
    updated_review = change_manager.generate_review_summary(llm_response)
    return updated_review


def extract_terraform_module_sources_from_files(repo_dir):
    """
    Parse all .tf files in the repo for module blocks with git source URLs.
    Returns a set of unique git URLs.
    """
    module_sources = set()
    import glob
    tf_files = glob.glob(os.path.join(repo_dir, "**", "*.tf"), recursive=True)
    for tf_file in tf_files:
        with open(tf_file, "r") as f:
            content = f.read()
            # Find all module blocks
            for module_match in re.finditer(r'module\s+"([^"]+)"\s*{([^}]*)}', content, re.DOTALL):
                block_body = module_match.group(2)
                # Look for source = "git::..."
                source_match = re.search(r'source\s*=\s*"(git::[^"]+)"', block_body)
                if source_match:
                    module_sources.add(source_match.group(1))
    return module_sources


def prompt_and_clone_modules(module_sources, cloned_modules_dir):
    """
    Prompt the user for each unique, not-yet-cloned module source.
    Returns a list of local paths to cloned modules to review.
    """
    cloned_paths = []
    skip_all = False
    os.makedirs(cloned_modules_dir, exist_ok=True)
    for url in module_sources:
        module_name = url.split('/')[-1].replace('.git', '')
        dest_dir = os.path.join(cloned_modules_dir, module_name)
        if os.path.exists(dest_dir):
            continue  # Already cloned
        if skip_all:
            continue
        # Sample prompt/UX:
        print(f"\nThis PR depends on external module: {url}")
        resp = input("Do you want to clone and review this module as part of the PR review? (y/n/skip all): ").strip().lower()
        if resp == 'y':
            print(f"Cloning {url} to {dest_dir} ...")
            try:
                # Use git to clone
                import subprocess
                subprocess.run(['git', 'clone', url.replace('git::', ''), dest_dir], check=True)
                cloned_paths.append(dest_dir)
            except Exception as e:
                print(f"[ERROR] Failed to clone {url}: {e}")
        elif resp == 'skip all':
            skip_all = True
        # else: skip this module
    return cloned_paths


def is_binary_file(filepath):
    # Simple check for binary files
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(1024)
            if b'\0' in chunk:
                return True
        # Also check mimetype
        mime, _ = mimetypes.guess_type(filepath)
        if mime and not mime.startswith('text'):
            return True
    except Exception:
        return False
    return False


def find_external_git_dependencies_in_diff(diff):
    """
    Scan the diff for new/changed references to external git repositories in supported files.
    Returns a set of unique git URLs.
    """
    git_urls = set()
    current_file = None
    for line in diff.splitlines():
        # Track which file we're in
        if line.startswith('+++ '):
            current_file = line[4:].strip()
            if current_file.startswith('b/'):
                current_file = current_file[2:]
        # Only consider added lines
        if line.startswith('+') and not line.startswith('+++') and current_file:
            added_line = line[1:].strip()
            # .tf files: look for module source = "git::..."
            if current_file.endswith('.tf'):
                m = re.search(r'source\s*=\s*"(git::[^"]+)"', added_line)
                if m:
                    git_urls.add(m.group(1))
            # .gitmodules: look for url = ...
            elif current_file.endswith('.gitmodules'):
                if 'url =' in added_line:
                    url = added_line.split('=', 1)[1].strip()
                    if url.startswith('http') or url.startswith('git@'):
                        git_urls.add(url)
            # requirements.txt: look for git+ URLs
            elif current_file.endswith('requirements.txt'):
                if 'git+' in added_line:
                    url = added_line.split('git+', 1)[1].strip()
                    if url:
                        git_urls.add('https://' + url if not url.startswith('http') else url)
            # go.mod: look for github.com/gitlab.com in added lines
            elif current_file.endswith('go.mod'):
                if 'github.com' in added_line or 'gitlab.com' in added_line:
                    parts = added_line.split()
                    for part in parts:
                        if part.startswith('github.com') or part.startswith('gitlab.com'):
                            git_urls.add('https://' + part)
            # README.md: look for git clone commands
            elif current_file.lower() == 'readme.md':
                if 'git clone' in added_line:
                    tokens = added_line.split()
                    for i, token in enumerate(tokens):
                        if token == 'git' and i+2 < len(tokens) and tokens[i+1] == 'clone':
                            url = tokens[i+2]
                            if url.startswith('http') or url.startswith('git@'):
                                git_urls.add(url)
    return git_urls


def prompt_and_clone_external_repos(git_urls, cloned_dir):
    """
    Prompt the user for each unique, not-yet-cloned external git repo.
    Returns a list of local paths to cloned repos to review.
    """
    cloned_paths = []
    skip_all = False
    os.makedirs(cloned_dir, exist_ok=True)
    for url in git_urls:
        repo_name = url.split('/')[-1].replace('.git', '')
        dest_dir = os.path.join(cloned_dir, repo_name)
        if os.path.exists(dest_dir):
            continue  # Already cloned
        if skip_all:
            continue
        print(f"\nThis PR depends on external repository: {url}")
        resp = input("Do you want to clone and review this repository as part of the PR review? (y/n/skip all): ").strip().lower()
        if resp == 'y':
            print(f"Cloning {url} to {dest_dir} ...")
            try:
                import subprocess
                # Fix: Strip 'git::' prefix if present
                clone_url = url
                if clone_url.startswith('git::'):
                    clone_url = clone_url[len('git::'):]
                subprocess.run(['git', 'clone', clone_url, dest_dir], check=True)
                cloned_paths.append(dest_dir)
            except Exception as e:
                print(f"[ERROR] Failed to clone {url}: {e}")
        elif resp == 'skip all':
            skip_all = True
        # else: skip this repo
    return cloned_paths


def log_audit(message):
    """Log audit events to both console and a file."""
    print(f"[AUDIT] {message}")
    try:
        with open("audit.log", "a") as f:
            f.write(message + "\n")
    except Exception as e:
        print(f"[AUDIT ERROR] Could not write to audit.log: {e}")


def review_pr_or_branch(repo_url=None, repo_path=None, branch=None, base_branch='main', pr_number=None, repo_slug=None, interactive=True, plugins=None, provider=None):
    """
    Clone or use a local repo, fetch and checkout the branch, and get the diff.
    Optionally post the LLM review as a PR comment if pr_number and repo_slug are provided.
    Now includes interactive change management.
    Only review, line comments, and summary are posted. No approve/merge or other actions are taken.
    """
    from ..github.pr_client import get_pr_metadata
    if repo_url:
        # If it's a PR URL, extract the repository URL
        if '/pull/' in repo_url and pr_number and repo_slug:
            actual_repo_url = extract_repo_url_from_pr_url(repo_url)
            if not actual_repo_url:
                click.echo(f"Error: Could not extract repository URL from PR URL: {repo_url}")
                return
            click.echo(f"Extracted repository URL from PR: {actual_repo_url}")
            repo_url = actual_repo_url
            # Fetch PR metadata
            pr_meta = get_pr_metadata(repo_slug, pr_number)
            if not pr_meta:
                click.echo(f"Error: Could not fetch PR metadata for {repo_slug}#{pr_number}")
                return
            base_branch = pr_meta['base_branch']
            branch = pr_meta['head_branch']
            click.echo(f"[INFO] PR base branch: {base_branch}, head branch: {branch}")
        
        dest_dir = os.path.join('workspace', os.path.basename(repo_url.rstrip('/').replace('.git', '')))
        if not os.path.exists(dest_dir):
            git_utils.clone_repo(repo_url, dest_dir)
        repo_dir = dest_dir
    elif repo_path:
        repo_dir = repo_path
    else:
        click.echo("Either repo_url or repo_path must be provided.")
        return

    # Initialize change manager
    change_manager = ChangeManager(repo_dir)

    if branch:
        git_utils.fetch_branch(repo_dir, branch)
        git_utils.checkout_branch(repo_dir, branch)
        diff = git_utils.get_diff(repo_dir, base_branch, branch)
        click.echo(f"\n[DIFF] {base_branch}..{branch}:\n{diff[:1000]}{'... (truncated)' if len(diff) > 1000 else ''}")
    else:
        click.echo("No branch specified for review.")
        diff = ""

    # NEW: Only prompt for external git dependencies if referenced/changed in the diff
    external_git_urls = find_external_git_dependencies_in_diff(diff)
    if external_git_urls:
        cloned_dir = os.path.join(repo_dir, 'external_repos')
        cloned_paths = prompt_and_clone_external_repos(external_git_urls, cloned_dir)
        for ext_path in cloned_paths:
            print(f"\n[INFO] Reviewing external repository: {ext_path}")
            ext_summary = analyze_directory(ext_path)
            for file, results in ext_summary.items():
                print(f"[STATIC ANALYSIS] {file}")
                print(f"  Format: {results['format']}")
                print(f"  Lint:   {results['lint']}")
            print(f"[INFO] External repository review complete: {ext_path}")

    # Run static analysis
    click.echo("\n[INFO] Running static analysis (format/lint checks)...")
    summary = analyze_directory(repo_dir)
    for file, results in summary.items():
        click.echo(f"\n[STATIC ANALYSIS] {file}")
        click.echo(f"  Format: {results['format']}")
        click.echo(f"  Lint:   {results['lint']}")

    # NEW: Run comprehensive review engines
    click.echo("\n[INFO] Running comprehensive review engines...")
    
    # Security Analysis
    try:
        security_issues = security_issues_in_diff(diff, language)
        if security_issues:
            click.echo(f"\n[SECURITY] Found {len(security_issues)} security issues:")
            for issue in security_issues:
                click.echo(f"  ⚠️  {issue}")
                log_audit(f"[SECURITY] {issue}")
        else:
            click.echo("[SECURITY] No security issues detected")
    except Exception as e:
        click.echo(f"[SECURITY] Error in security analysis: {e}")
        log_audit(f"[ERROR] Security analysis failed: {e}")

    # Compliance Analysis
    try:
        compliance_issues = compliance_issues_in_diff(diff, language)
        if compliance_issues:
            click.echo(f"\n[COMPLIANCE] Found {len(compliance_issues)} compliance issues:")
            for issue in compliance_issues:
                click.echo(f"  📋 {issue}")
                log_audit(f"[COMPLIANCE] {issue}")
        else:
            click.echo("[COMPLIANCE] No compliance issues detected")
    except Exception as e:
        click.echo(f"[COMPLIANCE] Error in compliance analysis: {e}")
        log_audit(f"[ERROR] Compliance analysis failed: {e}")

    # Best Practices Analysis
    try:
        best_practice_issues = best_practices_in_diff(diff, language)
        if best_practice_issues:
            click.echo(f"\n[BEST PRACTICES] Found {len(best_practice_issues)} best practice issues:")
            for issue in best_practice_issues:
                click.echo(f"  💡 {issue}")
                log_audit(f"[BEST PRACTICES] {issue}")
        else:
            click.echo("[BEST PRACTICES] No best practice issues detected")
    except Exception as e:
        click.echo(f"[BEST PRACTICES] Error in best practices analysis: {e}")
        log_audit(f"[ERROR] Best practices analysis failed: {e}")

    # Dependency Analysis
    try:
        dependency_issues = analyze_dependencies(repo_dir, language)
        if dependency_issues:
            click.echo(f"\n[DEPENDENCIES] Found {len(dependency_issues)} dependency issues:")
            for issue in dependency_issues:
                click.echo(f"  📦 {issue}")
                log_audit(f"[DEPENDENCIES] {issue}")
        else:
            click.echo("[DEPENDENCIES] No dependency issues detected")
    except Exception as e:
        click.echo(f"[DEPENDENCIES] Error in dependency analysis: {e}")
        log_audit(f"[ERROR] Dependency analysis failed: {e}")

    # Test Coverage Analysis
    try:
        test_coverage_issues = analyze_test_coverage(repo_dir, language)
        if test_coverage_issues:
            click.echo(f"\n[TEST COVERAGE] Found {len(test_coverage_issues)} test coverage issues:")
            for issue in test_coverage_issues:
                click.echo(f"  🧪 {issue}")
                log_audit(f"[TEST COVERAGE] {issue}")
        else:
            click.echo("[TEST COVERAGE] No test coverage issues detected")
    except Exception as e:
        click.echo(f"[TEST COVERAGE] Error in test coverage analysis: {e}")
        log_audit(f"[ERROR] Test coverage analysis failed: {e}")

    # Documentation Analysis
    try:
        documentation_issues = analyze_documentation(repo_dir, language)
        if documentation_issues:
            click.echo(f"\n[DOCUMENTATION] Found {len(documentation_issues)} documentation issues:")
            for issue in documentation_issues:
                click.echo(f"  📚 {issue}")
                log_audit(f"[DOCUMENTATION] {issue}")
        else:
            click.echo("[DOCUMENTATION] No documentation issues detected")
    except Exception as e:
        click.echo(f"[DOCUMENTATION] Error in documentation analysis: {e}")
        log_audit(f"[ERROR] Documentation analysis failed: {e}")

    # Prepare comprehensive static summary string for LLM
    static_summary_str = "\n".join([
        f"{file}:\n  Format: {results['format']}\n  Lint: {results['lint']}" for file, results in summary.items()
    ])

    # Add review engine results to summary
    review_summaries = []
    if security_issues:
        review_summaries.append(f"Security Issues: {', '.join(security_issues)}")
    if compliance_issues:
        review_summaries.append(f"Compliance Issues: {', '.join(compliance_issues)}")
    if best_practice_issues:
        review_summaries.append(f"Best Practice Issues: {', '.join(best_practice_issues)}")
    if dependency_issues:
        review_summaries.append(f"Dependency Issues: {', '.join(dependency_issues)}")
    if test_coverage_issues:
        review_summaries.append(f"Test Coverage Issues: {', '.join(test_coverage_issues)}")
    if documentation_issues:
        review_summaries.append(f"Documentation Issues: {', '.join(documentation_issues)}")
    
    if review_summaries:
        static_summary_str += "\n\nReview Engine Results:\n" + "\n".join(review_summaries)

    # Detect language (simple heuristic: use first file's extension)
    language = 'code'
    if summary:
        first_file = next(iter(summary))
        ext = os.path.splitext(first_file)[1]
        lang_map = {
            '.tf': 'Terraform', '.py': 'Python', '.yaml': 'YAML', '.yml': 'YAML',
            '.go': 'Go', '.java': 'Java', '.sh': 'Shell'
        }
        language = lang_map.get(ext, 'code')

    # Check for large diffs
    diff_size = len(diff) if 'diff' in locals() else 0
    if diff_size > 100_000:
        log_audit(f"[WARN] Diff too large for LLM: {diff_size} bytes. Skipping LLM review.")
        print("[WARN] Diff too large for LLM review. Skipping LLM step.")
        return

    # Skip binary files
    for root, dirs, files in os.walk(repo_dir):
        for file in files:
            path = os.path.join(root, file)
            if is_binary_file(path):
                log_audit(f"[SKIP] Skipping binary file: {path}")

    # Run plugins (custom checks/adapters)
    if plugins:
        for plugin in plugins:
            try:
                plugin.run(repo_dir)
                log_audit(f"[PLUGIN] Ran plugin: {plugin.__file__}")
            except Exception as e:
                log_audit(f"[ERROR] Plugin {plugin.__file__} failed: {e}")

    # Query LLM for review (chunked, with progress/debug logging)
    try:
        click.echo("\n[INFO] Querying LLM for review...")
        all_line_comments = []
        all_summaries = []
        start_time = time.time()
        
        # Explicitly detect the provider
        from ..llm.unified_client import get_llm_client
        if provider:
            client = get_llm_client(provider=provider)
        else:
            client = get_llm_client()
        detected_provider = getattr(client, 'provider', None)
        click.echo(f"[DEBUG] Detected LLM provider: {detected_provider}")
        using_gemini_cli = detected_provider == "gemini_cli"
        
        if using_gemini_cli:
            click.echo("[INFO] Using Gemini CLI - processing entire diff without chunking...")
            prompt = build_review_prompt(diff, static_summary_str, language)
            try:
                line_comments, summary_comment = query_llm_for_review(prompt, diff, provider=detected_provider)
                click.echo(f"[LLM] Response received: {len(line_comments)} comments, summary: {summary_comment[:100]}...")
                click.echo(f"[LLM] Raw line_comments: {line_comments}")
                click.echo(f"[LLM] Raw summary: {summary_comment}")
                all_line_comments = line_comments
                all_summaries = [summary_comment] if summary_comment else []
            except Exception as e:
                click.echo(f"[LLM] Error: {e}")
                log_audit(f"[ERROR] LLM error: {e}")
                all_line_comments, all_summaries = [], []
        else:
            # Use chunking for other providers
            click.echo("[INFO] Using chunked processing...")
            # PATCH: For Terraform, chunk by resource block
            if language.lower() == "terraform":
                import re
                resource_blocks = re.split(r'\nresource\s+"', diff)
                chunked = []
                for i, block in enumerate(resource_blocks):
                    if i == 0 and not block.strip().startswith('resource'):
                        continue
                    chunk = ("terraform/gke_spanner_sql_bad.tf", f"resource block {i}", ("resource " if i > 0 else "") + block)
                    chunked.append(chunk)
            else:
                chunked = chunk_diff_by_file_and_hunk(diff, max_chunk_chars=2000)
            chunk_idx = 0
            total_chunks = len(chunked)
            for file_path, hunk_header, chunk_str in chunked:
                chunk_idx += 1
                chunk_desc = f"{file_path or ''} {hunk_header or ''}".strip()
                click.echo(f"[CHUNK {chunk_idx}/{total_chunks}] Reviewing chunk: {chunk_desc} (size: {len(chunk_str)} chars)")
                prompt = build_review_prompt(chunk_str, static_summary_str, language)
                chunk_start = time.time()
                try:
                    line_comments, summary_comment = query_llm_for_review(prompt, chunk_str, provider=detected_provider)
                    chunk_time = time.time() - chunk_start
                    click.echo(f"[CHUNK {chunk_idx}] LLM response time: {chunk_time:.2f}s")
                    click.echo(f"[CHUNK {chunk_idx}] LLM summary: {summary_comment}")
                    click.echo(f"[CHUNK {chunk_idx}] LLM line comments: {line_comments}")
                    # DEBUG: Log raw LLM output
                    log_audit(f"[LLM RAW OUTPUT] {line_comments} | SUMMARY: {summary_comment}")
                except Exception as e:
                    click.echo(f"[CHUNK {chunk_idx}] LLM error: {e}")
                    line_comments, summary_comment = [], None
                # Timeout/retry logic
                if (not line_comments or chunk_time > 60) and len(chunk_str) > 500:
                    click.echo(f"[CHUNK {chunk_idx}] Empty/slow response, retrying with smaller sub-chunks...")
                    sublines = chunk_str.split('\n')
                    for i in range(0, len(sublines), 10):
                        subchunk = '\n'.join(sublines[i:i+10])
                        if not subchunk.strip():
                            continue
                        subprompt = build_review_prompt(subchunk, static_summary_str, language)
                        try:
                            sub_start = time.time()
                            sub_line_comments, sub_summary = query_llm_for_review(subprompt, subchunk, provider=detected_provider)
                            sub_time = time.time() - sub_start
                            click.echo(f"[CHUNK {chunk_idx}] Sub-chunk {i//10+1}: LLM response time: {sub_time:.2f}s")
                            if sub_line_comments:
                                line_comments.extend(sub_line_comments)
                            if sub_summary:
                                all_summaries.append(sub_summary)
                        except Exception as e:
                            click.echo(f"[CHUNK {chunk_idx}] Sub-chunk {i//10+1} error: {e}")
                if line_comments:
                    all_line_comments.extend(line_comments)
                if summary_comment:
                    all_summaries.append(summary_comment)
        
        # Aggregate summaries
        summary_comment = '\n'.join(all_summaries) if all_summaries else ""
        total_time = time.time() - start_time
        click.echo(f"\n[LLM REVIEW] Summary (all chunks):\n{summary_comment}\nLine comments: {all_line_comments}")
        click.echo(f"\n[INFO] Review complete. Total time: {total_time:.2f}s. Total comments: {len(all_line_comments)}.")
    except Exception as e:
        log_audit(f"[ERROR] LLM/server error: {e}")
        print(f"[ERROR] LLM/server error: {e}")
        return

    # NEW: Interactive Change Management
    if interactive and all_line_comments:
        try:
            click.echo("\n[INFO] Starting interactive change management...")
            # Create a comprehensive LLM response for change management
            llm_response = f"Review Summary:\n{summary_comment}\n\nLine Comments:\n"
            for _, _, comment in all_line_comments:
                llm_response += f"- {comment}\n"
            
            # Run interactive change management
            updated_review = interactive_change_management(change_manager, llm_response, repo_dir, diff)
            click.echo(f"[INTERACTIVE] Change management completed. Updated review: {updated_review[:100]}...")
            log_audit(f"[INTERACTIVE] Change management completed")
        except Exception as e:
            click.echo(f"[INTERACTIVE] Error in change management: {e}")
            log_audit(f"[ERROR] Interactive change management failed: {e}")

    # Parse diff for actual changed lines and map LLM comments to real line numbers
    diff_lines = parse_unified_diff(diff)
    first_file = diff_lines[0][0] if diff_lines else None
    first_line = diff_lines[0][1] if diff_lines else 1

    # Map LLM comments to actual diff lines
    mapped_comments = []
    if all_line_comments and diff_lines:
        # Extract just the comments from LLM output (ignore line numbers)
        llm_comments = [comment for _, _, comment in all_line_comments]
        
        # Map each comment to a diff line, cycling through if we have more comments than lines
        for i, comment in enumerate(llm_comments):
            diff_index = i % len(diff_lines)
            file_path, line_num, _ = diff_lines[diff_index]
            mapped_comments.append((file_path, line_num, comment))
    elif all_line_comments:
        # If no diff lines but we have comments, map to first file
        for _, _, comment in all_line_comments:
            mapped_comments.append((first_file, first_line, comment))

    # Post line-specific comments for actionable findings (LLM-powered)
    if pr_number and repo_slug and os.environ.get('GITHUB_TOKEN') and branch:
        click.echo("\n[INFO] Posting LLM-powered line-by-line comments to PR...")
        commit_sha = get_latest_commit_sha(repo_dir, branch)
        
        # Post mapped comments
        for file_path, line_num, comment in mapped_comments:
            if file_path and line_num:
                result = post_line_comment(repo_slug, pr_number, comment, commit_sha, file_path, line_num)
                click.echo(f"[POST] {result}")
                log_audit(f"[POST] {result}")
            else:
                # If no file, post as general PR comment
                result = post_pr_comment(repo_slug, pr_number, comment)
                click.echo(f"[POST] {result}")
                log_audit(f"[POST] {result}")
        
        # Post all LLM comments as PR comments for visibility (including those without specific line numbers)
        for _, _, comment in all_line_comments:
            if comment and comment.strip():
                # Try to post as line comment first, fallback to general comment
                if diff_lines:
                    # Use the first diff line for general comments
                    first_diff_file, first_diff_line, _ = diff_lines[0]
                    result = post_line_comment(repo_slug, pr_number, comment, commit_sha, first_diff_file, first_diff_line)
                    click.echo(f"[POST-LINE] {result}")
                    log_audit(f"[POST-LINE] {result}")
                else:
                    # Post as general PR comment
                    result = post_pr_comment(repo_slug, pr_number, comment)
                    click.echo(f"[POST-GENERAL] {result}")
                    log_audit(f"[POST-GENERAL] {result}")
        
        # Post summary as PR comment
        if summary_comment:
            click.echo("\n[INFO] Posting LLM review summary as PR comment...")
            result = post_pr_comment(repo_slug, pr_number, summary_comment)
            click.echo(f"[POST] {result}")
            log_audit(f"[POST] {result}")
        click.echo("\n[NOTICE] This agent does NOT approve, merge, or take any action on PRs/branches. All such actions must be performed by the user in VSCode or GitHub UI.")

    # Only for Terraform
    if language.lower() == 'terraform':
        module_sources = extract_terraform_module_sources_from_files(repo_dir)
        if module_sources:
            cloned_modules_dir = os.path.join(repo_dir, 'external_modules')
            cloned_paths = prompt_and_clone_modules(module_sources, cloned_modules_dir)
            # For each cloned module, run static analysis and LLM review
            for mod_path in cloned_paths:
                print(f"\n[INFO] Reviewing external module: {mod_path}")
                mod_summary = analyze_directory(mod_path)
                for file, results in mod_summary.items():
                    print(f"[STATIC ANALYSIS] {file}")
                    print(f"  Format: {results['format']}")
                    print(f"  Lint:   {results['lint']}")
                # Optionally, run LLM review on module code (can be extended)
                print(f"[INFO] External module review complete: {mod_path}")

    click.echo("[INFO] Review complete. No PR/branch actions taken by agent. User must approve/merge in VSCode or GitHub UI.")


@click.command()
@click.option('--pr', 'pr_url', type=str, help='GitHub PR link to review')
@click.option('--repo', 'repo_path', type=str, help='Path to local repo')
@click.option('--branch', type=str, help='Branch to review')
@click.option('--pr-number', type=int, help='Pull request number (for posting comments)')
@click.option('--repo-slug', type=str, help='GitHub repo in org/repo format (for posting comments)')
@click.option('--no-interactive', is_flag=True, help='Disable interactive change management (useful for CI/CD)')
@click.option('--provider', type=click.Choice(['ollama', 'google_code_assist', 'gemini_cli']), help='LLM provider to use for the review')
@click.option('--help', is_flag=True, help='Show this message and exit.')
def review(pr_url, repo_path, branch, pr_number, repo_slug, no_interactive, provider, help):
    """Review a pull request or branch. Optionally post LLM review as PR comment if --pr-number and --repo-slug are provided."""
    if help:
        click.echo("\nUsage: xprr review [OPTIONS]\n")
        click.echo("  Review a pull request or branch. Optionally post LLM review as PR comment if --pr-number and --repo-slug are provided.\n")
        click.echo("  The review now includes interactive change management where you can: - Apply specific suggested changes - Revert applied changes if needed - Selectively ignore certain recommendations\n")
        click.echo("  Required GitHub token scopes: repo (for private repos), public_repo (for public repos), and write:discussion for comments.\n")
        click.echo("\nOptions:")
        click.echo("  --pr TEXT                       GitHub PR link to review")
        click.echo("  --repo TEXT                     Path to local repo")
        click.echo("  --branch TEXT                   Branch to review")
        click.echo("  --pr-number INTEGER             Pull request number (for posting comments)")
        click.echo("  --repo-slug TEXT                GitHub repo in org/repo format (for posting comments)")
        click.echo("  --no-interactive                Disable interactive change management (useful for CI/CD)")
        click.echo("  --provider [ollama|google_code_assist|gemini_cli]  LLM provider to use for the review")
        click.echo("  --help                          Show this message and exit.")
        sys.exit(0)

    # Handle PR URL and prompt for cloning
    if pr_url and not repo_path:
        repo_url = extract_repo_url_from_pr_url(pr_url)
        if not repo_url:
            click.echo(f"[ERROR] Could not extract repository URL from PR URL: {pr_url}")
            sys.exit(1)
        click.echo(f"[INFO] PR URL detected. Repository: {repo_url}")
        resp = click.prompt("Do you want to clone the repository for this PR review? [Y/n]", default="Y")
        if resp.strip().lower() in ["y", "yes", ""]:
            # Clone the repo if not already present
            dest_dir = os.path.join('workspace', os.path.basename(repo_url.rstrip('/').replace('.git', '')))
            if not os.path.exists(dest_dir):
                try:
                    git_utils.clone_repo(repo_url, dest_dir)
                except Exception as e:
                    click.echo(f"[ERROR] Failed to clone repository: {e}")
                    sys.exit(1)
            repo_path = dest_dir
            # Fetch PR metadata and checkout PR branch
            from ..github.pr_client import get_pr_metadata
            org_repo = repo_url.split('github.com/')[-1].replace('.git', '')
            pr_number = int(pr_url.rstrip('/').split('/')[-1])
            pr_meta = get_pr_metadata(org_repo, pr_number)
            if not pr_meta:
                click.echo(f"[ERROR] Could not fetch PR metadata for {org_repo}#{pr_number}")
                sys.exit(1)
            base_branch = pr_meta['base_branch']
            branch = pr_meta['head_branch']
            click.echo(f"[INFO] PR base branch: {base_branch}, head branch: {branch}")
        else:
            repo_path = click.prompt("Enter the path to your local clone of the repository", type=str)
            if not os.path.exists(repo_path):
                click.echo(f"[ERROR] Provided path does not exist: {repo_path}")
                sys.exit(1)

    # LLM provider selection
    from ..llm.unified_client import get_llm_client
    client = get_llm_client()
    available_providers = client.get_available_providers()
    enabled_providers = [p for p, ok in available_providers.items() if ok]
    if not provider:
        if len(enabled_providers) == 0:
            click.echo("[ERROR] No LLM providers are available. Please configure at least one provider.")
            sys.exit(1)
        elif len(enabled_providers) == 1:
            provider = enabled_providers[0]
            click.echo(f"[INFO] Only one LLM provider available: {provider}")
        else:
            click.echo("Multiple LLM providers detected:")
            for idx, p in enumerate(enabled_providers, 1):
                click.echo(f"  {idx}. {p}")
            sel = click.prompt(f"Select provider [1-{len(enabled_providers)}]", type=int, default=1)
            provider = enabled_providers[sel-1]
    else:
        if provider not in enabled_providers:
            click.echo(f"[ERROR] Selected provider '{provider}' is not available. Available: {enabled_providers}")
            sys.exit(1)

    # Prompt for Gemini CLI key if needed
    if provider == "gemini_cli":
        from ..llm.credential_manager import get_credential_manager
        cred_mgr = get_credential_manager()
        if not cred_mgr.get_credential("gemini_cli", "api_key"):
            click.echo("Gemini CLI API key not found.")
            cred_mgr.prompt_for_credentials("gemini_cli")

    # Run the review
    review_pr_or_branch(
        repo_url=None,  # Already handled
        repo_path=repo_path,
        branch=branch,
        base_branch=None,
        pr_number=pr_number,
        repo_slug=repo_slug,
        interactive=not no_interactive,
        plugins=None,
        provider=provider
    ) 