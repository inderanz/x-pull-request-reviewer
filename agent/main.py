import os
import click
from . import git_utils
from .static_analysis import analyze_directory
from .diff_utils import parse_unified_diff
from .change_manager import ChangeManager
from .suggestion_parser import parse_suggestions_from_llm, extract_code_changes_from_suggestions
from llm.review_prompt import build_review_prompt, build_actionable_suggestions_prompt
from llm.ollama_client import query_ollama
from github.pr_client import post_pr_comment, post_line_comment
from review.security import security_issues_in_diff
from review.compliance import compliance_issues_in_diff
from review.best_practices import best_practices_in_diff
from review.dependency import analyze_dependencies
from review.test_coverage import analyze_test_coverage
from review.documentation import analyze_documentation
import re
import shutil
import glob


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


def review_pr_or_branch(repo_url=None, repo_path=None, branch=None, base_branch='main', pr_number=None, repo_slug=None, interactive=True):
    """
    Clone or use a local repo, fetch and checkout the branch, and get the diff.
    Optionally post the LLM review as a PR comment if pr_number and repo_slug are provided.
    Now includes interactive change management.
    Only review, line comments, and summary are posted. No approve/merge or other actions are taken.
    """
    if repo_url:
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

    # Run static analysis
    click.echo("\n[INFO] Running static analysis (format/lint checks)...")
    summary = analyze_directory(repo_dir)
    for file, results in summary.items():
        click.echo(f"\n[STATIC ANALYSIS] {file}")
        click.echo(f"  Format: {results['format']}")
        click.echo(f"  Lint:   {results['lint']}")

    # Prepare static summary string for LLM
    static_summary_str = "\n".join([
        f"{file}:\n  Format: {results['format']}\n  Lint: {results['lint']}" for file, results in summary.items()
    ])

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

    # LLM review
    click.echo("\n[INFO] Querying LLM for review...")
    prompt = build_review_prompt(diff, static_summary_str, language)
    llm_response = query_ollama(prompt)
    click.echo(f"\n[LLM REVIEW]\n{llm_response}")

    # Interactive change management
    if interactive:
        llm_response = interactive_change_management(change_manager, llm_response, repo_dir, diff)

    # Security, compliance, and best practices review
    click.echo("\n[INFO] Running security, compliance, and best practices checks...")
    sec_issues = security_issues_in_diff(diff, language)
    comp_issues = compliance_issues_in_diff(diff, language)
    best_issues = best_practices_in_diff(diff, language)

    if sec_issues:
        click.echo(f"\n[SECURITY ISSUES]\n- " + "\n- ".join(sec_issues))
    else:
        click.echo("\n[SECURITY ISSUES]\nNone detected.")
    if comp_issues:
        click.echo(f"\n[COMPLIANCE ISSUES]\n- " + "\n- ".join(comp_issues))
    else:
        click.echo("\n[COMPLIANCE ISSUES]\nNone detected.")
    if best_issues:
        click.echo(f"\n[BEST PRACTICES]\n- " + "\n- ".join(best_issues))
    else:
        click.echo("\n[BEST PRACTICES]\nNo major issues detected.")

    # Dependency analysis
    click.echo("\n[INFO] Running dependency analysis...")
    dep_issues = analyze_dependencies(repo_dir, language)
    if dep_issues:
        click.echo(f"\n[DEPENDENCY ISSUES]\n- " + "\n- ".join(dep_issues))
    else:
        click.echo("\n[DEPENDENCY ISSUES]\nNo risky or outdated dependencies detected.")

    # Test coverage analysis
    click.echo("\n[INFO] Running test coverage analysis...")
    coverage_summary = analyze_test_coverage(repo_dir, language)
    click.echo(f"\n[TEST COVERAGE]\n{coverage_summary}")

    # Documentation analysis
    click.echo("\n[INFO] Running documentation analysis...")
    doc_findings = analyze_documentation(repo_dir, language)
    click.echo("\n[DOCUMENTATION]\n" + "\n".join(doc_findings))

    # Post line-specific comments for actionable findings (only, never approve/merge)
    if repo_url and pr_number and repo_slug and os.environ.get('GITHUB_TOKEN') and branch:
        click.echo("\n[INFO] Posting line-specific comments for actionable findings...")
        commit_sha = get_latest_commit_sha(repo_dir, branch)
        diff_lines = parse_unified_diff(diff)
        for issue in sec_issues + comp_issues + best_issues:
            posted = False
            for file_path, line_num, line_content in diff_lines:
                if file_path in issue or line_content in issue or file_path in llm_response:
                    result = post_line_comment(repo_slug, pr_number, issue, commit_sha, file_path, line_num)
                    click.echo(result)
                    posted = True
                    break
            # If not posted, post on the first changed line of the first file
            if not posted and diff_lines:
                file_path, line_num, _ = diff_lines[0]
                result = post_line_comment(repo_slug, pr_number, issue, commit_sha, file_path, line_num)
                click.echo(result)

    # Also post a general summary as a PR comment (never approve/merge)
    if repo_url and pr_number and repo_slug and os.environ.get('GITHUB_TOKEN'):
        click.echo("\n[INFO] Posting LLM review as PR summary comment (no approve/merge actions will be taken)...")
        result = post_pr_comment(repo_slug, pr_number, llm_response)
        click.echo(result)
        click.echo("\n[NOTICE] This agent does NOT approve, merge, or take any action on PRs/branches. All such actions must be performed by the user in VSCode or the GitHub UI.")

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