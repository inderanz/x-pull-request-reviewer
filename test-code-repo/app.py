#!/usr/bin/env python3
"""
Test Python file with multiple issues for XPRR testing.
This file contains intentional security vulnerabilities and code quality issues.
"""

import os
import sys
import subprocess
import eval  # Security issue: importing eval

def main():
    """Main function with multiple issues."""
    # Security issue: hardcoded password
    password = "admin123"
    
    # Security issue: using eval
    result = eval("2 + 2")
    
    # Security issue: command injection
    user_input = "ls -la"
    os.system(user_input)  # Security vulnerability
    
    # Security issue: subprocess with shell=True
    subprocess.run(f"echo {user_input}", shell=True)
    
    # Code quality issue: unused import
    import json  # Unused import
    
    # Code quality issue: magic number
    timeout = 30  # Magic number without explanation
    
    # Code quality issue: long line
    very_long_variable_name_that_exceeds_the_maximum_line_length_and_should_be_reported_by_flake8 = "this is a very long string that makes the line too long"
    
    # Code quality issue: missing docstring
    def helper_function():
        return "helper"
    
    # Code quality issue: inconsistent indentation
    if True:
        print("correct")
      print("incorrect")  # Wrong indentation
    
    return result

if __name__ == "__main__":
    main() # Test change
