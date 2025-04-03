# AlphaForge v1.0

A minimal but functional MCP-LEAN bridge with Gemini integration, designed for QuantConnect interaction.

## Features

*   **Natural Language to Backtest:** Use Gemini to parse strategy descriptions into actionable parameters.
*   **Local LEAN Backtesting:** Execute backtests directly using the local LEAN engine via Docker.
*   **QuantConnect Cloud Integration:**
    *   Push local project changes to the cloud (`push_project`).
    *   Initiate backtests on QuantConnect Cloud (`cloud_backtest`).
    *   (Placeholder) Download market data.
*   **MCP Server:** Provides a standardized API for interacting with these tools.
*   **Dockerized:** Runs the MCP server and LEAN engine in containers for consistent environments.
*   **Basic Security:** Includes OAuth2 authentication scaffolding.

## Setup

1.  **Clone Repository:**
    ```bash
    git clone <your-repo-url>
    cd alphaforge-v1
    ```

2.  **Configure Environment:**
    *   Copy `.env.example` (if provided) or create a `.env` file.
    *   Fill in your API keys and user IDs:
        ```dotenv
        GEMINI_API_KEY=your_gemini_api_key
        QC_API_KEY=your_quantconnect_api_key # Also known as API Token
        QC_USER_ID=your_quantconnect_user_id
        QC_API_TOKEN=your_quantconnect_api_token # Same as QC_API_KEY

        # Optional: Customize allowed symbols for validation
        # ALLOWED_SYMBOLS=SPY,QQQ,AAPL,GOOG,BTCUSD,ETHUSD

        # Optional: Specify local path if different from default
        # QC_PROJECTS_DIR=./MyQCProjects
        ```
    *   **Important:** Ensure the `QC_API_KEY` and `QC_API_TOKEN` are the same value (your QuantConnect API Access Token).

3.  **Create Configuration File:**
    *   Ensure the `config/` directory exists.
    *   Create `config/risk_settings.json` (or use the one generated):
        ```json
        {
            "max_position_size": 100000,
            "max_drawdown_percent": 5,
            "allowed_symbols": ["SPY", "QQQ", "AAPL", "GOOG", "BTCUSD", "ETHUSD"],
            "default_stop_loss_percent": 2,
            "default_take_profit_percent": 5,
            "max_trades_per_day": 10
        }
        ```
    *   *Note:* The `allowed_symbols` here might be superseded by the `ALLOWED_SYMBOLS` environment variable if set.

4.  **Install Dependencies (Optional - primarily for local testing):**
    ```bash
    pip install -r requirements.txt
    # Add pytest & pytest-mock if running tests locally
    pip install pytest pytest-mock pytest-asyncio
    ```

5.  **Build and Start Docker Containers:**
    ```bash
    docker-compose up --build
    ```
    *   The first build might take some time to download base images and install dependencies.
    *   The `mcp_server` container will initialize the LEAN CLI using the credentials from `.env`.

## Usage

Interact with the MCP server API, typically running on `http://localhost:8080`.

**Example: Running a Cloud Backtest**

```python
import requests
import json

mcp_server_url = "http://localhost:8080" # Adjust if needed

# Define the request payload
payload = {
    "project_name": "My Cloud Strategy Name", # Must exist in your QC account
    "strategy_parameters": {
        "symbol": "SPY",          # Make sure SPY is allowed
        "momentum_window": 14,
        "holding_period": 5
        # Add other parameters your QC algorithm expects
    },
    "backtest_name": "AlphaForge API Test Run" # Optional name for the run
}

# Make the POST request to the cloud_backtest tool
try:
    response = requests.post(
        f"{mcp_server_url}/tools/cloud_backtest",
        json=payload
        # Add authentication headers if required/configured
        # headers={"Authorization": "Bearer YOUR_ACCESS_TOKEN"}
    )

    response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

    result = response.json()
    print("API Response:")
    print(json.dumps(result, indent=2))

    if result.get("status") == "success" and result.get("backtest_id"):
        print(f"\nCloud backtest submitted successfully!")
        print(f"Backtest ID: {result['backtest_id']}")
        # You can use this ID to check status/results on QuantConnect website
    elif result.get("status") == "error":
        print(f"\nError: {result.get('context')} - {result.get('message')}")

except requests.exceptions.RequestException as e:
    print(f"API Request Failed: {e}")
except json.JSONDecodeError:
    print(f"Failed to decode JSON response: {response.text}")

```

**Other Available Tools:**

*   `/tools/push_project`: Pushes changes for a specific project to QC Cloud.
    *   Payload: `{"project_name": "Project Name To Push"}`
*   `/tools/download_market_data`: (Placeholder) Intended to download data.
*   `/tools/local_backtest_strategy`: Runs a backtest using the local LEAN engine.
    *   Payload: `{"strategy_description": "Run basic template algorithm"}`

**Available Resources:**

*   `/resources/cloud_projects`: (Placeholder) Lists QC Cloud projects.
*   `/resources/risk_parameters`: Reads settings from `config/risk_settings.json`.

## Running Tests (Locally)

Ensure `pytest`, `pytest-mock`, and `pytest-asyncio` are installed.

```bash
python -m pytest tests/
```

## Project Structure

```bash
alphaforge-v1/
├── .env                  # Environment variables (GITIGNORE THIS!)
├── config/
│   └── risk_settings.json # Risk parameters
├── docker-compose.yml    # Container setup
├── requirements.txt      # Python dependencies
├── scripts/
│   └── init-lean.sh      # Script to initialize LEAN CLI in container
├── src/
│   ├── mcp_server/       # Core MCP logic
│   │   ├── __init__.py
│   │   ├── server.py     # MCP Server definition
│   │   ├── tools.py      # Tool definitions (TradingTools)
│   │   ├── bridge.py     # Local LEAN bridge
│   │   └── Dockerfile    # Dockerfile for the MCP server service
│   ├── nlp/              # Natural Language Processing
│   │   ├── __init__.py
│   │   └── gemini_parser.py # Gemini interaction logic
│   └── integrations/     # External service integrations
│       ├── __init__.py
│       └── qc_cloud.py   # QuantConnect Cloud bridge logic
└── tests/                # Test suite
    ├── __init__.py
    ├── test_parser.py    # Tests for Gemini parser
    └── test_tools.py     # Tests for MCP tools
└── README.md             # This file
```
