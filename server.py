# server.py
import logging
from fastmcp import FastMCP

# Importing config first configures stderr logging and validates the endpoint.
import config
# Import feature modules
from features import common, entities, apm, synthetics, alerts

logger = logging.getLogger(__name__)

# --- FastMCP Server Initialization ---
# Dependencies are defined here, but execution relies on fastmcp CLI handling them
# unless run directly with `python server.py` (not recommended for this setup).
mcp = FastMCP(
    "New Relic NerdGraph MCP Server",
    dependencies=["requests"] # Core dependency needed by client.py
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

# --- Main execution block (for info and potential direct run debugging) ---
if __name__ == "__main__":
    # This block is primarily for informational purposes when the script is run directly.
    # The recommended way to run is: `fastmcp run server.py:mcp`
    # Direct execution (`python server.py`) does not automatically handle dependencies
    # listed in the FastMCP constructor.
    logger.info("--- New Relic MCP Server ---")
    # Check for required config (already checked in config.py, but good to double-check here)
    try:
        if not config.API_KEY:
             logger.error("NEW_RELIC_API_KEY environment variable is not set.")
        if not config.ACCOUNT_ID:
            logger.warning("NEW_RELIC_ACCOUNT_ID environment variable is not set. Some features require it.")
    except Exception as e:
         logger.error("Error loading configuration: %s", e)

    logger.info("This script defines the MCP server instance.")
    logger.info("To run the server with dependency management, use: fastmcp run server.py:mcp")
    logger.info("Ensure NEW_RELIC_API_KEY and NEW_RELIC_ACCOUNT_ID are set in your environment.")

    # You could potentially add code here to start the server directly using uvicorn
    # for development/debugging, but `fastmcp run` is the intended method.
    # Example (requires `pip install uvicorn`):
    # import uvicorn
    # print("\nAttempting to start server directly with uvicorn (for debugging)...")
    # try:
    #     uvicorn.run(mcp.app, host="127.0.0.1", port=8000) # mcp.app exposes the ASGI app
    # except Exception as e:
    #     print(f"Failed to start uvicorn: {e}") 
