import re

def parse_unified_diff(diff):
    """
    Parse a unified diff and return a list of (file_path, line_number, line_content) for added/changed lines.
    Only considers lines starting with '+' (not '+++', not in removed lines).
    """
    results = []
    current_file = None
    new_line_num = None
    for line in diff.splitlines():
        if line.startswith('+++ '):
            current_file = line[4:].strip()
            if current_file.startswith('b/'):
                current_file = current_file[2:]
        elif line.startswith('@@'):
            m = re.match(r'@@ \-\d+,\d+ \+(\d+),(\d+) @@', line)
            if m:
                new_line_num = int(m.group(1))
        elif line.startswith('+') and not line.startswith('+++') and current_file and new_line_num is not None:
            results.append((current_file, new_line_num, line[1:]))
            new_line_num += 1
        elif not line.startswith('-') and not line.startswith('@@') and not line.startswith('+++') and new_line_num is not None:
            new_line_num += 1
    return results 