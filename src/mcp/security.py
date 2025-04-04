from typing import List, Optional

class OAuth2Authenticator:
    """
    Simple OAuth2 authenticator for the MCP server.
    """
    
    def __init__(self, allowed_domains: List[str] = None, auto_approve_tools: List[str] = None):
        self.allowed_domains = allowed_domains or []
        self.auto_approve_tools = auto_approve_tools or []
        
    def authenticate(self, token: str) -> bool:
        """
        Authenticate a token.
        In a real implementation, this would validate the token with an OAuth provider.
        """
        # For this prototype, we'll just return True
        return True
        
    def authorize(self, token: str, tool_name: str) -> bool:
        """
        Authorize a token for a specific tool.
        """
        # For this prototype, we'll just check if the tool is in the auto-approve list
        return tool_name in self.auto_approve_tools
