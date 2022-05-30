import contextlib
import io
import tempfile

import pytest

from hooks.file_check_lines import file_check_lines, smart_quoted


@pytest.mark.parametrize(
    "quiet",
    (True, False),
    ids=("quiet=True", "quiet=False"),
)
@pytest.mark.parametrize(
    ("content", "lines", "expected_exitcode", "expected_missing_lines"),
    (
        pytest.param("foo\nbar\nbaz\n", ["foo", "bar"], 0, [], id="ok"),
        pytest.param("foo\n\n\n", ["bar", "baz"], 1, ["bar", "baz"], id="fail"),
        pytest.param(
            "foo\n\n\r\n\r\n\n", ["\r\n", "\n", "baz"], 1, ["baz"], id="ignore-newlines"
        ),
        pytest.param(
            "foo\n\n\n", ["\r\n", "\n", "baz"], 1, ["baz"], id="ignore-empty-lines"
        ),
    ),
)
def test_file_check_lines(
    quiet, content, lines, expected_exitcode, expected_missing_lines
):
    stderr = io.StringIO()
    with tempfile.NamedTemporaryFile() as f:
        f.write(content.encode("utf-8"))
        f.seek(0)

        with contextlib.redirect_stderr(stderr):
            exitcode = file_check_lines(f.name, lines, quiet=quiet)

        assert exitcode == expected_exitcode

        if quiet:
            assert not stderr.getvalue()
        else:
            stderr_lines = stderr.getvalue().splitlines()
            for expected_missing_line in expected_missing_lines:
                assert (
                    f"Line {smart_quoted(expected_missing_line)} not"
                    f" found in file {f.name}"
                ) in stderr_lines
