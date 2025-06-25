def security_issues_in_diff(diff, language):
    """
    Simple heuristic-based security scan of a code diff for the given language.
    Returns a list of detected issues.
    """
    issues = []
    lower_diff = diff.lower()
    if language.lower() == 'python':
        if 'eval(' in lower_diff:
            issues.append('Use of eval() detected')
        if 'os.system(' in lower_diff:
            issues.append('Use of os.system() detected')
        if 'password' in lower_diff and '"' in lower_diff:
            issues.append('Possible hardcoded password')
    elif language.lower() == 'terraform':
        if 'plain_text' in lower_diff or 'sensitive = false' in lower_diff:
            issues.append('Possible sensitive value not protected')
    elif language.lower() == 'shell':
        if 'curl' in lower_diff and '| sh' in lower_diff:
            issues.append('Piping curl to shell detected')
        if 'sudo' in lower_diff:
            issues.append('Use of sudo detected')
    elif language.lower() == 'go':
        if 'exec.command' in lower_diff:
            issues.append('Use of exec.Command detected')
    elif language.lower() == 'java':
        if 'runtime.getruntime().exec' in lower_diff:
            issues.append('Use of Runtime.getRuntime().exec detected')
    return issues 