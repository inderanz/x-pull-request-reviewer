import re
import os
from typing import List, Dict, Optional, Tuple


class SuggestionParser:
    """Parses LLM responses to extract actionable code suggestions."""
    
    def __init__(self):
        self.suggestions = []
    
    def parse_llm_response(self, llm_response: str, diff: str) -> List[Dict]:
        """Parse LLM response to extract actionable suggestions."""
        self.suggestions = []
        
        # Only match the most specific pattern for file-based suggestions
        self._extract_file_suggestions(llm_response, diff)
        
        # Extract line-based suggestions as general if no file context
        self._extract_line_suggestions(llm_response, diff)
        
        # Extract general suggestions
        self._extract_general_suggestions(llm_response)
        
        # Remove duplicates
        self._deduplicate_suggestions()
        
        return self.suggestions
    
    def _extract_file_suggestions(self, llm_response: str, diff: str):
        """Extract suggestions that reference specific files and line numbers."""
        # Only match file: prefix pattern for test consistency
        pattern = r'file:([^:\s]+):(\d+):\s*(.+)'
        matches = re.findall(pattern, llm_response, re.IGNORECASE)
        for match in matches:
            file_path = match[0].strip()
            line_num = int(match[1])
            description = match[2].strip()
            
            # Try to find the actual line content from diff
            current_line = self._find_line_in_diff(diff, file_path, line_num)
            
            suggestion = {
                'type': 'file_change',
                'file_path': file_path,
                'line_number': line_num,
                'description': description,
                'current_line': current_line,
                'suggested_line': None,  # Will be filled by LLM if provided
                'reason': description
            }
            
            self.suggestions.append(suggestion)
    
    def _extract_line_suggestions(self, llm_response: str, diff: str):
        # If no file context, treat as general suggestion
        pattern = r'line\s+(\d+):\s*(.+)'
        matches = re.findall(pattern, llm_response, re.IGNORECASE)
        for match in matches:
            line_num = int(match[0])
            description = match[1].strip()
            suggestion = {
                'type': 'general',
                'file_path': None,
                'line_number': line_num,
                'description': description,
                'current_line': None,
                'suggested_line': None,
                'reason': description
            }
            self.suggestions.append(suggestion)
    
    def _extract_general_suggestions(self, llm_response: str):
        """Extract general suggestions that don't reference specific lines."""
        # Look for general suggestion patterns - more specific to avoid false matches
        general_patterns = [
            r'^suggestion:\s*(.+)$',
            r'^recommendation:\s*(.+)$',
        ]
        
        lines = llm_response.split('\n')
        for line in lines:
            line = line.strip()
            for pattern in general_patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    description = match.group(1).strip()
                    
                    suggestion = {
                        'type': 'general',
                        'file_path': None,
                        'line_number': None,
                        'description': description,
                        'current_line': None,
                        'suggested_line': None,
                        'reason': description
                    }
                    
                    self.suggestions.append(suggestion)
    
    def _deduplicate_suggestions(self):
        """Remove duplicate suggestions based on content."""
        seen = set()
        unique_suggestions = []
        
        for suggestion in self.suggestions:
            # Create a unique key for each suggestion
            if suggestion['type'] in ['file_change', 'line_change']:
                key = (suggestion['type'], suggestion['file_path'], suggestion['line_number'], suggestion['reason'])
            else:
                key = (suggestion['type'], suggestion['reason'])
            
            if key not in seen:
                seen.add(key)
                unique_suggestions.append(suggestion)
        
        self.suggestions = unique_suggestions
    
    def _find_line_in_diff(self, diff: str, file_path: str, line_num: int) -> Optional[str]:
        """Find the content of a specific line in the diff."""
        lines = diff.split('\n')
        in_target_file = False
        
        for line in lines:
            # Check if we're in the target file
            if line.startswith('+++') and file_path in line:
                in_target_file = True
                continue
            elif line.startswith('+++') and in_target_file:
                in_target_file = False
                continue
            
            if in_target_file and line.startswith('+') and not line.startswith('+++'):
                # This is an added line, check if it's the one we're looking for
                # We need to track line numbers in the diff
                pass
        
        return None
    
    def _find_file_for_line(self, diff: str, line_num: int) -> Optional[str]:
        """Find which file a line number belongs to in the diff."""
        lines = diff.split('\n')
        current_file = None
        
        for line in lines:
            if line.startswith('+++'):
                current_file = line[4:].strip()  # Remove '+++ ' prefix
            elif line.startswith('@@'):
                # Parse the line numbers from the hunk header
                # Format: @@ -old_start,old_count +new_start,new_count @@
                match = re.search(r'@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@', line)
                if match:
                    new_start = int(match.group(1))
                    # Check if our line number falls in this hunk
                    # This is a simplified approach
                    pass
        
        return current_file
    
    def get_actionable_suggestions(self) -> List[Dict]:
        """Get only suggestions that can be acted upon."""
        return [s for s in self.suggestions if s['type'] in ['file_change', 'line_change']]
    
    def get_general_suggestions(self) -> List[Dict]:
        """Get general suggestions that don't require specific line changes."""
        return [s for s in self.suggestions if s['type'] == 'general']
    
    def display_suggestions(self):
        """Display all parsed suggestions in a user-friendly format."""
        if not self.suggestions:
            print("No suggestions found.")
            return
        
        print("\n" + "="*80)
        print("PARSED SUGGESTIONS")
        print("="*80)
        
        actionable = self.get_actionable_suggestions()
        general = self.get_general_suggestions()
        
        if actionable:
            print(f"\n📝 ACTIONABLE CHANGES ({len(actionable)}):")
            for i, suggestion in enumerate(actionable, 1):
                print(f"\n  [{i}] {suggestion['file_path']}:{suggestion['line_number']}")
                print(f"      Reason: {suggestion['reason']}")
                if suggestion['current_line']:
                    print(f"      Current: {suggestion['current_line']}")
        
        if general:
            print(f"\n💡 GENERAL SUGGESTIONS ({len(general)}):")
            for i, suggestion in enumerate(general, 1):
                print(f"\n  [{i}] {suggestion['reason']}")


def parse_suggestions_from_llm(llm_response: str, diff: str) -> List[Dict]:
    """Convenience function to parse suggestions from LLM response."""
    parser = SuggestionParser()
    return parser.parse_llm_response(llm_response, diff)


def extract_code_changes_from_suggestions(suggestions: List[Dict], repo_dir: str) -> List[Dict]:
    """Extract actual code changes that can be applied from suggestions."""
    code_changes = []
    
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
                        
                        # Try to generate a suggested line based on the description
                        suggested_line = generate_suggested_line(
                            current_line, suggestion['description'], suggestion['reason']
                        )
                        
                        if suggested_line and suggested_line != current_line:
                            code_changes.append({
                                'file_path': full_path,
                                'line_number': line_num,
                                'current_line': current_line,
                                'suggested_line': suggested_line,
                                'reason': suggestion['reason']
                            })
                
                except Exception as e:
                    print(f"[WARNING] Could not process {file_path}: {e}")
    
    return code_changes


def generate_suggested_line(current_line: str, description: str, reason: str) -> Optional[str]:
    """Generate a suggested line based on the current line and description."""
    # This is a simplified implementation
    # In a real scenario, you might want to use the LLM to generate the actual code
    
    # Common patterns for code improvements
    patterns = [
        (r'add\s+input\s+validation', lambda line: f"# TODO: Add input validation\n{line}"),
        (r'add\s+error\s+handling', lambda line: f"try:\n    {line}\nexcept Exception as e:\n    # TODO: Handle error appropriately"),
        (r'use\s+more\s+descriptive\s+variable', lambda line: f"# TODO: Use more descriptive variable name\n{line}"),
        (r'add\s+logging', lambda line: f"import logging\n{line}\nlogging.info('Operation completed')"),
    ]
    
    for pattern, transform in patterns:
        if re.search(pattern, description, re.IGNORECASE):
            return transform(current_line)
    
    return None 