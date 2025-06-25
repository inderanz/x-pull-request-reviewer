# Interactive Change Management Example

This example demonstrates how the x-pull-request-reviewer's interactive change management feature works in real-world scenarios.

## Scenario: Code Review with Multiple Suggestions

Imagine you're reviewing a Python application and the agent suggests several changes:

### 1. Initial Review

The agent reviews your code and provides suggestions like:

```
📝 ACTIONABLE CHANGES (3):
  [1] src/main.py:15: Add input validation for user_id parameter
      Reason: Security vulnerability - missing input validation
      Current: user_id = request.args.get('user_id')

  [2] src/utils.py:23: Consider using a more descriptive variable name
      Reason: Code readability - variable name is too generic
      Current: data = process_data(input_data)

  [3] src/database.py:45: Add error handling for database connection
      Reason: Robustness - missing exception handling
      Current: connection = db.connect()
```

### 2. Interactive Change Application

The system prompts you to choose which changes to apply:

```
CHANGE APPLICATION OPTIONS
--------------------------------------------------------------------------------
You can apply specific changes using the following options:
• Enter suggestion ID (e.g., '1') to apply a specific change
• Enter 'all' to apply all suggested changes
• Enter 'none' to skip all changes
• Enter multiple IDs separated by commas (e.g., '1,3,5')

Enter your choice: 1,3
```

You choose to apply changes 1 and 3 (security fix and error handling), but skip change 2 (variable naming).

### 3. Change Reversion

After applying changes, you can revert specific ones if needed:

```
APPLIED CHANGES SUMMARY
================================================================================

📁 src/main.py
  [1] Line 15: Add input validation for user_id parameter
      Original: user_id = request.args.get('user_id')
      New:      # TODO: Add input validation for user_id parameter
                user_id = request.args.get('user_id')

📁 src/database.py
  [2] Line 45: Add error handling for database connection
      Original: connection = db.connect()
      New:      # TODO: Add error handling for database connection
                connection = db.connect()

CHANGE REVERSION OPTIONS
--------------------------------------------------------------------------------
You can revert specific changes using the following options:
• Enter change ID (e.g., '1') to revert a specific change
• Enter 'file:filename' to revert all changes in a file (e.g., 'file:src/main.py')
• Enter 'all' to revert all changes
• Enter 'none' to keep all changes
• Enter multiple IDs separated by commas (e.g., '1,3,5')

Enter your choice: 2
```

You decide to revert the database change (ID 2) but keep the input validation change.

### 4. Final Review Summary

The system generates an updated review summary:

```
================================================================================
REVERTED CHANGES
================================================================================
The following changes were reverted by the user:

• src/database.py:45 - Add error handling for database connection
  Original: connection = db.connect()
  Reverted: # TODO: Add error handling for database connection
            connection = db.connect()

================================================================================
APPLIED CHANGES
================================================================================
1 changes were applied:

• src/main.py:15 - Add input validation for user_id parameter
```

## Real-World Use Cases

### Use Case 1: Security vs. Functionality Trade-off

**Scenario**: The agent suggests adding comprehensive input validation that might break existing functionality.

**User Decision**: Apply only critical security fixes, skip validation that might affect user experience.

**Commands**:
```bash
# Apply only security-related changes
Enter your choice: 1,4,7

# Later revert if it causes issues
Enter your choice: 4
```

### Use Case 2: Team Coding Standards

**Scenario**: The agent suggests style changes that don't match your team's conventions.

**User Decision**: Skip style suggestions, apply only functional improvements.

**Commands**:
```bash
# Skip all style-related changes
Enter your choice: none

# Or apply only specific functional changes
Enter your choice: 2,5,8
```

### Use Case 3: Experimental Features

**Scenario**: The agent suggests adding new features that you want to test.

**User Decision**: Apply changes to a specific file for testing.

**Commands**:
```bash
# Apply all changes in a specific file
Enter your choice: file:src/experimental.py

# Revert if the experiment doesn't work
Enter your choice: file:src/experimental.py
```

### Use Case 4: CI/CD Integration

**Scenario**: Running in automated environment where no user interaction is possible.

**Commands**:
```bash
# Disable interactive mode for CI/CD
python xprr_agent.py review --repo ./my-project --branch feature-branch --no-interactive
```

## Advanced Features

### Batch Operations

You can perform batch operations on changes:

```bash
# Apply all security-related changes
Enter your choice: 1,3,5,7

# Revert all changes in a problematic file
Enter your choice: file:src/legacy_module.py

# Apply changes to multiple specific files
Enter your choice: file:src/core.py,file:src/utils.py
```

### Change Tracking

The system tracks all changes with unique IDs:

- **Change ID**: Unique identifier for each applied change
- **File Path**: Which file was modified
- **Line Number**: Specific line that was changed
- **Reason**: Why the change was suggested
- **Original/New**: Before and after content

### Safety Features

- **Backup**: Original files are backed up before changes
- **Validation**: Line numbers are validated before applying changes
- **Rollback**: All changes can be reverted individually or in batches
- **Error Handling**: Graceful handling of file system errors

## Integration with GitHub

When used with GitHub PR integration, the final review summary includes:

1. **Original LLM Review**: The complete AI-generated review
2. **Applied Changes**: What was actually implemented
3. **Reverted Changes**: What was rejected and why
4. **User Decisions**: Summary of user choices

This provides transparency to the team about what changes were accepted vs. rejected.

## Best Practices

1. **Review Before Applying**: Always review suggestions before applying them
2. **Test After Changes**: Run tests after applying changes to ensure nothing breaks
3. **Use Batch Operations**: Group related changes for easier management
4. **Document Decisions**: The system automatically documents your choices
5. **Iterative Approach**: Apply changes incrementally and test frequently

## Troubleshooting

### Common Issues

1. **Invalid Line Numbers**: The system validates line numbers before applying changes
2. **File Not Found**: Changes are only applied to existing files
3. **Permission Errors**: Ensure write permissions for the repository
4. **Git Conflicts**: Resolve any git conflicts before applying changes

### Recovery Options

- **Revert All**: Use `all` to revert all applied changes
- **File-Level Revert**: Use `file:path` to revert all changes in a file
- **Manual Recovery**: Original files are backed up in the change manager 