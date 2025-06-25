import os
import re
import subprocess
import tempfile
from typing import List, Dict, Tuple, Optional
import click


class ChangeManager:
    """Manages interactive change selection and reversion for code reviews."""
    
    def __init__(self, repo_dir: str):
        self.repo_dir = repo_dir
        self.changes_made = []
        self.original_files = {}
        
    def track_changes(self, file_path: str, line_number: int, original_content: str, new_content: str, reason: str):
        """Track a change made to a file."""
        change_id = len(self.changes_made) + 1
        change = {
            'id': change_id,
            'file': file_path,
            'line': line_number,
            'original': original_content,
            'new': new_content,
            'reason': reason,
            'applied': True
        }
        self.changes_made.append(change)
        return change_id
    
    def backup_original_file(self, file_path: str):
        """Backup original file content before making changes."""
        if file_path not in self.original_files:
            try:
                with open(file_path, 'r') as f:
                    self.original_files[file_path] = f.read()
            except Exception as e:
                click.echo(f"[WARNING] Could not backup {file_path}: {e}")
    
    def apply_change(self, file_path: str, line_number: int, new_content: str, reason: str) -> int:
        """Apply a change to a file and track it."""
        self.backup_original_file(file_path)
        
        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
            
            if 1 <= line_number <= len(lines):
                original_content = lines[line_number - 1]
                lines[line_number - 1] = new_content + '\n'
                
                with open(file_path, 'w') as f:
                    f.writelines(lines)
                
                return self.track_changes(file_path, line_number, original_content, new_content, reason)
            else:
                click.echo(f"[ERROR] Line {line_number} is out of range for {file_path}")
                return -1
        except Exception as e:
            click.echo(f"[ERROR] Failed to apply change to {file_path}: {e}")
            return -1
    
    def revert_change(self, change_id: int) -> bool:
        """Revert a specific change by ID."""
        for change in self.changes_made:
            if change['id'] == change_id and change['applied']:
                try:
                    with open(change['file'], 'r') as f:
                        lines = f.readlines()
                    
                    lines[change['line'] - 1] = change['original']
                    
                    with open(change['file'], 'w') as f:
                        f.writelines(lines)
                    
                    change['applied'] = False
                    click.echo(f"[INFO] Reverted change {change_id}: {change['reason']}")
                    return True
                except Exception as e:
                    click.echo(f"[ERROR] Failed to revert change {change_id}: {e}")
                    return False
        return False
    
    def revert_file_changes(self, file_path: str) -> int:
        """Revert all changes made to a specific file."""
        reverted_count = 0
        for change in self.changes_made:
            if change['file'] == file_path and change['applied']:
                if self.revert_change(change['id']):
                    reverted_count += 1
        return reverted_count
    
    def get_applied_changes(self) -> List[Dict]:
        """Get all currently applied changes."""
        return [change for change in self.changes_made if change['applied']]
    
    def display_changes(self):
        """Display all applied changes in a user-friendly format."""
        applied_changes = self.get_applied_changes()
        
        if not applied_changes:
            click.echo("\n[INFO] No changes have been applied.")
            return
        
        click.echo("\n" + "="*80)
        click.echo("APPLIED CHANGES SUMMARY")
        click.echo("="*80)
        
        # Group changes by file
        file_changes = {}
        for change in applied_changes:
            if change['file'] not in file_changes:
                file_changes[change['file']] = []
            file_changes[change['file']].append(change)
        
        for file_path, changes in file_changes.items():
            click.echo(f"\n📁 {file_path}")
            for change in changes:
                click.echo(f"  [{change['id']}] Line {change['line']}: {change['reason']}")
                click.echo(f"      Original: {change['original'].strip()}")
                click.echo(f"      New:      {change['new'].strip()}")
    
    def interactive_revert_prompt(self) -> str:
        """Interactive prompt for users to select changes to revert."""
        applied_changes = self.get_applied_changes()
        
        if not applied_changes:
            return "No changes to revert."
        
        self.display_changes()
        
        click.echo("\n" + "="*80)
        click.echo("CHANGE REVERSION OPTIONS")
        click.echo("="*80)
        click.echo("You can revert specific changes using the following options:")
        click.echo("• Enter change ID (e.g., '1') to revert a specific change")
        click.echo("• Enter 'file:filename' to revert all changes in a file (e.g., 'file:src/main.py')")
        click.echo("• Enter 'all' to revert all changes")
        click.echo("• Enter 'none' to keep all changes")
        click.echo("• Enter multiple IDs separated by commas (e.g., '1,3,5')")
        
        while True:
            try:
                choice = click.prompt("\nEnter your choice", type=str, default="none").strip().lower()
                
                if choice == "none":
                    return "All changes kept."
                
                elif choice == "all":
                    for change in applied_changes:
                        self.revert_change(change['id'])
                    return "All changes reverted."
                
                elif choice.startswith("file:"):
                    file_path = choice[5:]  # Remove "file:" prefix
                    reverted_count = self.revert_file_changes(file_path)
                    return f"Reverted {reverted_count} changes in {file_path}."
                
                else:
                    # Handle multiple IDs or single ID
                    ids = [id.strip() for id in choice.split(",")]
                    reverted_count = 0
                    
                    for id_str in ids:
                        try:
                            change_id = int(id_str)
                            if self.revert_change(change_id):
                                reverted_count += 1
                        except ValueError:
                            click.echo(f"[ERROR] Invalid change ID: {id_str}")
                    
                    if reverted_count > 0:
                        return f"Reverted {reverted_count} changes."
                    else:
                        click.echo("[ERROR] No valid changes were reverted. Please try again.")
                        continue
                        
            except click.Abort:
                return "Operation cancelled by user."
    
    def generate_review_summary(self, original_review: str) -> str:
        """Generate an updated review summary with information about reverted changes."""
        applied_changes = self.get_applied_changes()
        reverted_changes = [change for change in self.changes_made if not change['applied']]
        
        summary = original_review
        
        if reverted_changes:
            summary += "\n\n" + "="*80
            summary += "\nREVERTED CHANGES"
            summary += "\n" + "="*80
            summary += "\nThe following changes were reverted by the user:\n"
            
            for change in reverted_changes:
                summary += f"\n• {change['file']}:{change['line']} - {change['reason']}"
                summary += f"\n  Original: {change['original'].strip()}"
                summary += f"\n  Reverted: {change['new'].strip()}"
        
        if applied_changes:
            summary += "\n\n" + "="*80
            summary += "\nAPPLIED CHANGES"
            summary += "\n" + "="*80
            summary += f"\n{len(applied_changes)} changes were applied:\n"
            
            for change in applied_changes:
                summary += f"\n• {change['file']}:{change['line']} - {change['reason']}"
        
        return summary


def parse_llm_suggestions(llm_response: str) -> List[Dict]:
    """Parse LLM response to extract actionable suggestions."""
    suggestions = []
    
    # Common patterns for LLM suggestions
    patterns = [
        r'(?:suggest|recommend|should|need to|consider).*?(?:change|modify|update|fix|add|remove)',
        r'(?:line \d+).*?(?:should|needs to|must)',
        r'(?:file:.*?)(?:line \d+).*?(?:change|modify)',
    ]
    
    lines = llm_response.split('\n')
    for i, line in enumerate(lines):
        line = line.strip()
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in patterns):
            suggestions.append({
                'line_number': i + 1,
                'content': line,
                'type': 'suggestion'
            })
    
    return suggestions


def extract_file_and_line_info(text: str) -> List[Tuple[str, int, str]]:
    """Extract file paths and line numbers from text."""
    # Pattern to match file paths and line numbers
    patterns = [
        r'([^\s]+):(\d+):?\s*(.+)',  # filename:line: description
        r'([^\s]+)\((\d+)\):\s*(.+)',  # filename(line): description
        r'line (\d+) in ([^\s]+):\s*(.+)',  # line X in filename: description
    ]
    
    results = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            if len(match) == 3:
                if match[0].isdigit():  # line X in filename format
                    line_num = int(match[0])
                    file_path = match[1]
                    description = match[2]
                else:  # filename:line format
                    file_path = match[0]
                    line_num = int(match[1])
                    description = match[2]
                
                results.append((file_path, line_num, description))
    
    return results 