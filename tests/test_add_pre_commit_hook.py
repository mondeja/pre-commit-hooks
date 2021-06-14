"""Tests for 'add-pre-commit-hook' hook."""

import contextlib
import io
import os
import tempfile

import pytest

from hooks.add_pre_commit_hook import add_pre_commit_hook


@pytest.mark.parametrize("quiet", (False, True), ids=("quiet=False", "quiet=True"))
@pytest.mark.parametrize(
    "dry_run", (False, True), ids=("dry_run=False", "dry_run=True")
)
@pytest.mark.parametrize(
    ("repo", "rev", "hook_id", "input_content", "expected_result", "expected_exitcode"),
    (
        pytest.param(
            "https://github.com/mondeja/pre-commit-hooks",
            "v1.0.0",
            "dev-extras-required",
            """repos:
  - repo: https://github.com/asottile/setup-cfg-fmt
    rev: v1.17.0
    hooks:
      - id: setup-cfg-fmt
""",
            """repos:
  - repo: https://github.com/asottile/setup-cfg-fmt
    rev: v1.17.0
    hooks:
      - id: setup-cfg-fmt
  - repo: https://github.com/mondeja/pre-commit-hooks
    rev: v1.0.0
    hooks:
      - id: dev-extras-required
""",
            1,
            id="add-repo",
        ),
        pytest.param(
            "https://github.com/mondeja/pre-commit-hooks",
            "v1.0.0",
            "dev-extras-required",
            """repos:
  - repo: https://github.com/mondeja/pre-commit-hooks
    rev: v1.0.0
    hooks:
      - id: wavelint
""",
            """repos:
  - repo: https://github.com/mondeja/pre-commit-hooks
    rev: v1.0.0
    hooks:
      - id: wavelint
      - id: dev-extras-required
""",
            1,
            id="add-hook",
        ),
        pytest.param(
            "https://github.com/mondeja/pre-commit-hooks",
            "v1.0.0",
            "dev-extras-required",
            """repos:
  - repo: https://github.com/mondeja/pre-commit-hooks
    rev: v1.0.0
    hooks:
      - id: dev-extras-required
""",
            """repos:
  - repo: https://github.com/mondeja/pre-commit-hooks
    rev: v1.0.0
    hooks:
      - id: dev-extras-required
""",
            0,
            id="add-hook",
        ),
    ),
)
def test_add_pre_commit_hook(
    repo,
    rev,
    hook_id,
    input_content,
    expected_result,
    expected_exitcode,
    quiet,
    dry_run,
):
    previous_cwd = os.getcwd()

    with tempfile.TemporaryDirectory() as dirname:
        filepath = os.path.join(dirname, ".pre-commit-config.yaml")
        if os.path.isfile(filepath):
            os.remove(filepath)

        with open(filepath, "w") as f:
            f.write(input_content)

        os.chdir(dirname)

        stderr = io.StringIO()

        with contextlib.redirect_stderr(stderr):
            exitcode = add_pre_commit_hook(
                repo,
                rev,
                hook_id,
                quiet=quiet,
                dry_run=dry_run,
            )

        assert exitcode == expected_exitcode

        if not dry_run:
            with open(filepath) as f:
                assert f.read() == expected_result

    os.chdir(previous_cwd)
