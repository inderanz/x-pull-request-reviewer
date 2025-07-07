import pytest
from unittest.mock import patch, MagicMock
from src.agent import main
import os

@patch('src.agent.main.get_latest_commit_sha', return_value='dummysha')
@patch('src.agent.main.git_utils')
@patch('src.agent.main.analyze_directory')
@patch('src.agent.main.build_enhanced_review_prompt')
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

def test_map_llm_comments_to_lines_modes():
    from src.agent.diff_utils import map_llm_comments_to_lines
    diff = (
        'diff --git a/foo.py b/foo.py\n'
        'index 0000000..1111111 100644\n'
        '--- a/foo.py\n'
        '+++ b/foo.py\n'
        '@@ -1,2 +1,4 @@\n'
        '-print("bar")\n'
        '+print("foo")\n'
        '+print("baz")\n'
        '+print("qux")\n'
    )
    # LLM comments: (file, line, comment)
    comments = [('foo.py', 2, 'Good change'), (None, 3, 'Another line'), ('foo.py', 2, 3, 'Multi-line comment')]
    # added mode
    mapped = map_llm_comments_to_lines(comments, diff, filter_mode='added')
    assert any(m[1] == 2 for m in mapped), 'added mode should map to added lines'
    # diff_context mode
    mapped = map_llm_comments_to_lines(comments, diff, filter_mode='diff_context', context_lines=1)
    assert any(m[1] == 2 or m[1] == 3 for m in mapped), 'diff_context should allow context lines'
    # file mode
    mapped = map_llm_comments_to_lines(comments, diff, filter_mode='file')
    assert all(m[0] == 'foo.py' for m in mapped if m[0]), 'file mode should allow any line in file'
    # nofilter mode
    mapped = map_llm_comments_to_lines(comments, diff, filter_mode='nofilter')
    assert any(m[0] == 'foo.py' for m in mapped), 'nofilter should allow any file/line'
    # multi-line
    multi = [c for c in mapped if isinstance(c[1], int) and c[1] == 2]
    assert multi, 'multi-line comment should be mapped' 