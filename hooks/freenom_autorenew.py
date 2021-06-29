"""Script that auto renews free Freenom domains."""

import argparse
import functools
import os
import re
import sys

import requests


MOZILLA_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/79.0.3945.130 Safari/537.36"
)

LOGIN_URL = "https://my.freenom.com/dologin.php"
DOMAIN_STATUS_URL = "https://my.freenom.com/domains.php?a=renewals"
RENEW_DOMAIN_URL = "https://my.freenom.com/domains.php?submitrenewals=true"

TOKEN_PTN = re.compile('name="token" value="(.*?)"', re.I)
DOMAIN_INFO_TPN = re.compile(
    r"<tr><td>(.*?)</td><td>[^<]+</td><td>[^<]+"
    r'<span class="[^<]+>(\d+?).Days</span>[^&]+&domain=(\d+?)">.*?</tr>',
    re.I,
)


class FreeNom:
    """Freenom implementation used to login into Freenom and autorenew free
    domains using HTTP requests.

    Extracted from https://github.com/SunYufei/freenom
    """

    def __init__(self, username: str, password: str):
        self._u = username
        self._p = password

        self._s = requests.Session()
        self._s.headers.update(
            {
                "user-agent": MOZILLA_USER_AGENT,
            }
        )

    def _login(self) -> bool:
        self._s.headers.update(
            {
                "content-type": "application/x-www-form-urlencoded",
                "referer": "https://my.freenom.com/clientarea.php",
            }
        )
        r = self._s.post(LOGIN_URL, data={"username": self._u, "password": self._p})
        return r.status_code == 200

    def renew(self, domain=None, period="12M"):
        """Renew the domains of an account."""
        ok = self._login()
        if not ok:
            sys.stderr.write(
                "Failed to login to Freenom.\nPlease, check that you've"
                " properly your credentials in 'FREENOM_EMAIL' and"
                " 'FREENOM_PASSWORD' environment variables.\n"
            )
            return

        self._s.headers.update({"referer": "https://my.freenom.com/clientarea.php"})
        r = self._s.get(DOMAIN_STATUS_URL)

        # page token
        match = re.search(TOKEN_PTN, r.text)
        if not match:
            sys.stderr.write("Failed to get token inside Freenom page\n")
            return
        token = match.group(1)

        # renew domains
        domains = re.findall(DOMAIN_INFO_TPN, r.text)

        for domain_, days, renewal_id in domains:
            if domain is not None and domain_ != domain:
                continue

            days = int(days)
            if days < 14:
                self._s.headers.update(
                    {
                        "referer": (
                            "https://my.freenom.com/domains.php?a=renewdomain"
                            "&domain={renewal_id}"
                        ),
                        "content-type": "application/x-www-form-urlencoded",
                    }
                )
                r = self._s.post(
                    RENEW_DOMAIN_URL,
                    data={
                        "token": token,
                        "renewalid": renewal_id,
                        f"renewalperiod[{renewal_id}]": period,
                        "paymentmethod": "credit",
                    },
                )
                if r.text.find("Order Confirmation") != -1:
                    sys.stdout.write(f"{domain_} -> Successful renew\n")
                else:
                    sys.stderr.write(f"{domain_} -> Error renewing!\n")
            sys.stdout.write(f"{domain_} -> {days} days for expiration\n")

        return True


def check_freenom_auth():
    authorization = True

    if not os.environ.get("FREENOM_EMAIL"):
        sys.stderr.write(
            "You must set the environment variable 'FREENOM_EMAIL' with"
            " the email used to login into your account.\n"
        )
        authorization = False

    if not os.environ.get("FREENOM_PASSWORD"):
        sys.stderr.write(
            "You must set the environment variable 'FREENOM_PASSWORD' with"
            " the password used to login into your account.\n"
        )
        authorization = False

    return authorization


@functools.lru_cache(maxsize=None)
def freenom_auth_parameters():
    return (os.environ["FREENOM_EMAIL"], os.environ["FREENOM_PASSWORD"])


def autorenew_freenom_domain(domain=None, period="12M", quiet=False):
    """Auto renews a free Freenom domain is it's inside the renovation time.

    Parameters
    ----------

    domain : str
      Domain to renew.

    period : str, optional
      Period for which to renew. As default, the maximum allowed for free domains.

    quiet : bool, optional
      If ``True``, don't print messages about what is doing during the process.
    """
    if not check_freenom_auth():
        return False

    freenom = FreeNom(*freenom_auth_parameters())
    return freenom.renew(domain=domain, period=period)


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Free Freenom domains autorenewer script.\n\nneeded environment"
            " variables:\n  - 'FREENOM_EMAIL':    Email used to authenticate"
            " your Freenom account.\n  - 'FREENOM_PASSWORD': Password used to"
            " authenticate your Freenom account."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-q", "--quiet", action="store_true", help="Supress output")
    parser.add_argument(
        "-d",
        "-domain",
        "--domain",
        type=str,
        metavar="DOMAIN",
        required=False,
        default=None,
        dest="domain",
        help=(
            "Freenom domain to renew. By default, all the free domains of your"
            " account will be renovated."
        ),
    )
    parser.add_argument(
        "-p",
        "-period",
        "--period",
        type=str,
        metavar="PERIOD",
        required=False,
        default="12M",
        dest="period",
        help=(
            "Period for the renovation. By default, the maximum allowed by"
            " Freenom for free domains, 12 months (12M)."
        ),
    )
    args = parser.parse_args()

    return (
        0
        if autorenew_freenom_domain(
            domain=args.domain, period=args.period, quiet=args.quiet
        )
        else 1
    )


if __name__ == "__main__":
    sys.exit(main())
