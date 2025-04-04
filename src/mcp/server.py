import asyncio
import uvicorn
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Callable, Dict, Any, Optional, Union
from .tools import Tool, Resource
from .security import OAuth2Authenticator

class McpServer:
    """
    Model-Centric Programming (MCP) Server
    Provides a framework for exposing tools and resources via an API.
    """

    def __init__(self, name: str = "MCP Server"):
        self.name = name
        self.tools = []
        self.resources = []
        self.authenticator = None
        self.app = FastAPI(title=name, description=f"{name} API")
        self._setup_routes()

    def _setup_routes(self):
        """Set up API routes."""
        @self.app.get("/")
        async def root():
            return {"message": f"Welcome to {self.name}", "version": "1.0"}

        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy"}

    def add_tools(self, tools: List[Callable]):
        """Add tools to the server."""
        self.tools.extend(tools)

        # Register each tool as an API endpoint
        for tool in tools:
            if hasattr(tool, 'name') and hasattr(tool, 'description') and hasattr(tool, 'params'):
                route_path = f"/tools/{tool.name}"

                # Create a dynamic route handler for this tool
                async def create_tool_endpoint(request: Request, tool_func=tool):
                    # Parse request body
                    try:
                        data = await request.json()
                    except Exception:
                        data = {}

                    # Check authentication if required
                    if hasattr(tool_func, 'require_auth') and tool_func.require_auth and self.authenticator:
                        auth_header = request.headers.get('Authorization')
                        if not auth_header or not auth_header.startswith('Bearer '):
                            raise HTTPException(status_code=401, detail="Authentication required")
                        token = auth_header.replace('Bearer ', '')
                        if not self.authenticator.authenticate(token):
                            raise HTTPException(status_code=401, detail="Invalid authentication token")
                        if not self.authenticator.authorize(token, tool_func.name):
                            raise HTTPException(status_code=403, detail="Not authorized to use this tool")

                    # Execute the tool with the provided parameters
                    try:
                        result = await tool_func(self, **data)
                        return result
                    except Exception as e:
                        return JSONResponse(
                            status_code=500,
                            content={"error": f"Tool execution failed: {str(e)}"}
                        )

                # Register the endpoint
                self.app.post(route_path)(create_tool_endpoint)
                print(f"Registered tool endpoint: {route_path}")

    def add_resources(self, resources: List[Resource]):
        """Add resources to the server."""
        self.resources.extend(resources)

        # Register each resource as an API endpoint
        for resource in resources:
            if hasattr(resource, 'name') and hasattr(resource, 'description'):
                route_path = f"/resources/{resource.name}"

                # Create a dynamic route handler for this resource
                async def create_resource_endpoint(resource_obj=resource):
                    try:
                        return resource_obj.get_data()
                    except Exception as e:
                        return JSONResponse(
                            status_code=500,
                            content={"error": f"Resource access failed: {str(e)}"}
                        )

                # Register the endpoint
                self.app.get(route_path)(create_resource_endpoint)
                print(f"Registered resource endpoint: {route_path}")

    def run(self, host: str = "0.0.0.0", port: int = 8080, authenticator: Optional[OAuth2Authenticator] = None):
        """Run the server."""
        self.authenticator = authenticator
        print(f"Starting {self.name} on {host}:{port}")
        print(f"Server is running with {len(self.tools)} tools and {len(self.resources)} resources")

        # Start the FastAPI server
        uvicorn.run(self.app, host=host, port=port)
