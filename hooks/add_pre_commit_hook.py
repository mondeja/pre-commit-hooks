"""Add a pre-commit hook to a pre-commit configuration file, if this exists."""

import argparse
import os
import sys

import yaml


def add_pre_commit_hook(repo, rev, hook_id, quiet=False, dry_run=False):
    """Add a pre-commit hook configuration to a pre-commit configuration file.

    Parameters
    ----------

    repo : str
      Repository where the hook to add is defined.

    rev : str
      Hook's repository version.

    hook_id: str
      Hook identifier.

    quiet : bool, optional
      Don't print output to STDERR (only has effect with ``dry_run`` enabled).

    dry_run: bool, optional
      When enabled, only writes to STDERR the replacements that would be added,
      but are not done.

    Returns
    -------

    int: 1 if the pre-commit configuration file has been changed, 0 otherwise.

    """
    pre_commit_config_path = ".pre-commit-config.yaml"
    if not os.path.isfile(pre_commit_config_path):
        return 0

    with open(pre_commit_config_path) as f:
        config_content = f.read()
        config = yaml.safe_load(config_content)

    if "repos" not in config or not config["repos"]:
        return 0

    _repo_found, _hook_found, _same_rev = (False, False, False)
    for repo_ in config["repos"]:
        if repo_["repo"] == repo:
            _repo_found = True
            _hook_found = hook_id in [hook["id"] for hook in repo_["hooks"]]
            _same_rev = repo_["rev"] == rev
            break

    if not _repo_found or not _same_rev:
        _repo_indentation = 2
        config_lines = config_content.splitlines(keepends=True)
        for line in config_lines:
            if line.lstrip().startswith("- repo:"):
                _repo_indentation = line.index("-")
                break
        indent = " " * _repo_indentation

        new_lines = config_lines
        new_lines.extend(
            [
                f"{indent}- repo: {repo}\n",
                f"{indent}  rev: {rev}\n",
                f"{indent}  hooks:\n",
                f"{indent}    - id: {hook_id}\n",
            ]
        )

        if dry_run:
            if not quiet:
                sys.stderr.write(
                    f"The hook '{hook_id}' with repo '{repo}' (rev: {rev})"
                    " would be added to '.pre-commit.config.yaml'\n"
                )
        else:
            with open(pre_commit_config_path, "w") as f:
                f.writelines(new_lines)

        return 1

    if not _hook_found and _same_rev:
        config_lines = config_content.splitlines(keepends=True)

        _inside_repo, _inside_hooks, _hooks_indent = (False, False, None)
        for i, line in enumerate(config_lines):
            if not _inside_repo:
                if line.lstrip().startswith("- repo:") and repo in line.replace(
                    "- repo:", ""
                ):
                    _inside_repo = True
            else:
                if _inside_hooks:
                    if _hooks_indent is None:
                        _hooks_indent = line.index("-") if "-" in line else None

                    if line.lstrip().startswith("- repo:"):
                        break
                else:
                    if line.lstrip().startswith("hooks:"):
                        _inside_hooks = True

        new_lines = []
        for n, line in enumerate(config_lines):
            new_lines.append(line)
            if n == i:
                new_lines.append(" " * _hooks_indent + f"- id: {hook_id}\n")

        if dry_run:
            if not quiet:
                sys.stderr.write(
                    f"The hook '{hook_id}' would be added to repo '{repo}'"
                    f" (rev: {rev})' at '.pre-commit.config.yaml'\n"
                )
        else:
            with open(pre_commit_config_path, "w") as f:
                f.writelines(new_lines)
        return 1

    return 0


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
        "-repo",
        "--repo",
        type=str,
        metavar="URL",
        required=True,
        dest="repo",
        help="Repository URL where the hook is defined.",
    )
    parser.add_argument(
        "-rev",
        "--rev",
        type=str,
        metavar="VERSION",
        required=True,
        dest="rev",
        help="Repository tag to fetch.",
    )
    parser.add_argument(
        "-id",
        "--id",
        type=str,
        metavar="HOOK_ID",
        required=True,
        dest="hook_id",
        help="Identifier of the hook to be added.",
    )

    args = parser.parse_args()

    exitcode = add_pre_commit_hook(
        args.repo,
        args.rev,
        args.hook_id,
    )

    return exitcode


if __name__ == "__main__":
    exit(main())
