#!/usr/bin/env python3
"""
Test script for enhanced line mapping functionality
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.diff_utils import (
    parse_unified_diff_with_context,
    create_line_numbered_diff,
    map_llm_comments_to_lines,
    extract_line_references_from_comment
)

def test_diff_parsing():
    """Test the enhanced diff parsing functionality"""
    print("=== Testing Enhanced Diff Parsing ===")
    
    # Sample diff
    sample_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -10,7 +10,8 @@ def main():
     password = "hardcoded_password"  # Line 10
     api_key = "secret_key_123"       # Line 11
     
-    result = query_database(password)  # Line 12
+    # Use environment variables instead
+    result = query_database(os.getenv("DB_PASSWORD"))  # Line 13
     
     return result
"""
    
    print("Original diff:")
    print(sample_diff)
    print()
    
    # Test enhanced parsing
    parsed = parse_unified_diff_with_context(sample_diff)
    print("Enhanced parsing result:")
    for item in parsed:
        print(f"  File: {item['file']}, Line: {item['line_number']}, Type: {item['type']}")
        print(f"  Content: {item['content']}")
        print()
    
    # Test line-numbered diff
    numbered = create_line_numbered_diff(sample_diff)
    print("Line-numbered diff:")
    print(numbered)
    print()

def test_line_mapping():
    """Test the intelligent line mapping functionality"""
    print("=== Testing Intelligent Line Mapping ===")
    
    # Sample diff
    sample_diff = """diff --git a/test.py b/test.py
index 1234567..abcdefg 100644
--- a/test.py
+++ b/test.py
@@ -10,7 +10,8 @@ def main():
     password = "hardcoded_password"  # Line 10
     api_key = "secret_key_123"       # Line 11
     
-    result = query_database(password)  # Line 12
+    # Use environment variables instead
+    result = query_database(os.getenv("DB_PASSWORD"))  # Line 13
     
     return result
"""
    
    # Sample LLM comments with various line number formats
    llm_comments = [
        (None, 10, "Hardcoded password detected - use environment variables"),
        (None, 11, "Hardcoded API key found - move to environment variables"),
        (None, 13, "Good change - using environment variables for database password"),
        (None, 999, "This line number is way off - should be mapped to closest match"),
        ("test.py", 10, "File-specific comment with correct line number"),
        (None, None, "Comment without line number - should be mapped to first line")
    ]
    
    print("LLM Comments:")
    for i, (file_path, line_num, comment) in enumerate(llm_comments):
        print(f"  {i+1}. File: {file_path}, Line: {line_num}, Comment: {comment}")
    print()
    
    # Test mapping
    mapped = map_llm_comments_to_lines(llm_comments, sample_diff)
    
    print("Mapped Comments:")
    for i, (file_path, line_num, comment) in enumerate(mapped):
        print(f"  {i+1}. File: {file_path}, Line: {line_num}, Comment: {comment}")
    print()

def test_line_reference_extraction():
    """Test extracting line references from comments"""
    print("=== Testing Line Reference Extraction ===")
    
    test_comments = [
        "Hardcoded password on line 15 - use environment variables",
        "SQL injection vulnerability at line 23",
        "test.py:45 - missing input validation",
        "Line 10 has a security issue",
        "No specific line reference in this comment"
    ]
    
    for comment in test_comments:
        references = extract_line_references_from_comment(comment)
        print(f"Comment: {comment}")
        print(f"References: {references}")
        print()

def main():
    """Run all tests"""
    print("Testing Enhanced Line Mapping Functionality")
    print("=" * 50)
    print()
    
    test_diff_parsing()
    test_line_mapping()
    test_line_reference_extraction()
    
    print("All tests completed!")

if __name__ == "__main__":
    main() 