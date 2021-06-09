"""Tests for 'dev-extras-required' hook."""

import contextlib
import io
import os
import tempfile

import pytest

from hooks.dev_extras_required import check_pyproject_toml, check_setup_cfg


@pytest.mark.parametrize(
    "filename",
    ("setup.cfg", "_setup.cfg"),
    ids=("filename=setup.cfg", "filename=setup.cfg"),
)
@pytest.mark.parametrize("quiet", (False, True), ids=("quiet=False", "quiet=True"))
@pytest.mark.parametrize(
    "dry_run", (False, True), ids=("dry_run=False", "dry_run=True")
)
@pytest.mark.parametrize(
    "dev_extra_name",
    ("dev", "development"),
    ids=("dev_extra_name=dev", "dev_extra_name=development"),
)
@pytest.mark.parametrize(
    (
        "input_content",
        "expected_result",
        "expected_exitcode",
        "expected_stderr_lines",
    ),
    (
        (
            pytest.param(
                """[metadata]
name = foo
version = 1.0.0
description = Foo bar baz
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/mondeja/pre-commit-hooks
author = Alvaro Mondejar
author_email = mondejar1994@gmail.com
license = BSD-3-Clause
license_file = LICENSE
classifiers = 
	License :: OSI Approved :: BSD License
	Programming Language :: Python
	Programming Language :: Python :: 3

[options]
packages = find:
python_requires = >=3.6.1

[options.packages.find]
exclude = 
	tests*

[options.entry_points]
console_scripts = 
	foo-hook = hooks.foo:main

[options.extras_require]
test = 
	pytest==6.2.0
	pytest-cov==2.12.1
	waves==0.2.4

[bdist_wheel]
universal = True
""",
                """[metadata]
name = foo
version = 1.0.0
description = Foo bar baz
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/mondeja/pre-commit-hooks
author = Alvaro Mondejar
author_email = mondejar1994@gmail.com
license = BSD-3-Clause
license_file = LICENSE
classifiers = 
	License :: OSI Approved :: BSD License
	Programming Language :: Python
	Programming Language :: Python :: 3

[options]
packages = find:
python_requires = >=3.6.1

[options.packages.find]
exclude = 
	tests*

[options.entry_points]
console_scripts = 
	foo-hook = hooks.foo:main

[options.extras_require]
test = 
	pytest==6.2.0
	pytest-cov==2.12.1
	waves==0.2.4
{dev_extra_name} = 
	pytest==6.2.0
	pytest-cov==2.12.1
	waves==0.2.4

[bdist_wheel]
universal = True

""",
                1,
                [
                    (
                        "Requirement 'pytest==6.2.0' would be added to"
                        " '{dev_extra_name}' extra group at '{filename}'"
                    ),
                    (
                        "Requirement 'pytest-cov==2.12.1' would be added to"
                        " '{dev_extra_name}' extra group at '{filename}'"
                    ),
                    (
                        "Requirement 'waves==0.2.4' would be added to"
                        " '{dev_extra_name}' extra group at '{filename}'"
                    ),
                ],
                id="tests[0] -> dev[2]",
            ),
            pytest.param(
                """[metadata]
name = foo
version = 1.0.0
description = Foo bar baz
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/mondeja/pre-commit-hooks
author = Alvaro Mondejar
author_email = mondejar1994@gmail.com
license = BSD-3-Clause
license_file = LICENSE
classifiers = 
	License :: OSI Approved :: BSD License
	Programming Language :: Python
	Programming Language :: Python :: 3

[options]
packages = find:
python_requires = >=3.6.1

[options.packages.find]
exclude = 
	tests*

[options.entry_points]
console_scripts = 
	foo-hook = hooks.foo:main

[options.extras_require]
test = 
	pytest==6.2.0
{dev_extra_name} =
	pytest-cov==2.12.1
	waves==0.2.4

[bdist_wheel]
universal = True
""",
                """[metadata]
name = foo
version = 1.0.0
description = Foo bar baz
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/mondeja/pre-commit-hooks
author = Alvaro Mondejar
author_email = mondejar1994@gmail.com
license = BSD-3-Clause
license_file = LICENSE
classifiers = 
	License :: OSI Approved :: BSD License
	Programming Language :: Python
	Programming Language :: Python :: 3

[options]
packages = find:
python_requires = >=3.6.1

[options.packages.find]
exclude = 
	tests*

[options.entry_points]
console_scripts = 
	foo-hook = hooks.foo:main

[options.extras_require]
test = 
	pytest==6.2.0
{dev_extra_name} = 
	pytest-cov==2.12.1
	waves==0.2.4
	pytest==6.2.0

[bdist_wheel]
universal = True

""",
                1,
                [
                    (
                        "Requirement 'pytest==6.2.0' would be added to"
                        " '{dev_extra_name}' extra group at '{filename}'"
                    ),
                ],
                id="tests -> dev",
            ),
            pytest.param(
                """[metadata]
name = foo
version = 1.0.0
description = Foo bar baz
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/mondeja/pre-commit-hooks
author = Alvaro Mondejar
author_email = mondejar1994@gmail.com
license = BSD-3-Clause
license_file = LICENSE
classifiers = 
	License :: OSI Approved :: BSD License
	Programming Language :: Python
	Programming Language :: Python :: 3

[options]
packages = find:
python_requires = >=3.6.1

[options.packages.find]
exclude = 
	tests*

[options.entry_points]
console_scripts = 
	foo-hook = hooks.foo:main

[options.extras_require]
test = 
	pytest==6.2.0
{dev_extra_name} =
	pytest-cov==2.12.1
	waves==0.2.4
	pytest==6.2.0

[bdist_wheel]
universal = True
""",
                """[metadata]
name = foo
version = 1.0.0
description = Foo bar baz
long_description = file: README.md
long_description_content_type = text/markdown
url = https://github.com/mondeja/pre-commit-hooks
author = Alvaro Mondejar
author_email = mondejar1994@gmail.com
license = BSD-3-Clause
license_file = LICENSE
classifiers = 
	License :: OSI Approved :: BSD License
	Programming Language :: Python
	Programming Language :: Python :: 3

[options]
packages = find:
python_requires = >=3.6.1

[options.packages.find]
exclude = 
	tests*

[options.entry_points]
console_scripts = 
	foo-hook = hooks.foo:main

[options.extras_require]
test = 
	pytest==6.2.0
{dev_extra_name} =
	pytest-cov==2.12.1
	waves==0.2.4
	pytest==6.2.0

[bdist_wheel]
universal = True
""",
                0,
                [],
                id="correct",
            ),
        )
    ),
)
def test_check_setup_cfg(
    input_content,
    expected_result,
    expected_exitcode,
    expected_stderr_lines,
    filename,
    dev_extra_name,
    dry_run,
    quiet,
):
    with tempfile.TemporaryDirectory() as dirname:
        filename = os.path.join(dirname, filename)

        with open(filename, "w") as f:
            f.write(input_content.replace("{dev_extra_name}", dev_extra_name))

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exitcode = check_setup_cfg(
                filename=filename,
                dev_extra_name=dev_extra_name,
                quiet=quiet,
                dry_run=dry_run,
            )

        assert exitcode == expected_exitcode

        if dry_run:
            if not quiet:
                expected_stderr_lines = [
                    line.replace("{dev_extra_name}", dev_extra_name).replace(
                        "{filename}", filename
                    )
                    for line in expected_stderr_lines
                ]

                for line in stderr.getvalue().splitlines():
                    assert line in expected_stderr_lines
        else:
            with open(filename) as f:
                result = f.read()

            assert result == expected_result.replace("{dev_extra_name}", dev_extra_name)


@pytest.mark.parametrize(
    "filename",
    ("pyproject.toml", "_pyproject.toml"),
    ids=("filename=pyproject.toml", "filename=_pyproject.toml"),
)
@pytest.mark.parametrize("quiet", (False, True), ids=("quiet=False", "quiet=True"))
@pytest.mark.parametrize(
    "dev_extra_name",
    ("dev", "development"),
    ids=("dev_extra_name=dev", "dev_extra_name=development"),
)
@pytest.mark.parametrize(
    ("input_content", "expected_exitcode", "expected_stderr_lines"),
    (
        pytest.param(
            """[build-system]
requires = ["flit_core >=2,<4"]
build-backend = "flit_core.buildapi"

[tool.flit.metadata]
module = "furo"
requires-python = ">=3.6"
requires = [
  "beautifulsoup4",
  "sphinx ~= 3.0",
]
classifiers = [
  "Framework :: Sphinx",
  "Framework :: Sphinx :: Theme",
  "Programming Language :: Python :: 3",
]

[tool.flit.metadata.requires-extra]
test = [
  "pytest",
  "pytest-cov",
  "pytest-xdist",
]
doc = [
  "myst-parser",
  "sphinx-copybutton",
  "sphinx-inline-tabs",
  # Broken release. https://github.com/executablebooks/MyST-Parser/issues/343
  "docutils != 0.17",
]

[tool.flit.entrypoints]
"sphinx.html_themes" = {furo = "furo"}

[tool.flit.sdist]
include = [
  # Generated assets
  "src/furo/theme/furo/static/*/*",
]
exclude = [
  "docs/", "src/furo/assets",
  # JS stuff
  "gulpfile.js", "package.json", "package-lock.json",
  # Linting stuff
  ".flake8", ".isort.cfg", ".pre-commit-config.yaml",
]
""",
            1,
            [
                (
                    "Requirement 'pytest' would be added to"
                    " '{dev_extra_name}' extra group at '{filename}'"
                ),
                (
                    "Requirement 'pytest-cov' would be added to"
                    " '{dev_extra_name}' extra group at '{filename}'"
                ),
                (
                    "Requirement 'pytest-xdist' would be added to"
                    " '{dev_extra_name}' extra group at '{filename}'"
                ),
                (
                    "Requirement 'myst-parser' would be added to"
                    " '{dev_extra_name}' extra group at '{filename}'"
                ),
                (
                    "Requirement 'sphinx-copybutton' would be added to"
                    " '{dev_extra_name}' extra group at '{filename}'"
                ),
                (
                    "Requirement 'sphinx-inline-tabs' would be added to"
                    " '{dev_extra_name}' extra group at '{filename}'"
                ),
                (
                    "Requirement 'docutils != 0.17' would be added to"
                    " '{dev_extra_name}' extra group at '{filename}'"
                ),
            ],
            id="flit(test + doc -> dev)",
        ),
        pytest.param(
            """[build-system]
requires = ["flit_core >=2,<4"]
build-backend = "flit_core.buildapi"

[tool.flit.metadata]
module = "furo"
requires-python = ">=3.6"
requires = [
  "beautifulsoup4",
  "sphinx ~= 3.0",
]
classifiers = [
  "Framework :: Sphinx",
  "Framework :: Sphinx :: Theme",
  "Programming Language :: Python :: 3",
]

[tool.flit.metadata.requires-extra]
test = [
  "pytest",
  "pytest-cov",
  "pytest-xdist",
]
doc = [
  "myst-parser",
  "sphinx-copybutton",
  "sphinx-inline-tabs",
  # Broken release. https://github.com/executablebooks/MyST-Parser/issues/343
  "docutils != 0.17",
]
{dev_extra_name} = [
  "pytest",
  "pytest-cov",
  "pytest-xdist",
  "myst-parser",
  "sphinx-copybutton",
  "sphinx-inline-tabs",
  "docutils != 0.17",
]
""",
            0,
            [],
            id="flit(correct)",
        ),
        pytest.param(
            """[tool.poetry]
name = "awesome"

[tool.poetry.dependencies]
# These packages are mandatory and form the core of this package’s distribution.
mandatory = "^1.0"

# A list of all of the optional dependencies, some of which are included in the
# below `extras`. They can be opted into by apps.
psycopg2 = { version = "^2.7", optional = true }
mysqlclient = { version = "^1.3", optional = true }

[tool.poetry.extras]
mysql = ["mysqlclient"]
pgsql = ["psycopg2"]
""",
            1,
            [
                (
                    "Requirement 'mysqlclient' would be added to"
                    " '{dev_extra_name}' extra group at '{filename}'"
                ),
                (
                    "Requirement 'psycopg2' would be added to"
                    " '{dev_extra_name}' extra group at '{filename}'"
                ),
            ],
            id="poetry(mysql + pgsql -> dev)",
        ),
        pytest.param(
            """[tool.poetry]
name = "awesome"

[tool.poetry.dependencies]
# These packages are mandatory and form the core of this package’s distribution.
mandatory = "^1.0"

# A list of all of the optional dependencies, some of which are included in the
# below `extras`. They can be opted into by apps.
psycopg2 = { version = "^2.7", optional = true }
mysqlclient = { version = "^1.3", optional = true }

[tool.poetry.extras]
mysql = ["mysqlclient"]
pgsql = ["psycopg2"]
{dev_extra_name} = ["mysqlclient", "psycopg2"]
""",
            0,
            [],
            id="poetry(correct)",
        ),
    ),
)
def test_check_pyproject_toml(
    input_content,
    expected_exitcode,
    expected_stderr_lines,
    dev_extra_name,
    filename,
    quiet,
):
    with tempfile.TemporaryDirectory() as dirname:
        filename = os.path.join(dirname, filename)

        with open(filename, "w") as f:
            f.write(input_content.replace("{dev_extra_name}", dev_extra_name))

        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            exitcode = check_pyproject_toml(
                filename=filename,
                dev_extra_name=dev_extra_name,
                quiet=quiet,
            )

        assert exitcode == expected_exitcode

        if not quiet:
            expected_stderr_lines = [
                line.replace("{dev_extra_name}", dev_extra_name).replace(
                    "{filename}", filename
                )
                for line in expected_stderr_lines
            ]

            for line in stderr.getvalue().splitlines():
                assert line in expected_stderr_lines
