"""Tests for 'nameserver-endswith' hook."""

import contextlib
import io

import pytest

from hooks.nameservers_endswith import nameservers_endswith


@pytest.mark.parametrize("quiet", (True, False), ids=("quiet=True", "quiet=False"))
@pytest.mark.parametrize(
    ("domain", "nameserver", "expected_result", "expected_stderr"),
    (
        pytest.param(
            "mkdocs-mdpo.ga",
            "cloudflare.com",
            True,
            "",
            id="domain=mkdocs-mdpo.ga-nameserver=cloudflare.com",
        ),
        pytest.param(
            "mkdocs-mdpo.ga",
            "cloudflare.co",
            False,
            (
                "Found invalid nameserver 'irma.ns.cloudflare.com' for domain"
                " 'mkdocs-mdpo.ga'.\nFound invalid nameserver"
                " 'craig.ns.cloudflare.com' for domain 'mkdocs-mdpo.ga'.\n"
            ),
            id="domain=mkdocs-mdpo.ga-nameserver=cloudflare.co",
        ),
    ),
)
def test_nameservers_endswith(
    domain, nameserver, expected_result, expected_stderr, quiet
):
    stderr = io.StringIO()

    with contextlib.redirect_stderr(stderr):
        result = nameservers_endswith(
            domain,
            nameserver,
            quiet=quiet,
        )

        assert result is expected_result

    if not quiet:
        assert expected_stderr == stderr.getvalue()
    else:
        assert not stderr.getvalue()
