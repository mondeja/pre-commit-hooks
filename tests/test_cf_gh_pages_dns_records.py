"""Tests for 'cloudflare-gh-pages-dns' hook."""

import contextlib
import io
import os

import pytest

from hooks.cf_gh_pages_dns_records import check_cloudflare_gh_pages_dns_records


@pytest.mark.skipif(
    not os.environ.get("CF_API_KEY"),
    reason=(
        "Cloudflare user API key defined in 'CF_API_KEY' environment variable"
        " needed."
    ),
)
@pytest.mark.parametrize("quiet", (True, False), ids=("quiet=True", "quiet=False"))
@pytest.mark.parametrize(
    ("domain", "username", "expected_result", "expected_stderr"),
    (
        pytest.param(
            "hrcgen.ml",
            "mondeja",
            True,
            "",
            id="domain=hrcgen.ml-username=mondeja",  # configured with GH pages
        ),
        pytest.param(
            "foobar.baz",
            "mondeja",
            False,
            (
                "The domain 'foobar.baz' was not found being managed by your"
                " Cloudflare account.\n"
            ),
            id="domain=foobar.baz-username=mondeja",  # inexistent zone
        ),
        # TODO: add example domain to test bad configuration
    ),
)
def test_check_cloudflare_gh_pages_dns_records(
    domain,
    username,
    expected_result,
    expected_stderr,
    quiet,
):
    stderr = io.StringIO()

    with contextlib.redirect_stderr(stderr):
        result = check_cloudflare_gh_pages_dns_records(
            domain,
            username,
            quiet=quiet,
        )

        assert result is expected_result

    assert stderr.getvalue() == expected_stderr
