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


def map_llm_comments_to_lines(llm_comments, diff, filter_mode='added', context_lines=3):
    """
    Map LLM comments to valid (file_path, line_number) pairs for added lines in the diff.
    Supports filter modes: 'added', 'diff_context', 'file', 'nofilter'.
    Supports multi-line (range) comments if LLM provides (file, start_line, end_line, comment).
    If a comment cannot be mapped, return (None, None, comment) so it can be posted as a general comment.
    """
    # Parse the diff for added lines and context
    parsed_diff = parse_unified_diff_with_context(diff)
    added_lines = set()
    context_lines_set = set()
    file_lines = {}
    all_files = set()
    for item in parsed_diff:
        file_path = item['file']
        all_files.add(file_path)
        if file_path not in file_lines:
            file_lines[file_path] = set()
        file_lines[file_path].add(item['line_number'])
        if item['type'] == 'added':
            added_lines.add((file_path, item['line_number']))
            # For diff_context mode, add context lines
            idx = parsed_diff.index(item)
            for offset in range(-context_lines, context_lines+1):
                ctx_idx = idx + offset
                if 0 <= ctx_idx < len(parsed_diff):
                    ctx_item = parsed_diff[ctx_idx]
                    context_lines_set.add((ctx_item['file'], ctx_item['line_number']))

    mapped_comments = []
    for comment_tuple in llm_comments:
        # Support both (file, line, comment) and (file, start_line, end_line, comment)
        if len(comment_tuple) == 4:
            orig_file, start_line, end_line, comment = comment_tuple
            line_range = range(start_line, end_line+1) if start_line and end_line else []
        else:
            orig_file, orig_line, comment = comment_tuple
            line_range = [orig_line] if orig_line else []

        mapped = False
        # Try to map based on filter_mode
        if filter_mode == 'added':
            for line in line_range:
                if orig_file and (orig_file, line) in added_lines:
                    mapped_comments.append((orig_file, line, comment))
                    mapped = True
                    break
                elif not orig_file:
                    # Try to find any file with this added line
                    for file_path, lnum in added_lines:
                        if lnum == line:
                            mapped_comments.append((file_path, lnum, comment))
                            mapped = True
                            break
                if mapped:
                    break
        elif filter_mode == 'diff_context':
            for line in line_range:
                if orig_file and (orig_file, line) in context_lines_set:
                    mapped_comments.append((orig_file, line, comment))
                    mapped = True
                    break
                elif not orig_file:
                    for file_path, lnum in context_lines_set:
                        if lnum == line:
                            mapped_comments.append((file_path, lnum, comment))
                            mapped = True
                            break
                if mapped:
                    break
        elif filter_mode == 'file':
            for line in line_range:
                if orig_file and orig_file in file_lines and line in file_lines[orig_file]:
                    mapped_comments.append((orig_file, line, comment))
                    mapped = True
                    break
                elif not orig_file:
                    for file_path in file_lines:
                        if line in file_lines[file_path]:
                            mapped_comments.append((file_path, line, comment))
                            mapped = True
                            break
                if mapped:
                    break
        elif filter_mode == 'nofilter':
            # Allow any file/line
            for line in line_range:
                if orig_file:
                    mapped_comments.append((orig_file, line, comment))
                    mapped = True
                    break
                elif not orig_file:
                    for file_path in all_files:
                        mapped_comments.append((file_path, line, comment))
                        mapped = True
                        break
                if mapped:
                    break
        if not mapped:
            mapped_comments.append((None, None, comment))
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