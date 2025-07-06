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


def parse_unified_diff_with_context(diff):
    """
    Parse a unified diff and return detailed context including line numbers, content, and file information.
    Returns a more structured format for better LLM understanding.
    """
    results = []
    current_file = None
    new_line_num = None
    old_line_num = None
    hunk_context = []
    
    for line in diff.splitlines():
        if line.startswith('+++ '):
            current_file = line[4:].strip()
            if current_file.startswith('b/'):
                current_file = current_file[2:]
        elif line.startswith('@@'):
            # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
            m = re.match(r'@@ \-(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@', line)
            if m:
                old_line_num = int(m.group(1))
                new_line_num = int(m.group(3))
                hunk_context = []
        elif line.startswith('+') and not line.startswith('+++') and current_file and new_line_num is not None:
            # Added line
            results.append({
                'file': current_file,
                'line_number': new_line_num,
                'content': line[1:],
                'type': 'added',
                'context': hunk_context.copy()
            })
            new_line_num += 1
        elif line.startswith('-') and current_file and old_line_num is not None:
            # Removed line
            results.append({
                'file': current_file,
                'line_number': old_line_num,
                'content': line[1:],
                'type': 'removed',
                'context': hunk_context.copy()
            })
            old_line_num += 1
        elif not line.startswith('@@') and not line.startswith('+++') and new_line_num is not None:
            # Context line
            hunk_context.append(line)
            new_line_num += 1
            if old_line_num is not None:
                old_line_num += 1
    
    return results


def create_line_numbered_diff(diff):
    """
    Create a line-numbered version of the diff that makes it easier for the LLM to reference specific lines.
    """
    parsed_diff = parse_unified_diff_with_context(diff)
    
    if not parsed_diff:
        return diff
    
    # Group by file
    files = {}
    for item in parsed_diff:
        if item['file'] not in files:
            files[item['file']] = []
        files[item['file']].append(item)
    
    # Create numbered diff
    numbered_diff = []
    for file_path, changes in files.items():
        numbered_diff.append(f"File: {file_path}")
        numbered_diff.append("=" * (len(file_path) + 6))
        
        for change in changes:
            line_type = "+" if change['type'] == 'added' else "-"
            numbered_diff.append(f"{line_type} Line {change['line_number']}: {change['content']}")
        
        numbered_diff.append("")
    
    return "\n".join(numbered_diff)


def map_llm_comments_to_lines(llm_comments, diff):
    """
    Intelligently map LLM comments to actual diff lines based on line numbers and content.
    
    Args:
        llm_comments: List of (file_path, line_num, comment) tuples from LLM
        diff: The original diff string
    
    Returns:
        List of (file_path, line_num, comment) tuples with corrected line numbers
    """
    parsed_diff = parse_unified_diff(diff)
    
    if not parsed_diff:
        return llm_comments
    
    # Get the file path from the diff
    file_path = parsed_diff[0][0] if parsed_diff else None
    
    mapped_comments = []
    
    for orig_file, orig_line, comment in llm_comments:
        # If the LLM provided a reasonable line number, preserve it
        if orig_line and 1 <= orig_line <= 1000:
            mapped_comments.append((file_path, orig_line, comment))
        else:
            # Only apply fallback for clearly wrong line numbers
            mapped_comments.append((file_path, 1, comment))
    
    return mapped_comments


def extract_line_references_from_comment(comment):
    """
    Extract line number references from a comment using various patterns.
    Returns a list of (file_path, line_number) tuples.
    """
    references = []
    
    # Pattern 1: "line X" or "Line X"
    line_patterns = [
        r'line\s+(\d+)',
        r'Line\s+(\d+)',
        r'LINE\s+(\d+)',
        r'at\s+line\s+(\d+)',
        r'on\s+line\s+(\d+)'
    ]
    
    for pattern in line_patterns:
        matches = re.finditer(pattern, comment, re.IGNORECASE)
        for match in matches:
            line_num = int(match.group(1))
            references.append((None, line_num))
    
    # Pattern 2: "file:line" format
    file_line_pattern = r'([^:\s]+):(\d+)'
    matches = re.finditer(file_line_pattern, comment)
    for match in matches:
        file_path = match.group(1)
        line_num = int(match.group(2))
        references.append((file_path, line_num))
    
    return references


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