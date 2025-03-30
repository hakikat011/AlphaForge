import pytest
import os
from unittest.mock import patch, MagicMock

# Mock the environment variable before importing the module
# Set a dummy key for testing purposes
@pytest.fixture(autouse=True)
def mock_env_vars(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-api-key")

# Now import the module that uses the env var
from src.nlp.gemini_parser import parse_gemini_response

# Mock the google.generativeai client
@patch('src.nlp.gemini_parser.genai.GenerativeModel')
def test_parser_success(mock_generative_model):
    """Test successful parsing of a simulated Gemini response."""
    # Configure the mock model and its response
    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    # Simulate a realistic JSON output structure based on the improved prompt
    mock_response.text = '''
    ```json
    {
        "action": "backtest",
        "strategy_details": "50-day moving average",
        "symbols": ["SPY"],
        "start_date": "2022-01-01", 
        "end_date": null, 
        "strategy_type": "moving_average",
        "parameters": { "window": 50 }
    }
    ```
    '''
    mock_model_instance.generate_content.return_value = mock_response
    mock_generative_model.return_value = mock_model_instance

    test_input = "Backtest SPY with 50-day moving average from 2022-01-01"
    result = parse_gemini_response(test_input)

    # Assertions
    assert result["action"] == "backtest"
    assert "SPY" in result["symbols"]
    assert result["start_date"] == "2022-01-01"
    assert result["strategy_type"] == "moving_average"
    assert result["parameters"]["window"] == 50
    assert "error" not in result # Check that no error field is present

    # Verify that generate_content was called correctly
    mock_model_instance.generate_content.assert_called_once()
    call_args, _ = mock_model_instance.generate_content.call_args
    assert test_input in call_args[0] # Check if user input is in the prompt

@patch('src.nlp.gemini_parser.genai.GenerativeModel')
def test_parser_json_decode_error(mock_generative_model):
    """Test handling of invalid JSON response from Gemini."""
    mock_model_instance = MagicMock()
    mock_response = MagicMock()
    mock_response.text = 'This is not valid JSON'
    mock_model_instance.generate_content.return_value = mock_response
    mock_generative_model.return_value = mock_model_instance

    test_input = "Some input that causes invalid JSON"
    result = parse_gemini_response(test_input)

    # Assertions for error handling
    assert "error" in result
    assert "Failed to parse Gemini response as JSON" in result["error"]
    assert result["raw_response"] == 'This is not valid JSON'
    # Check if fallback values are present
    assert result["action"] == "backtest" 
    assert "SPY" in result["symbols"]

@patch('src.nlp.gemini_parser.genai.GenerativeModel')
def test_parser_api_error(mock_generative_model):
    """Test handling of API errors during Gemini interaction."""
    mock_model_instance = MagicMock()
    # Simulate an exception being raised by the API call
    mock_model_instance.generate_content.side_effect = Exception("API connection failed")
    mock_generative_model.return_value = mock_model_instance

    test_input = "Input causing API error"
    result = parse_gemini_response(test_input)

    # Assertions for error handling
    assert "error" in result
    assert "Gemini API interaction failed" in result["error"]
    assert "API connection failed" in result["error"] 

# Note: To run these tests, you'll need pytest and pytest-mock (or just mock if using standard unittest)
# Install: pip install pytest pytest-mock python-dotenv 