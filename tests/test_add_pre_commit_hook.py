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
    (
        "repo",
        "rev",
        "hook_id",
        "input_content",
        "expected_result",
        "expected_exitcode",
        "expected_stderr",
    ),
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
            None,
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
            None,
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
            None,
            id="dont-add-hook",
        ),
        pytest.param(
            "https://github.com/mondeja/pre-commit-hooks",
            "v1.1.2",
            "foo-hook-id",
            r"""repos:
  - repo: https://github.com/mondeja/pre-commit-hooks
    rev: v1.0.0
    hooks:
      - id: dev-extras-required
  - repo: https://github.com/mondeja/pre-commit-hooks
    rev: v1.1.2
    hooks:
      - id: dev-extras-required
""",
            None,
            1,
            (
                "Multiple definitions of repository"
                " 'https://github.com/mondeja/pre-commit-hooks' in"
                " configuration file '.pre-commit-config.yaml'."
                " You must determine manually one of them.\n"
            ),
            id="multiple-definitions",
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
    expected_stderr,
    quiet,
    dry_run,
):
    try:
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

            if expected_stderr is not None:
                assert stderr.getvalue() == expected_stderr
            else:

                if not dry_run:
                    with open(filepath) as f:
                        assert f.read() == expected_result
    finally:
        os.chdir(previous_cwd)
