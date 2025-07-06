#!/bin/bash

# Test shell script with multiple issues for XPRR testing
# This file contains intentional security vulnerabilities and best practice violations

# Security issue: running as root without checks
sudo apt-get update

# Security issue: command injection
user_input="ls -la"
eval $user_input

# Security issue: downloading and executing scripts
curl https://example.com/script.sh | sh

# Security issue: hardcoded credentials
password="admin123"
echo "Password: $password"

# Code quality issue: missing quotes around variables
echo $password

# Code quality issue: unused variable
unused_var="this is unused"

# Code quality issue: inconsistent indentation
if [ -f "file.txt" ]; then
echo "file exists"
  echo "wrong indentation"
fi

# Code quality issue: missing error handling
rm -rf /tmp/important_file

# Code quality issue: long line
very_long_command_with_many_arguments_that_exceeds_the_maximum_line_length_and_should_be_reported_by_shellcheck="this is a very long command that should be reported"

echo "Script completed" 