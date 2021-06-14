"""This pre-commit hook will read all the Python dependencies of the project
and, if your project has other extras requirements in dependencies, will check
if your installation configuration contains a development extras requirements
option which would contain all other requirements.
"""

import argparse
import configparser
import os
import sys


def check_setup_cfg(
    filename="setup.cfg",
    dev_extra_name="dev",
    quiet=False,
    dry_run=False,
):
    """Check that all other extra requirements than development ones are
    included in development extra group in a ``setup.cfg`` configuration file.

    Parameters
    ----------

    filename : str, optional
      Path to the file to check.

    dev_extra_name : str, optional
      Development extra requirements group name.

    quiet : bool, optional
      Enabled, don't print output to stderr when a requirement is not
      defined in development extra requirements group.

    dry_run : bool, optional
      Enable, don't make the rewritting of the file, just print errors
      to STDERR.
    """
    exitcode = 0

    config = configparser.ConfigParser()
    with open(filename) as f:
        config.read_string(f.read())

    dev_extra_requirements = []
    other_extra_requirements = []

    if config.has_section("options.extras_require"):
        for extra, requirements_str in config.items("options.extras_require"):
            requirements = [r for r in requirements_str.split("\n") if r]

            if extra == dev_extra_name:
                dev_extra_requirements.extend(requirements)
            else:
                other_extra_requirements.extend(requirements)

    for requirement in other_extra_requirements:
        if requirement not in dev_extra_requirements:
            exitcode = 1

            if dry_run:
                if not quiet:
                    sys.stderr.write(
                        f"Requirement '{requirement}' would be added to"
                        f" '{dev_extra_name}' extra group at '{filename}'\n"
                    )
            else:
                dev_extra_requirements.append(requirement)
                dev_extra_requirements.sort()
                config.set(
                    "options.extras_require",
                    dev_extra_name,
                    "\n" + "\n".join(dev_extra_requirements),
                )

    if exitcode:
        with open(filename, "w") as f:
            config.write(f)

    return exitcode


def check_pyproject_toml(
    filename="pyproject.toml",
    dev_extra_name="dev",
    quiet=False,
):
    """Check that all other extra requirements than development ones are
    included in development extra group in a ``pyproject.toml`` configuration
    file.

    Parameters
    ----------

    filename : str, optional
      Path to the file to check.

    dev_extra_name : str, optional
      Development extra requirements group name.

    quiet : bool, optional
      Enabled, don't print output to stderr when a requirement is not
      defined in development extra requirements group.
    """
    import toml

    with open(filename) as f:
        parsed_toml = toml.loads(f.read())

    def _extra_reqs_not_found():
        sys.stderr.write(f"Extra requirements not found in file '{filename}'\n")
        return 1

    if "tool" not in parsed_toml:
        return _extra_reqs_not_found()

    def update_pyproject_toml_if_needed(build_system):
        exitcode = 0
        if build_system == "flit":
            if "metadata" not in parsed_toml["tool"]["flit"]:
                return _extra_reqs_not_found()

            if "requires-extra" not in parsed_toml["tool"]["flit"]["metadata"]:
                return _extra_reqs_not_found()

            requires_extra = parsed_toml["tool"]["flit"]["metadata"]["requires-extra"]
        else:  # build_system == "poetry":
            if "extras" not in parsed_toml["tool"]["poetry"]:
                return _extra_reqs_not_found()

            requires_extra = parsed_toml["tool"]["poetry"]["extras"]

        dev_extra_requirements, other_extra_requirements = ([], [])

        for extra, requirements in requires_extra.items():
            if extra == dev_extra_name:
                dev_extra_requirements.extend(requirements)
            else:
                other_extra_requirements.extend(requirements)

        # toml package must implement TOML files prettifycation in order to
        # rewrite the TOML file

        for requirement in other_extra_requirements:
            if requirement not in dev_extra_requirements:
                exitcode = 1

                # if dry_run:
                if not quiet:
                    sys.stderr.write(
                        f"Requirement '{requirement}' would be added to"
                        f" '{dev_extra_name}' extra group at '{filename}'\n"
                    )
                """
                else:
                    if dev_extra_name not in requires_extra:
                        requires_extra[dev_extra_name] = []
                    requires_extra[dev_extra_name].append(requirement)
                """

        """
        if exitcode:
            if build_system == "flit":
                parsed_toml["tool"]["flit"]["metadata"]["requires-extra"] = (
                    requires_extra
                )
            else:
                parsed_toml["tool"]["poetry"]["extras"] = requires_extra

            new_toml_content = toml.dumps(parsed_toml)
            with open(filename, "w") as f:
                f.write(new_toml_content)
        """

        return exitcode

    if "flit" in parsed_toml["tool"]:
        exitcode = update_pyproject_toml_if_needed("flit")
    elif "poetry" in parsed_toml["tool"]:
        exitcode = update_pyproject_toml_if_needed("poetry")
    else:
        exitcode = _extra_reqs_not_found()
    return exitcode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", nargs="*")
    parser.add_argument("-q", "--quiet", action="store_true", help="Supress output")
    parser.add_argument(
        "-d",
        "--dry-run",
        action="store_true",
        dest="dry_run",
        help="Don't do the rewriting, just writes errors to stderr.",
    )
    parser.add_argument(
        "-extra",
        "--extra",
        type=str,
        metavar="NAME",
        required=False,
        default="dev",
        dest="extra_name",
        help="Path to the 'setup.cfg' file.",
    )
    parser.add_argument(
        "-setup-cfg",
        "--setup-cfg",
        type=str,
        metavar="FILEPATH",
        required=False,
        default="setup.cfg",
        dest="setup_cfg",
        help="Path to the 'setup.cfg' file.",
    )
    parser.add_argument(
        "-pyproject-toml",
        "--pyproject-toml",
        type=str,
        metavar="FILEPATH",
        required=False,
        default="pyproject.toml",
        dest="pyproject_toml",
        help="Path to the 'pyproject.toml' file.",
    )
    args = parser.parse_args()

    filenames = (args.setup_cfg, args.pyproject_toml)
    if not any([os.path.isfile(filename) for filename in filenames]):
        for filename in filenames:
            sys.stderr.write(f"'{filename}' file not found\n")
        return 1

    if os.path.isfile(args.setup_cfg):
        exitcode = check_setup_cfg(
            filename=args.setup_cfg,
            dev_extra_name=args.extra_name,
            quiet=args.quiet,
            dry_run=args.dry_run,
        )
    else:
        exitcode = check_pyproject_toml(
            filename=args.pyproject_toml,
            dev_extra_name=args.extra_name,
            quiet=args.quiet,
        )

    return exitcode


if __name__ == "__main__":
    exit(main())
