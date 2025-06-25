import pytest
import tempfile
import os
from agent.change_manager import ChangeManager


class TestChangeManager:
    """Test cases for the ChangeManager class."""
    
    def setup_method(self):
        """Set up test environment."""
        self.temp_dir = tempfile.mkdtemp()
        self.change_manager = ChangeManager(self.temp_dir)
        
        # Create a test file
        self.test_file = os.path.join(self.temp_dir, "test.py")
        with open(self.test_file, 'w') as f:
            f.write("def hello():\n")
            f.write("    print('Hello, World!')\n")
            f.write("    return True\n")
    
    def teardown_method(self):
        """Clean up test environment."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_apply_change(self):
        """Test applying a change to a file."""
        # Apply a change to line 2
        change_id = self.change_manager.apply_change(
            self.test_file, 2, "    print('Hello, Updated World!')", "Update greeting message"
        )
        
        assert change_id == 1
        
        # Verify the change was applied
        with open(self.test_file, 'r') as f:
            lines = f.readlines()
        
        assert "print('Hello, Updated World!')" in lines[1]
        
        # Verify change tracking
        applied_changes = self.change_manager.get_applied_changes()
        assert len(applied_changes) == 1
        assert applied_changes[0]['id'] == 1
        assert applied_changes[0]['reason'] == "Update greeting message"
    
    def test_revert_change(self):
        """Test reverting a change."""
        # Apply a change
        change_id = self.change_manager.apply_change(
            self.test_file, 2, "    print('Modified')", "Test modification"
        )
        
        # Verify change was applied
        with open(self.test_file, 'r') as f:
            lines = f.readlines()
        assert "print('Modified')" in lines[1]
        
        # Revert the change
        success = self.change_manager.revert_change(change_id)
        assert success
        
        # Verify change was reverted
        with open(self.test_file, 'r') as f:
            lines = f.readlines()
        assert "print('Hello, World!')" in lines[1]
        
        # Verify no applied changes remain
        applied_changes = self.change_manager.get_applied_changes()
        assert len(applied_changes) == 0
    
    def test_revert_file_changes(self):
        """Test reverting all changes in a file."""
        # Apply multiple changes
        self.change_manager.apply_change(
            self.test_file, 2, "    print('Change 1')", "First change"
        )
        self.change_manager.apply_change(
            self.test_file, 3, "    return False", "Second change"
        )
        
        # Verify changes were applied
        applied_changes = self.change_manager.get_applied_changes()
        assert len(applied_changes) == 2
        
        # Revert all changes in the file
        reverted_count = self.change_manager.revert_file_changes(self.test_file)
        assert reverted_count == 2
        
        # Verify all changes were reverted
        applied_changes = self.change_manager.get_applied_changes()
        assert len(applied_changes) == 0
    
    def test_invalid_line_number(self):
        """Test applying change to invalid line number."""
        change_id = self.change_manager.apply_change(
            self.test_file, 999, "invalid line", "Invalid change"
        )
        
        assert change_id == -1
        
        # Verify no changes were applied
        applied_changes = self.change_manager.get_applied_changes()
        assert len(applied_changes) == 0
    
    def test_revert_nonexistent_change(self):
        """Test reverting a change that doesn't exist."""
        success = self.change_manager.revert_change(999)
        assert not success
    
    def test_generate_review_summary(self):
        """Test generating review summary with changes."""
        # Apply some changes
        self.change_manager.apply_change(
            self.test_file, 2, "    print('Modified')", "Update greeting"
        )
        
        # Revert one change
        self.change_manager.revert_change(1)
        
        # Apply another change
        self.change_manager.apply_change(
            self.test_file, 3, "    return 'success'", "Update return value"
        )
        
        original_review = "This is the original review."
        summary = self.change_manager.generate_review_summary(original_review)
        
        assert "REVERTED CHANGES" in summary
        assert "APPLIED CHANGES" in summary
        assert "Update greeting" in summary
        assert "Update return value" in summary


class TestSuggestionParser:
    """Test cases for suggestion parsing functionality."""
    
    def test_parse_file_suggestions(self):
        """Test parsing file-based suggestions from LLM response."""
        from agent.suggestion_parser import parse_suggestions_from_llm
        
        llm_response = """Here are my suggestions:
file:src/main.py:15: Add input validation for user_id parameter
file:src/utils.py:23: Consider using a more descriptive variable name"""
        
        suggestions = parse_suggestions_from_llm(llm_response, "")
        
        assert len(suggestions) == 2
        assert suggestions[0]['type'] == 'file_change'
        assert suggestions[0]['file_path'] == 'src/main.py'
        assert suggestions[0]['line_number'] == 15
        assert "Add input validation" in suggestions[0]['reason']
    
    def test_parse_line_suggestions(self):
        """Test parsing line-based suggestions."""
        from agent.suggestion_parser import parse_suggestions_from_llm
        
        llm_response = """Suggestions:
line 23: Consider using a more descriptive variable name
line 45: Add error handling for database connection"""
        
        suggestions = parse_suggestions_from_llm(llm_response, "")
        
        # Since we don't have diff context, these will be parsed as general suggestions
        assert len(suggestions) == 2
        assert suggestions[0]['type'] == 'general'
        assert "descriptive variable name" in suggestions[0]['reason']
    
    def test_parse_general_suggestions(self):
        """Test parsing general suggestions."""
        from agent.suggestion_parser import parse_suggestions_from_llm
        
        llm_response = """General recommendations:
suggestion: Add comprehensive error handling
recommendation: Consider adding unit tests"""
        
        suggestions = parse_suggestions_from_llm(llm_response, "")
        
        assert len(suggestions) == 2
        assert suggestions[0]['type'] == 'general'
        assert "comprehensive error handling" in suggestions[0]['reason']
    
    def test_deduplicate_suggestions(self):
        """Test that duplicate suggestions are removed."""
        from agent.suggestion_parser import parse_suggestions_from_llm
        
        llm_response = """Suggestions:
file:src/main.py:15: Add input validation
file:src/main.py:15: Add input validation
suggestion: Add error handling
suggestion: Add error handling"""
        
        suggestions = parse_suggestions_from_llm(llm_response, "")
        
        # Should have only 2 unique suggestions
        assert len(suggestions) == 2
        
        # Check that we have one file change and one general suggestion
        types = [s['type'] for s in suggestions]
        assert 'file_change' in types
        assert 'general' in types


if __name__ == "__main__":
    pytest.main([__file__]) 