import logging
import os
import sys
from urllib.parse import urlparse

# --- Logging ---
# Configure logging to stderr. This server speaks MCP over stdio (JSON-RPC on
# stdout), so anything written to stdout corrupts the protocol stream. All
# diagnostics MUST go to stderr.
logging.basicConfig(
    stream=sys.stderr,
    level=os.getenv("NEWRELIC_MCP_LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("newrelic_mcp")

# Load API Key (Required)
API_KEY = os.getenv("NEW_RELIC_API_KEY")
if not API_KEY:
    raise ValueError("NEW_RELIC_API_KEY environment variable not set.")

# Load Account ID (Optional, but needed for many features)
ACCOUNT_ID_STR = os.getenv("NEW_RELIC_ACCOUNT_ID")
ACCOUNT_ID: int | None = None
if ACCOUNT_ID_STR:
    try:
        ACCOUNT_ID = int(ACCOUNT_ID_STR)
        logger.info("Using New Relic Account ID: %s", ACCOUNT_ID)
    except ValueError:
        # Don't raise immediately, let features that require it handle the None case
        logger.warning(
            "NEW_RELIC_ACCOUNT_ID ('%s') is not a valid integer. "
            "Features requiring an Account ID may fail.",
            ACCOUNT_ID_STR,
        )
else:
    logger.warning(
        "NEW_RELIC_ACCOUNT_ID environment variable not set. Some features require it."
    )


# --- NerdGraph API Endpoint ---
# The endpoint is configurable (e.g. for the EU data center), but because the
# New Relic API key is sent in every request, an attacker who can influence the
# environment could otherwise redirect that key to a server they control. We
# therefore require HTTPS and restrict the host to known New Relic domains.
#
# Set NERDGRAPH_ALLOW_INSECURE_ENDPOINT=true ONLY for trusted self-hosted/proxy
# setups where you accept the risk of sending the API key elsewhere.
DEFAULT_NERDGRAPH_URL = "https://api.newrelic.com/graphql"
ALLOWED_NERDGRAPH_HOST_SUFFIXES = (".newrelic.com",)

_ALLOW_INSECURE_ENDPOINT = os.getenv(
    "NERDGRAPH_ALLOW_INSECURE_ENDPOINT", "false"
).strip().lower() in ("1", "true", "yes")


def _validate_nerdgraph_url(url: str) -> str:
    """Validate a configured NerdGraph endpoint before the API key is ever sent to it."""
    if _ALLOW_INSECURE_ENDPOINT:
        logger.warning(
            "NERDGRAPH_ALLOW_INSECURE_ENDPOINT is set; skipping endpoint validation "
            "for '%s'. The New Relic API key will be sent to this host.",
            url,
        )
        return url

    parsed = urlparse(url)

    if parsed.scheme != "https":
        raise ValueError(
            f"Refusing to use NERDGRAPH_URL '{url}': only HTTPS endpoints are allowed "
            "(the New Relic API key is sent to this host). Set "
            "NERDGRAPH_ALLOW_INSECURE_ENDPOINT=true to override at your own risk."
        )

    host = (parsed.hostname or "").lower()
    if not any(
        host == suffix.lstrip(".") or host.endswith(suffix)
        for suffix in ALLOWED_NERDGRAPH_HOST_SUFFIXES
    ):
        raise ValueError(
            f"Refusing to use NERDGRAPH_URL '{url}': host '{host}' is not a recognized "
            f"New Relic domain ({', '.join(ALLOWED_NERDGRAPH_HOST_SUFFIXES)}). Set "
            "NERDGRAPH_ALLOW_INSECURE_ENDPOINT=true to override at your own risk."
        )

    return url


_configured_url = os.getenv("NERDGRAPH_URL")
if _configured_url:
    NERDGRAPH_URL = _validate_nerdgraph_url(_configured_url.strip())
else:
    NERDGRAPH_URL = DEFAULT_NERDGRAPH_URL
