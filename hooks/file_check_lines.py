"""Check that a set of lines are included inside the content of a file."""

import argparse
import sys


def smart_quoted(value):
    return (
        f"'{value}'"
        if "'" not in value
        else (f'"{value}"' if '"' not in value else f"'{value}'")
    )


def normalize_lines(lines):
    normalized_lines = []
    for line in lines:
        if line:
            normalized_lines.append(line.strip("\r\n"))
    normalized_lines.sort()
    return normalized_lines


def file_check_lines(filename, expected_lines, quiet=False):

    with open(filename, encoding="utf-8") as f:
        lines = f.read().splitlines()

    expected_lines = normalize_lines(expected_lines)
    if not expected_lines:
        sys.stderr.write("Any valid non empty expected line passed as argument\n")
        return 1

    retcode = 0
    for expected_line in expected_lines:
        if expected_line in lines:
            continue

        retcode = 1
        if not quiet:
            sys.stderr.write(
                f"Line {smart_quoted(expected_line)} not found in file {filename}\n"
            )

    return retcode


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--quiet", action="store_true", help="Supress output")
    parser.add_argument("filename", help="Filename to check for content")
    parser.add_argument("lines", nargs="+", help="Lines to check")
    args = parser.parse_args()

    return file_check_lines(args.filename, args.lines, quiet=args.quiet)


if __name__ == "__main__":
    sys.exit(main())
