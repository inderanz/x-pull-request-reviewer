import pytest
from unittest.mock import patch, MagicMock
from src.agent import main
import os

@patch('src.agent.main.get_latest_commit_sha', return_value='dummysha')
@patch('src.agent.main.git_utils')
@patch('src.agent.main.analyze_directory')
@patch('src.agent.main.build_review_prompt')
@patch('src.agent.main.query_llm_for_review')
@patch('src.agent.main.post_pr_comment')
@patch('src.agent.main.post_line_comment')
def test_review_pr_or_branch_full_workflow(mock_line_comment, mock_pr_comment, mock_llm, mock_prompt, mock_analyze, mock_git, mock_commit_sha):
    # Setup mocks
    mock_git.clone_repo.return_value = None
    mock_git.fetch_branch.return_value = None
    mock_git.checkout_branch.return_value = None
    # Use a valid, multi-line unified diff
    diff = (
        'diff --git a/foo.py b/foo.py\n'
        'index 0000000..1111111 100644\n'
        '--- a/foo.py\n'
        '+++ b/foo.py\n'
        '@@ -1,2 +1,2 @@\n'
        '-print("bar")\n'
        '+print("foo")\n'
    )
    mock_git.get_diff.return_value = diff
    mock_analyze.return_value = {'foo.py': {'format': 'ok', 'lint': 'ok'}}
    mock_prompt.return_value = 'prompt'
    mock_llm.return_value = ([('foo.py', 1, 'Good change')], 'Summary: Good changes')
    mock_pr_comment.return_value = '[INFO] Comment posted.'
    mock_line_comment.return_value = '[INFO] Line comment posted.'

    # Patch environment to include GITHUB_TOKEN
    with patch.dict(os.environ, {"GITHUB_TOKEN": "dummy"}):
        main.review_pr_or_branch(
            repo_url='https://github.com/org/repo.git',
            branch='feature',
            pr_number=1,
            repo_slug='org/repo'
        )
        # Assert calls
        assert mock_git.clone_repo.called
        assert mock_git.fetch_branch.called
        assert mock_git.checkout_branch.called
        assert mock_git.get_diff.called
        assert mock_analyze.called
        assert mock_prompt.called
        assert mock_llm.called
        assert mock_pr_comment.called
        mock_line_comment.assert_called()

@patch('src.agent.main.git_utils')
def test_review_pr_or_branch_missing_repo(mock_git):
    # Should print error and return
    with patch('click.echo') as mock_echo:
        main.review_pr_or_branch()
        mock_echo.assert_any_call('Either repo_url or repo_path must be provided.') 