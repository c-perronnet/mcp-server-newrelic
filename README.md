[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/ulucaydin-mcp-server-newrelic-badge.png)](https://mseep.ai/app/ulucaydin-mcp-server-newrelic)

# New Relic NerdGraph MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) <!-- Add license if applicable -->

This repository provides a [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server for interacting with the [New Relic NerdGraph API](https://docs.newrelic.com/docs/apis/nerdgraph/get-started/introduction-new-relic-nerdgraph/). It allows MCP clients (like Claude Desktop) to use natural language or specific commands to query and interact with your New Relic account data and features.

Built using the [FastMCP](https://gofastmcp.com) framework (v3).

## Features

This MCP server exposes various New Relic capabilities as tools and resources, including:

*   **Account Details:** Fetch basic information about the configured account.
*   **Generic NerdGraph Queries:** Execute arbitrary NerdGraph queries.
*   **NRQL Queries:** Run specific NRQL queries against your account data.
*   **Entity Management:** Search for entities (Applications, Hosts, Monitors, etc.) and retrieve detailed information by GUID.
*   **APM:** List Application Performance Monitoring (APM) applications.
*   **Synthetics:** List Synthetic monitors and create simple browser monitors.
*   **Alerts:** List alert policies, view open incidents, and acknowledge incidents.

## Prerequisites

*   **Python:** Python 3.10+ recommended (as required by `fastmcp`).
*   **pip:** Python package installer.
*   **New Relic Account:** Access to a New Relic account.
*   **New Relic User API Key:** A User API key is required for authentication. You can generate one [here](https://docs.newrelic.com/docs/apis/intro-apis/new-relic-api-keys/#user-api-key). **Keep this key secure!**
*   **New Relic Account ID:** Your New Relic Account ID is needed for most operations. You can find it in the New Relic UI (often in the URL or account settings).

## Setup & Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the actual URL
    cd mcp-server-newrelic
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    This will install `fastmcp`, `requests`, and their dependencies.

## Configuration

The server requires your New Relic API Key and Account ID to function. Configure these using environment variables **before** running the server:

```bash
# Replace YOUR_API_KEY and YOUR_ACCOUNT_ID with your actual credentials
export NEW_RELIC_API_KEY="YOUR_API_KEY"
export NEW_RELIC_ACCOUNT_ID="YOUR_ACCOUNT_ID"
# EU-region accounts: select the EU data center
export NEW_RELIC_REGION="EU"
```

**Security Note:** Do not hardcode your API key in the source code. Using environment variables is the recommended approach. You can also use tools like `direnv` or place these `export` commands in your shell profile (`.zshrc`, `.bashrc`, etc.) for persistence, but be mindful of the security implications.

### Optional environment variables

| Variable | Default | Purpose |
| --- | --- | --- |
| `NEW_RELIC_REGION` | `US` | Selects the NerdGraph endpoint by region: `US` → `api.newrelic.com`, `EU` → `api.eu.newrelic.com`. **EU-region accounts must set `NEW_RELIC_REGION=EU`.** |
| `NERDGRAPH_URL` | (from region) | Override the NerdGraph endpoint with a full URL. Takes precedence over `NEW_RELIC_REGION`. Must be HTTPS and a `*.newrelic.com` host — your API key is sent here. |
| `NERDGRAPH_ALLOW_INSECURE_ENDPOINT` | `false` | Set to `true` to bypass the endpoint allowlist for a trusted self-hosted proxy. **Only do this if you accept that the API key will be sent to that host.** |
| `NEWRELIC_MCP_LOG_LEVEL` | `INFO` | Logging verbosity (`DEBUG` logs query/response bodies — may contain sensitive data). |

## Running the Server

This server uses the **STDIO** transport by default — the MCP client launches it as a
subprocess and communicates over stdin/stdout. You normally don't run it by hand; the
client (e.g. Claude Code, Claude Desktop) starts it for you using the configuration below.

To run it manually for a quick smoke test:

```bash
fastmcp run server.py:mcp   # or: python server.py
```

> All diagnostic output goes to **stderr** so the STDIO JSON-RPC stream on stdout stays
> clean. Set `NEWRELIC_MCP_LOG_LEVEL=DEBUG` for verbose logging (note: DEBUG logs query
> and response bodies, which may contain sensitive data).

## Usage with Claude Code

The easiest way is the FastMCP CLI, which registers the server with Claude Code and wires
up dependencies automatically (it reads `fastmcp.json`):

```bash
fastmcp install claude-code server.py \
  --env NEW_RELIC_API_KEY=YOUR_API_KEY \
  --env NEW_RELIC_ACCOUNT_ID=YOUR_ACCOUNT_ID
```

Or configure it manually with `claude mcp add` (uses `uv` to provide an isolated
environment — recommended):

```bash
claude mcp add newrelic \
  -e NEW_RELIC_API_KEY=YOUR_API_KEY \
  -e NEW_RELIC_ACCOUNT_ID=YOUR_ACCOUNT_ID \
  -- uv run --with fastmcp --with requests fastmcp run /absolute/path/to/server.py:mcp
```

Verify the connection with `/mcp` inside Claude Code, then ask things like
*"Show me my APM applications"* or *"List open critical incidents in account 1234567"*.

## Usage with Other MCP Clients (e.g. Claude Desktop)

Add an entry to your client's MCP config (for Claude Desktop:
`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "newrelic": {
      "command": "uv",
      "args": ["run", "--with", "fastmcp", "--with", "requests",
               "fastmcp", "run", "/absolute/path/to/server.py:mcp"],
      "env": {
        "NEW_RELIC_API_KEY": "YOUR_API_KEY",
        "NEW_RELIC_ACCOUNT_ID": "YOUR_ACCOUNT_ID"
      }
    }
  }
}
```

After saving, restart the client. You should see a 🔨 / tools indicator. You can now
interact with your New Relic account using natural language or by directly invoking the
tools listed below.

    *   **Natural Language Example:** "Show me my APM applications" or "List open critical incidents in account 1234567"
    *   **Direct Invocation (if supported):** `list_apm_applications()` or `list_open_incidents(priority='CRITICAL', target_account_id=1234567)`

## Available Tools & Resources

The server provides the following functions accessible via the Model Context Protocol:

---

### Common (`features/common.py`)

*   **Tool: `query_nerdgraph`**
    *   **Description:** Executes an arbitrary NerdGraph query. Use for operations not covered by specific tools.
    *   **Arguments:**
        *   `nerdgraph_query` (str): The GraphQL query string.
        *   `variables` (Optional[Dict]): JSON dictionary of variables for the query.
    *   **Returns:** JSON string of the query result.

*   **Tool: `run_nrql_query`**
    *   **Description:** Executes a NRQL query.
    *   **Arguments:**
        *   `nrql` (str): The NRQL query string (e.g., `"SELECT count(*) FROM Transaction TIMESERIES"`).
        *   `target_account_id` (Optional[int]): Account ID to query (uses default from env if omitted).
    *   **Returns:** JSON string of the NRQL result.

*   **Resource: `get_account_details`**
    *   **Description:** Provides basic details (ID, name) for the configured New Relic account.
    *   **URI:** `newrelic://account_details`
    *   **Returns:** JSON string containing account details (`{"data": {"id": ..., "name": ...}}`) or an error.

---

### Entities (`features/entities.py`)

*   **Tool: `search_entities`**
    *   **Description:** Searches for New Relic entities based on criteria.
    *   **Arguments:**
        *   `name` (Optional[str]): Filter by name (fuzzy match).
        *   `entity_type` (Optional[str]): Filter by type (e.g., `'APPLICATION'`, `'HOST'`).
        *   `domain` (Optional[str]): Filter by domain (e.g., `'APM'`, `'INFRA'`).
        *   `tags` (Optional[List[Dict]]): Filter by tags (e.g., `[{"key": "env", "value": "prod"}]`).
        *   `target_account_id` (Optional[int]): Explicit account ID to search within.
        *   `limit` (int): Max results (default 50).
    *   **Returns:** JSON string of search results.

*   **Resource: `get_entity_details`**
    *   **Description:** Retrieves detailed information for a specific entity. Includes common fields and type-specific details for APM, Browser, Infra, Synthetics, Dashboards, etc.
    *   **URI:** `newrelic://entity/{guid}` (replace `{guid}` with the entity GUID)
    *   **Returns:** JSON string of entity details.

*   **Prompt: `generate_entity_search_query`**
    *   **Description:** Generates the `query` string condition part for the `entitySearch` NerdGraph field, useful for constructing search queries.
    *   **Arguments:**
        *   `entity_name` (str): Name to search for (exact match used in prompt generation).
        *   `entity_domain` (Optional[str]): Domain to include in the query condition.
        *   `entity_type` (Optional[str]): Type to include in the query condition.
        *   `target_account_id` (Optional[int]): Account ID to include in the query condition.
    *   **Returns:** String representing the search condition (e.g., `"accountId = 123 AND name = 'My App' AND domain = 'APM'"`).

---

### APM (`features/apm.py`)

*   **Tool: `list_apm_applications`**
    *   **Description:** Lists APM applications.
    *   **Arguments:**
        *   `target_account_id` (Optional[int]): Account ID to query (uses default if omitted).
    *   **Returns:** JSON string containing a list of APM applications.

---

### Synthetics (`features/synthetics.py`)

*   **Tool: `list_synthetics_monitors`**
    *   **Description:** Lists Synthetic monitors.
    *   **Arguments:**
        *   `target_account_id` (Optional[int]): Account ID to query (uses default if omitted).
    *   **Returns:** JSON string containing a list of Synthetic monitors.

*   **Tool: `create_simple_browser_monitor`**
    *   **Description:** Creates a basic Synthetics simple browser monitor.
    *   **Arguments:**
        *   `monitor_name` (str): Name for the new monitor.
        *   `url` (str): URL to monitor.
        *   `locations` (List[str]): List of public location labels (e.g., `["AWS_US_EAST_1"]`).
        *   `period` (str): Check frequency (e.g., `"EVERY_15_MINUTES"`). Default: `"EVERY_15_MINUTES"`.
        *   `status` (str): Initial status (`"ENABLED"` or `"DISABLED"`). Default: `"ENABLED"`.
        *   `target_account_id` (Optional[int]): Account ID for creation (uses default if omitted).
        *   `tags` (Optional[List[Dict]]): Optional tags (e.g., `[{"key": "team", "value": "ops"}]`).
    *   **Returns:** JSON string with the result, including the new monitor's GUID.

*   **Resource:** Synthetics monitor details can be retrieved using the `get_entity_details` resource with the monitor's GUID (`newrelic://entity/{monitor_guid}`).

---

### Alerts (`features/alerts.py`)

*   **Tool: `list_alert_policies`**
    *   **Description:** Lists alert policies, optionally filtering by name.
    *   **Arguments:**
        *   `target_account_id` (Optional[int]): Account ID to query (uses default if omitted).
        *   `policy_name_filter` (Optional[str]): Filter policies where name contains this string.
    *   **Returns:** JSON string containing a list of alert policies.

*   **Tool: `list_open_incidents`**
    *   **Description:** Lists currently open alert incidents.
    *   **Arguments:**
        *   `target_account_id` (Optional[int]): Account ID to query (uses default if omitted).
        *   `priority` (Optional[str]): Filter by priority (`'CRITICAL'`, `'WARNING'`).
    *   **Returns:** JSON string containing a list of open incidents.

*   **Tool: `acknowledge_alert_incident`**
    *   **Description:** Acknowledges an open alert incident.
    *   **Arguments:**
        *   `incident_id` (int): The ID of the incident to acknowledge.
        *   `target_account_id` (Optional[int]): Account ID where the incident occurred (uses default if omitted).
        *   `message` (Optional[str]): Optional message for the acknowledgement.
    *   **Returns:** JSON string with the result of the acknowledgement.

---

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature`).
3.  Make your changes.
4.  Commit your changes (`git commit -am 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature`).
6.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details (if a LICENSE file exists). 