# server.py
import logging
from fastmcp import FastMCP

# Importing config first configures stderr logging and validates the endpoint.
import config
# Import feature modules
from features import common, entities, apm, synthetics, alerts

logger = logging.getLogger(__name__)

# --- FastMCP Server Initialization ---
# Runtime dependencies (requests) are declared in fastmcp.json / requirements.txt.
# In FastMCP 3.x the `dependencies=` constructor argument was removed.
mcp = FastMCP(
    "New Relic NerdGraph MCP Server",
    instructions="Provides tools and resources to interact with the New Relic NerdGraph API.",
)

# --- Register Features ---
# Call the register function from each feature module
logger.info("Registering common features...")
common.register(mcp)
logger.info("Registering entity features...")
entities.register(mcp)
logger.info("Registering APM features...")
apm.register(mcp)
logger.info("Registering Synthetics features...")
synthetics.register(mcp)
logger.info("Registering Alerts features...")
alerts.register(mcp)

logger.info("Feature registration complete.")

# --- Main execution block ---
# Running `python server.py` starts the server over STDIO, which is what
# Claude Code (and other desktop MCP clients) expect. The `fastmcp run
# server.py:mcp` CLI works as well. All diagnostics go to stderr so the STDIO
# JSON-RPC stream on stdout stays clean.
if __name__ == "__main__":
    logger.info("Starting New Relic NerdGraph MCP Server (STDIO transport)...")
    if not config.ACCOUNT_ID:
        logger.warning("NEW_RELIC_ACCOUNT_ID is not set. Some features require it.")
    # Default transport is STDIO. For an HTTP deployment use:
    #   mcp.run(transport="http", host="127.0.0.1", port=8000)
    mcp.run()
