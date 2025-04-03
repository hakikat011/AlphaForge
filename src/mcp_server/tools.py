# Placeholder for MCP server tool definitions
# You might define shared tools or configurations here. 

from mcp import Tool, Resource
from typing import Optional, Dict, List
from datetime import datetime # Added missing import
# Corrected import path for QuantConnectCloudBridge
from ..integrations.qc_cloud import QuantConnectCloudBridge 
# Removed import for deploy_live_with_confirmation as it's not implemented yet
# from ..integrations.qc_cloud import deploy_live_with_confirmation 
import shlex
import os
import re # Import re for _extract_backtest_id

class TradingTools:
    def __init__(self):
        self.qc_bridge = QuantConnectCloudBridge()
        # Note: This env var might not be set in the container unless explicitly defined
        self.projects_dir = os.getenv("QC_PROJECTS_DIR", "./QuantConnect Projects") # Defaulting locally might be safer

    # --------------------------
    # Core Trading Operations
    # --------------------------
    
    @Tool(
        name="cloud_backtest",
        description="Run a backtest on QuantConnect Cloud",
        params={
            "project_name": "str",
            "strategy_parameters": "dict", # Keep as dict for flexibility
            "backtest_name": "Optional[str]"
        }
    )
    async def cloud_backtest(self, 
                           project_name: str,
                           strategy_parameters: Dict, # Accept parameters dictionary
                           backtest_name: Optional[str] = None) -> Dict:
        """
        Initiates a cloud backtest after pushing project changes.
        Example Usage:
        {
            "project_name": "SPY Momentum Strategy",
            "strategy_parameters": { 
                "symbol": "SPY", 
                "momentum_window": 14, 
                "holding_period": 5
            },
            "backtest_name": "AlphaForge Optimized v1.2"
        }
        """
        try:
            # 1. Validate input (example: ensure symbol exists in params)
            symbol = strategy_parameters.get('symbol')
            if symbol:
                 self._validate_symbol(symbol)
            else:
                 print("Warning: No symbol provided in strategy_parameters for validation.")
                 # Or potentially raise ValueError if symbol is mandatory

            # --- Note: Strategy Parameter Handling --- 
            # The strategy_parameters dict is received but NOT automatically passed 
            # to the LEAN CLI backtest command here. 
            # LEAN algorithms typically read parameters from 'parameters.json' or 
            # environment variables set during deployment/backtest launch.
            # Passing arbitrary dicts requires modifying the QC algorithm 
            # (e.g., to read from ObjectStore) or enhancing the bridge/CLI interaction.
            # For now, these params are just validated/logged.
            print(f"Received strategy parameters: {strategy_parameters}")

            # 2. Push project to cloud (using the name directly)
            # Quoting is handled within the bridge method
            print(f"Pushing project: {project_name}")
            push_result = await self.qc_bridge.push_changes(project_name)
            
            if not push_result["success"]:
                # Include more detail from push_result if available
                error_details = push_result.get("error", "Unknown push error")
                if push_result.get("output"): # Sometimes errors are in output
                    error_details += f" | Output: {push_result['output'][:200]}..."
                return self._format_error("Push failed", error_details)
            print(f"Push successful for project: {project_name}")
                
            # 3. Submit backtest
            print(f"Submitting backtest for project: {project_name}")
            bt_result = await self.qc_bridge.submit_cloud_backtest(
                project_name,
                backtest_name # Pass optional name
            )
            
            # Extract backtest ID if submission was successful
            backtest_id = None
            if bt_result["success"]:
                 backtest_id = self._extract_backtest_id(bt_result["output"])
                 print(f"Backtest submitted successfully. ID: {backtest_id}")
            else:
                 print(f"Backtest submission failed. Error: {bt_result.get('error')}")

            return {
                "status": "success" if bt_result["success"] else "error",
                "backtest_id": backtest_id, # Include extracted ID
                "details": bt_result # Return full submission result
            }
            
        except ValueError as ve:
             # Catch specific validation errors
             return self._format_error("Validation Error", str(ve))
        except Exception as e:
            # Catch unexpected errors during the process
            import traceback
            print(f"Unexpected Error in cloud_backtest: {traceback.format_exc()}")
            return self._format_error("Backtest process failed", str(e))

    # --------------------------
    # Live Trading Operations (Commented out until dependencies are implemented)
    # --------------------------

    # @Tool(
    #     name="deploy_live",
    #     description="Deploy strategy to live trading with confirmation",
    #     params={
    #         "project_name": "str",
    #         "environment": "str",
    #         "confirmation_token": "str"
    #     },
    #     require_auth=True
    # )
    # async def deploy_live(self, 
    #                     project_name: str,
    #                     environment: str = "paper",
    #                     confirmation_token: str = "") -> Dict:
    #     """
    #     Safety wrapper for live deployments
    #     """
    #     if not self._validate_confirmation_token(confirmation_token):
    #         return self._format_error("Deployment blocked", "Invalid confirmation token")
            
    #     # This function needs to be implemented in qc_cloud.py
    #     return await deploy_live_with_confirmation(
    #         project_name, 
    #         environment,
    #         confirmation_token
    #     )
    
    # def _validate_confirmation_token(self, token: str) -> bool:
    #     """Placeholder for validating deployment confirmation."""
    #     # Implement actual token validation logic (e.g., compare with a generated token)
    #     print(f"Validating confirmation token: {token}")
    #     return token == "CONFIRM_DEPLOY"

    # --------------------------
    # Data Management Tools
    # --------------------------

    @Tool(
        name="download_market_data",
        description="(Placeholder) Fetch market data from QuantConnect",
        params={
            "symbol": "str",
            "resolution": "str",
            "start_date": "str",
            "end_date": "str"
        }
    )
    async def download_data(self,
                          symbol: str,
                          resolution: str = "daily",
                          start_date: str = "2010-01-01",
                          end_date: str = "2023-12-31") -> Dict:
        """
        Example Response (Placeholder):
        {
            "symbol": "SPY",
            "data_points": 3285,
            "resolution": "daily",
            "columns": ["open", "high", "low", "close", "volume"]
        }
        """
        # Implementation would call QC data API or LEAN CLI data commands
        print(f"Placeholder: Download data for {symbol}, {resolution} from {start_date} to {end_date}")
        # Example: Constructing a LEAN CLI command (requires verification)
        # command = f"data download --ticker {shlex.quote(symbol)} --resolution {resolution} --start {start_date} --end {end_date}"
        # result = await self.qc_bridge._execute_lean_command(command)
        # return result
        return {
            "status": "success",
            "message": "Data download not implemented yet.",
            "details": {
                 "symbol": symbol,
                 "resolution": resolution,
                 "start_date": start_date,
                 "end_date": end_date
            }
        }

    # --------------------------
    # Project Management Tools
    # --------------------------

    @Tool(
        name="push_project",
        description="Sync local project changes with QuantConnect Cloud",
        params={"project_name": "str"}
    )
    async def push_project(self, project_name: str) -> Dict:
        """Explicitly pushes project changes to the cloud."""
        print(f"Explicitly pushing project: {project_name}")
        # Quoting handled by bridge method
        result = await self.qc_bridge.push_changes(project_name) 
        print(f"Push result: {result}")
        return result

    # --------------------------
    # Utility Methods
    # --------------------------

    def _validate_symbol(self, symbol: str):
        """Basic check for symbol format or whitelist (example)."""
        # Example: Allow common stock/crypto formats
        if not re.match(r'^[A-Z]{1,5}(USD)?$', symbol.upper()):
             raise ValueError(f"Invalid symbol format: {symbol}")
        
        # Optional: Check against a dynamic whitelist fetched from somewhere
        allowed = os.getenv("ALLOWED_SYMBOLS", "SPY,QQQ,AAPL,GOOG,BTCUSD,ETHUSD").split(',')
        if symbol.upper() not in allowed:
            raise ValueError(f"Symbol {symbol} not permitted in current configuration.")
        print(f"Symbol {symbol} validated.")

    def _format_error(self, context: str, message: str) -> Dict:
        """Standardizes error reporting for tools."""
        print(f"Error - Context: {context}, Message: {message}") # Log error server-side
        return {
            "status": "error",
            "context": context,
            "message": message, # Keep message concise for client
            "timestamp": datetime.utcnow().isoformat() + "Z" # Add Z for UTC
        }

    def _extract_backtest_id(self, cli_output: str) -> Optional[str]:
        """Parse backtest ID from LEAN CLI's 'cloud backtest' output."""
        # Example output: "Started backtest named 'Adjective Noun Animal' for project 'My Project' with backtestId XXX"
        # Or: "BacktestId: XXX"
        match = re.search(r"(?:backtestId|BacktestId)[:\s]+(\S+)", cli_output)
        if match:
            return match.group(1).strip()
        # Fallback or more specific regex needed if format varies
        print(f"Could not extract backtest ID from output: {cli_output[:100]}...")
        return None

# --------------------------
# Resource Definitions
# --------------------------

class TradingResources:
    # Note: Resource access methods should ideally be async if they perform I/O
    # Making list_projects async in the bridge would be better.
    # For now, assume it's synchronous or wrapped appropriately elsewhere.
    cloud_projects = Resource(
        name="cloud_projects",
        description="List of available QuantConnect Cloud projects (Placeholder Data)",
        # This lambda calls the method on an instance
        access_method=lambda: QuantConnectCloudBridge().list_projects()
    )

    # Example: Reading from a file requires the file to exist in the container
    risk_parameters = Resource(
        name="risk_parameters",
        description="Current risk management settings (reads from ./config/risk_settings.json)",
        access_path="./config/risk_settings.json" 
        # Ensure this path is valid within the container and the file exists.
        # Might need to adjust path relative to WORKDIR or mount a config volume.
    )

# Example instantiation (usually done within the MCP Server)
# tools_instance = TradingTools()
# resources_instance = TradingResources()
# server.add_tools(tools_instance.get_tools()) # Assuming a method to get all tools
# server.add_resources([resources_instance.cloud_projects, resources_instance.risk_parameters]) 