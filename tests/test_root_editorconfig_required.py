"""root-editorconfig-required hook tests."""

import contextlib
import io
import os
import tempfile

import pytest

from hooks.root_editorconfig_required import check_root_editorconfig


@pytest.mark.parametrize(
    "quiet",
    (True, False),
    ids=("quiet=True", "quiet=False"),
)
@pytest.mark.parametrize(
    "create_file",
    (True, False),
    ids=("create_file=True", "create_file=False"),
)
@pytest.mark.parametrize(
    ("input_content", "expected_stderr", "expected_exitcode"),
    (
        pytest.param(
            """# EditorConfig is awesome: https://EditorConfig.org

root = true

[*]
end_of_line = lf
insert_final_newline = true

[*.{js,py}]
charset = utf-8
""",
            None,
            0,
            id="root=true",
        ),
        pytest.param(
            """root = false

[*]
end_of_line = lf
insert_final_newline = true

[*.{js,py}]
charset = utf-8
""",
            (
                "Found 'root = false' in .editorconfig when expected to"
                " find 'root = true'.\n"
            ),
            1,
            id="root=false",
        ),
        pytest.param(
            """root = invalid

[*]
end_of_line = lf
insert_final_newline = true

[*.{js,py}]
charset = utf-8
""",
            (
                "Invalid 'root' directive value 'invalid' at"
                " '.editorconfig:1'. Possible values are 'true' and 'false'.\n"
            ),
            1,
            id="root=invalid",
        ),
        pytest.param(
            """root = true
root = false

[*]
end_of_line = lf
insert_final_newline = true

[*.{js,py}]
charset = utf-8
""",
            (
                "Found 'root = false' in .editorconfig when expected to"
                " find 'root = true'.\n"
            ),
            1,
            id="root=true-root=false",
        ),
        pytest.param(
            """root = true
root = true

[*]
end_of_line = lf
insert_final_newline = true

[*.{js,py}]
charset = utf-8
""",
            "Found multiple definitions of 'root = true' in .editorconfig\n",
            1,
            id="root=true-root=true",
        ),
        pytest.param(
            """[*]
root = true
end_of_line = lf
insert_final_newline = true

[*.{js,py}]
charset = utf-8
""",
            "Directive 'root = true' not found before section headers.\n",
            1,
            id="[*]root=true",
        ),
    ),
)
def test_root_editorconfig_required(
    input_content,
    expected_stderr,
    expected_exitcode,
    create_file,
    quiet,
):
    if expected_stderr is None:
        expected_stderr = ""

    previous_cwd = os.getcwd()

    with tempfile.TemporaryDirectory() as dirpath:
        try:
            os.chdir(dirpath)

            if create_file:
                with open(os.path.join(dirpath, ".editorconfig"), "w") as f:
                    f.write(input_content)
            else:
                expected_exitcode = 1
                expected_stderr = "Missing '.editorconfig' file\n"

            if quiet:
                expected_stderr = ""

            stderr = io.StringIO()
            with contextlib.redirect_stderr(stderr):
                exitcode = check_root_editorconfig(quiet=quiet)

            assert exitcode == expected_exitcode
            assert stderr.getvalue() == expected_stderr

        finally:
            os.chdir(previous_cwd)
