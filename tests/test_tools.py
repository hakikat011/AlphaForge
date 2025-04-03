import pytest
from unittest.mock import patch, MagicMock, AsyncMock # Import AsyncMock for async methods
import os # Import os for environment variable mocking

# Mock environment variables before other imports might need them
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("QC_PROJECTS_DIR", "./QuantConnect Projects")
    # Add other potentially used env vars if necessary for tool initialization
    # monkeypatch.setenv("ALLOWED_SYMBOLS", "SPY,QQQ")

# Import the class to test *after* setting up mocks if it uses env vars on import
from src.mcp_server.tools import TradingTools

@pytest.fixture
def trading_tools():
    """Provides an instance of TradingTools for testing."""
    # Use patch to avoid actual bridge initialization during TradingTools instantiation
    with patch('src.integrations.qc_cloud.QuantConnectCloudBridge') as mock_bridge_init:
        # Configure the mock bridge instance if needed for __init__
        mock_bridge_init.return_value = MagicMock()
        tools = TradingTools()
        # Assign the mock bridge instance to the tools instance for later use in tests
        # tools.qc_bridge = mock_bridge_init.return_value
        return tools

@pytest.mark.asyncio
async def test_cloud_backtest_success(trading_tools):
    """Tests the cloud_backtest tool for a successful scenario."""
    # Mock the QuantConnectCloudBridge methods used within cloud_backtest
    with patch.object(trading_tools.qc_bridge, 'push_changes', new_callable=AsyncMock) as mock_push, \
         patch.object(trading_tools.qc_bridge, 'submit_cloud_backtest', new_callable=AsyncMock) as mock_submit:

        # Configure the return values of the mocked async methods
        mock_push.return_value = {"success": True, "output": "Push successful"}
        mock_submit.return_value = {
            "success": True,
            "output": "Started backtest named 'Test Backtest' for project 'Test Project' with backtestId BT-12345"
            # Ensure output format matches what _extract_backtest_id expects
        }

        # Define test inputs
        project_name = "Test Project"
        strategy_parameters = {"symbol": "SPY", "window": 20} # Ensure symbol is valid per default ALLOWED_SYMBOLS
        backtest_name = "Test Backtest Run"

        # Call the tool method
        result = await trading_tools.cloud_backtest(
            project_name=project_name,
            strategy_parameters=strategy_parameters,
            backtest_name=backtest_name
        )

        # Assertions
        assert result["status"] == "success"
        assert result["backtest_id"] == "BT-12345"
        assert "details" in result
        assert result["details"]["success"] is True

        # Verify mocks were called correctly
        mock_push.assert_called_once_with(project_name)
        mock_submit.assert_called_once_with(project_name, backtest_name)

@pytest.mark.asyncio
async def test_cloud_backtest_push_failure(trading_tools):
    """Tests the cloud_backtest tool when the push_changes step fails."""
    with patch.object(trading_tools.qc_bridge, 'push_changes', new_callable=AsyncMock) as mock_push, \
         patch.object(trading_tools.qc_bridge, 'submit_cloud_backtest', new_callable=AsyncMock) as mock_submit:

        mock_push.return_value = {"success": False, "error": "Push failed due to permissions"}

        result = await trading_tools.cloud_backtest(
            project_name="FailPush Project",
            strategy_parameters={"symbol": "QQQ"},
            backtest_name="PushFail Test"
        )

        assert result["status"] == "error"
        assert result["context"] == "Push failed"
        assert "Push failed due to permissions" in result["message"]
        assert "backtest_id" not in result # Should not attempt submit

        mock_push.assert_called_once_with("FailPush Project")
        mock_submit.assert_not_called() # Verify submit wasn't called

@pytest.mark.asyncio
async def test_cloud_backtest_submit_failure(trading_tools):
    """Tests the cloud_backtest tool when the submit_cloud_backtest step fails."""
    with patch.object(trading_tools.qc_bridge, 'push_changes', new_callable=AsyncMock) as mock_push, \
         patch.object(trading_tools.qc_bridge, 'submit_cloud_backtest', new_callable=AsyncMock) as mock_submit:

        mock_push.return_value = {"success": True, "output": "Push successful"}
        mock_submit.return_value = {"success": False, "error": "Cloud resource limit reached"}

        result = await trading_tools.cloud_backtest(
            project_name="SubmitFail Project",
            strategy_parameters={"symbol": "AAPL"},
            backtest_name="SubmitFail Test"
        )

        assert result["status"] == "error"
        assert result["backtest_id"] is None # ID extraction should fail or return None
        assert result["details"]["success"] is False
        assert "Cloud resource limit reached" in result["details"]["error"]

        mock_push.assert_called_once_with("SubmitFail Project")
        mock_submit.assert_called_once_with("SubmitFail Project", "SubmitFail Test")

@pytest.mark.asyncio
async def test_cloud_backtest_invalid_symbol(trading_tools):
    """Tests validation failure for disallowed symbols."""
    with patch.object(trading_tools.qc_bridge, 'push_changes', new_callable=AsyncMock) as mock_push:
         # No need to mock submit as it shouldn't be reached

        result = await trading_tools.cloud_backtest(
            project_name="InvalidSymbol Project",
            strategy_parameters={"symbol": "INVALID"}, # Symbol not in default whitelist
            backtest_name="InvalidSymbol Test"
        )

        assert result["status"] == "error"
        assert result["context"] == "Validation Error"
        assert "Symbol INVALID not permitted" in result["message"]

        mock_push.assert_not_called() # Push should not happen if validation fails

# Add more tests for other tools (push_project, download_data) and edge cases.
# Example test for push_project:
@pytest.mark.asyncio
async def test_push_project(trading_tools):
     with patch.object(trading_tools.qc_bridge, 'push_changes', new_callable=AsyncMock) as mock_push:
        mock_push.return_value = {"success": True, "output": "Project pushed successfully."}

        project_name = "MyPushTestProject"
        result = await trading_tools.push_project(project_name)

        assert result["success"] is True
        assert "Project pushed successfully" in result["output"]
        mock_push.assert_called_once_with(project_name) 