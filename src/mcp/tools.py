import json
import os
from typing import Callable, Dict, Any, List, Optional

class Tool:
    """
    Decorator for defining tools that can be exposed via the MCP server.
    """
    
    def __init__(self, name: str, description: str, params: Dict[str, str], require_auth: bool = False):
        self.name = name
        self.description = description
        self.params = params
        self.require_auth = require_auth
        self.func = None
    
    def __call__(self, func):
        self.func = func
        # Add tool metadata to the function
        func.name = self.name
        func.description = self.description
        func.params = self.params
        func.require_auth = self.require_auth
        return func


class Resource:
    """
    Defines a resource that can be accessed via the MCP server.
    """
    
    def __init__(self, name: str, description: str, access_method: Optional[Callable] = None, access_path: Optional[str] = None):
        self.name = name
        self.description = description
        self.access_method = access_method
        self.access_path = access_path
        
    def get_data(self) -> Dict[str, Any]:
        """Get the resource data."""
        if self.access_method:
            return self.access_method()
        elif self.access_path and os.path.exists(self.access_path):
            with open(self.access_path, 'r') as f:
                return json.load(f)
        else:
            return {"error": "Resource not available"}
