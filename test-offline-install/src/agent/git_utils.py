import subprocess
import os
import click


def run_git_command(args, cwd=None):
    """Run a git command using the user's environment."""
    result = subprocess.run([
        'git', *args
    ], cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        click.echo(f"[GIT ERROR] {result.stderr}")
        raise RuntimeError(result.stderr)
    return result.stdout.strip()


def clone_repo(repo_url, dest_dir):
    click.echo(f"Cloning repo: {repo_url} -> {dest_dir}")
    run_git_command(['clone', repo_url, dest_dir])


def fetch_branch(repo_dir, branch):
    # Check if remote 'origin' exists
    remotes = run_git_command(['remote'], cwd=repo_dir)
    if 'origin' in remotes.split():
        click.echo(f"Fetching branch: {branch} from origin")
        run_git_command(['fetch', 'origin', branch], cwd=repo_dir)
    else:
        click.echo(f"[INFO] No remote 'origin' found. Skipping fetch, using local branch '{branch}'.")


def checkout_branch(repo_dir, branch):
    click.echo(f"Checking out branch: {branch}")
    run_git_command(['checkout', branch], cwd=repo_dir)


def get_diff(repo_dir, base, compare):
    click.echo(f"Getting diff: {base}..{compare}")
    try:
        # First, try to fetch the base branch if it doesn't exist locally
        try:
            run_git_command(['show-ref', '--verify', f'refs/heads/{base}'], cwd=repo_dir)
        except:
            # Base branch doesn't exist locally, try to fetch it
            click.echo(f"Base branch '{base}' not found locally, fetching from origin...")
            try:
                run_git_command(['fetch', 'origin', base], cwd=repo_dir)
            except:
                click.echo(f"Could not fetch base branch '{base}' from origin")
        
        # Now try the diff
        return run_git_command(['diff', f'{base}..{compare}'], cwd=repo_dir)
    except Exception as e:
        click.echo(f"[WARNING] Could not get diff {base}..{compare}: {e}")
        # Fallback: try to get diff against origin/base
        try:
            click.echo(f"Trying diff against origin/{base}...")
            return run_git_command(['diff', f'origin/{base}..{compare}'], cwd=repo_dir)
        except Exception as e2:
            click.echo(f"[ERROR] Could not get diff against origin/{base}: {e2}")
            # Final fallback: get diff against HEAD
            click.echo("Falling back to diff against HEAD...")
            return run_git_command(['diff', 'HEAD'], cwd=repo_dir)


def get_working_dir_diff(repo_dir):
    """Get diff of working directory changes (unstaged and staged changes)."""
    click.echo("Getting working directory diff...")
    try:
        # Get both unstaged and staged changes
        unstaged = run_git_command(['diff'], cwd=repo_dir)
        staged = run_git_command(['diff', '--cached'], cwd=repo_dir)
        
        if unstaged and staged:
            return unstaged + "\n" + staged
        elif unstaged:
            return unstaged
        elif staged:
            return staged
        else:
            return ""
    except Exception as e:
        click.echo(f"[WARNING] Could not get working directory diff: {e}")
        return ""


def confirm_action(message):
    return click.confirm(message, default=True)


def safe_commit_and_push(repo_dir, message):
    if confirm_action("Do you want to commit and push changes? (human-in-the-loop)"):
        run_git_command(['add', '.'], cwd=repo_dir)
        run_git_command(['commit', '-m', message], cwd=repo_dir)
        run_git_command(['push'], cwd=repo_dir)
        click.echo("Changes committed and pushed.")
    else:
        click.echo("Commit/push cancelled by user.") 