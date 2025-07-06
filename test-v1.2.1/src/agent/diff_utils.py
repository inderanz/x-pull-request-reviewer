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


def chunk_diff_by_file_and_hunk(diff, max_chunk_chars=3000):
    """
    Split a unified diff into per-file, per-hunk chunks, each <= max_chunk_chars.
    Returns a list of (file_path, hunk_header, chunk_diff_str).
    """
    chunks = []
    current_file = None
    current_hunk = None
    current_lines = []
    hunk_header = None
    for line in diff.splitlines():
        if line.startswith('+++ '):
            if current_lines:
                chunk_str = '\n'.join(current_lines)
                if chunk_str.strip():
                    chunks.append((current_file, hunk_header, chunk_str))
                current_lines = []
            current_file = line[4:].strip()
            if current_file.startswith('b/'):
                current_file = current_file[2:]
            hunk_header = None
        elif line.startswith('@@'):
            if current_lines:
                chunk_str = '\n'.join(current_lines)
                if chunk_str.strip():
                    chunks.append((current_file, hunk_header, chunk_str))
                current_lines = []
            hunk_header = line
        current_lines.append(line)
        # If chunk is too big, split
        if sum(len(l) for l in current_lines) > max_chunk_chars:
            chunk_str = '\n'.join(current_lines)
            chunks.append((current_file, hunk_header, chunk_str))
            current_lines = []
    # Add last chunk
    if current_lines:
        chunk_str = '\n'.join(current_lines)
        if chunk_str.strip():
            chunks.append((current_file, hunk_header, chunk_str))
    return chunks 