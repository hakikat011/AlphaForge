from mcp import McpServer, Tool, Resource
from mcp.security import OAuth2Authenticator # Import authenticator directly
from .bridge import LeanBridge
from ..integrations.qc_cloud import QuantConnectCloudBridge
# Import the new tools and resources classes
from .tools import TradingTools, TradingResources

class AlphaForgeServer(McpServer):
    def __init__(self):
        super().__init__(name="AlphaForge v1.0")
        
        # Initialize tools and resources first
        self.trading_tools = TradingTools()
        self.trading_resources = TradingResources()
        
        # Initialize other components
        self.lean = LeanBridge() # Local LEAN bridge (if used)
        self.qc_cloud = self.trading_tools.qc_bridge # Use the instance from TradingTools
        
        # Configure authenticator
        self.authenticator = OAuth2Authenticator(
            allowed_domains=["quantconnect.com"], # Example domain
            # Update tools approved for auto-run if needed
            auto_approve_tools=["cloud_backtest", "push_project", "download_market_data"]
        )
        
        # Register tools and resources
        self.register_tools()
        self.register_resources() # Call the new method

    def register_tools(self):
        """Registers tools available on the server."""
        # Define the original local backtest tool (if still needed)
        @Tool(
            name="local_backtest_strategy", # Renamed to avoid conflict
            description="Run LEAN backtest LOCALLY from natural language input",
            params={"strategy_description": "str"}
        )
        async def local_backtest(_, strategy_description: str):
            from ..nlp.gemini_parser import parse_gemini_response 
            config = parse_gemini_response(strategy_description)
            
            # Simplified example: Assume parser gives a path or name
            algorithm_identifier = config.get('algorithm_path', config.get('strategy_type', 'BasicTemplateAlgorithm'))
            lean_command = f"backtest {algorithm_identifier}" 

            print(f"Executing LOCAL LEAN command: {lean_command}")
            result = await self.lean.execute(lean_command)
            print(f"LOCAL LEAN execution result: {result}")

            return {
                "status": "success" if result.get("success") else "error",
                "details": result.get("output") or result.get("error") 
            }

        # Get tools from the TradingTools instance
        trading_tool_methods = [
            self.trading_tools.cloud_backtest,
            self.trading_tools.push_project,
            self.trading_tools.download_data
            # Add self.trading_tools.deploy_live here when implemented
        ]
        
        # Combine local tools (if any) and trading tools
        all_tools = [local_backtest] + trading_tool_methods
        self.add_tools(all_tools)
        print(f"Registered tools: {[tool.name for tool in all_tools]}")

    def register_resources(self):
        """Registers resources available on the server."""
        resources_list = [
            self.trading_resources.cloud_projects,
            self.trading_resources.risk_parameters
        ]
        self.add_resources(resources_list)
        print(f"Registered resources: {[res.name for res in resources_list]}")


if __name__ == "__main__":
    print("Starting AlphaForge v1.0 MCP Server...")
    server = AlphaForgeServer()
    # Run the server with the authenticator
    server.run(host="0.0.0.0", port=8080, authenticator=server.authenticator)
    print("AlphaForge v1.0 MCP Server stopped.") 