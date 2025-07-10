def best_practices_in_diff(diff, language):
    """
    Simple heuristic-based best practices scan of a code diff for the given language.
    Returns a list of detected issues or suggestions.
    """
    issues = []
    if language.lower() == 'python':
        if 'def ' in diff and '"""' not in diff:
            issues.append('Function missing docstring')
        if any(str(n) in diff for n in range(2, 10)) and 'const' not in diff and 'enum' not in diff:
            issues.append('Possible magic number detected')
    if language.lower() == 'terraform':
        if 'variable' in diff and 'description' not in diff:
            issues.append('Variable missing description')
    if language.lower() == 'go':
        if 'var ' in diff and '//' not in diff:
            issues.append('Variable missing comment')
    if language.lower() == 'java':
        if 'public class' in diff and '/**' not in diff:
            issues.append('Class missing Javadoc comment')
    return issues 