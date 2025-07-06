def compliance_issues_in_diff(diff, language):
    """
    Simple heuristic-based compliance scan of a code diff for the given language.
    Returns a list of detected issues.
    """
    issues = []
    # Always flag missing license header if 'license' is not present
    if 'license' not in diff.lower():
        issues.append('Missing license header')
    if language.lower() == 'terraform':
        if 'resource' in diff and 'name' in diff and ' ' in diff:
            issues.append('Resource name may not comply with naming conventions')
    if language.lower() == 'python':
        if 'import pickle' in diff.lower():
            issues.append('Use of pickle module may violate compliance policies')
    if language.lower() == 'java':
        if 'sun.' in diff:
            issues.append('Use of sun.* packages is forbidden in many orgs')
    return issues 