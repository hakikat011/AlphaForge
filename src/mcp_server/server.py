from mcp import McpServer, Tool, Resource
from .bridge import LeanBridge
# Removed unused Resource import

class AlphaForgeServer(McpServer):
    def __init__(self):
        # Added authenticator initialization from security baseline
        from mcp.security import OAuth2Authenticator
        super().__init__(name="AlphaForge v1.0")
        self.authenticator = OAuth2Authenticator(
            allowed_domains=["quantconnect.com"], 
            auto_approve_tools=["backtest_strategy"]
        )
        self.lean = LeanBridge()
        self.register_tools()

    def register_tools(self):
        @Tool(
            name="backtest_strategy",
            description="Run LEAN backtest from natural language input",
            params={"strategy_description": "str"}
        )
        async def backtest(_, strategy_description: str):
            # Step 1: Parse Gemini input
            # Corrected import path relative to server.py
            from ..nlp.gemini_parser import parse_gemini_response 
            config = parse_gemini_response(strategy_description)
            
            # Step 2: Execute LEAN - Placeholder, needs actual strategy logic
            # The config currently contains placeholders
            # We need a way to map config to an actual LEAN command/file
            # Example: Assume config['algorithm_path'] is generated or mapped
            # For v1, let's assume a fixed path or a simple mapping logic
            # This part requires further definition based on Gemini output and LEAN setup
            algorithm_path = config.get('algorithm_path', 'BasicTemplateAlgorithm') # Default or derived path
            lean_command = f"backtest {algorithm_path}" 
            # Example: Add parameters if needed: --start-date {config['start_date']}

            print(f"Executing LEAN command: {lean_command}") # Logging
            result = await self.lean.execute(lean_command)
            print(f"LEAN execution result: {result}") # Logging

            # Step 3: Format and return result (needs refinement)
            # The example output format doesn't match the LeanBridge output
            # Adapt this based on actual needs
            return {
                "status": "success" if result.get("success") else "error",
                # Placeholder for actual results processing
                "details": result.get("output") or result.get("error") 
            }
            
        self.add_tools([backtest])

if __name__ == "__main__":
    print("Starting AlphaForge v1.0 MCP Server...")
    server = AlphaForgeServer()
    # Added authenticator to run method
    server.run(host="0.0.0.0", port=8080, authenticator=server.authenticator) 
    print("AlphaForge v1.0 MCP Server stopped.") 