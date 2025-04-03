import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure the Gemini client
try:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    genai.configure(api_key=api_key)
except ValueError as e:
    print(f"Error configuring Gemini: {e}")
    # Handle the error appropriately - exit, raise, or use a default config
    # For now, we'll print and potentially fail later when the model is used.
except Exception as e:
    print(f"An unexpected error occurred during Gemini configuration: {e}")

def parse_gemini_response(user_input: str) -> dict:
    """Uses Gemini to parse user input into a structured JSON config."""
    try:
        model = genai.GenerativeModel('gemini-pro')
        
        # Improved prompt with clearer instructions and example
        prompt = f"""
        [SYSTEM] You are a helpful assistant that converts natural language trading strategy requests into a structured JSON format suitable for the LEAN engine. Focus on extracting key parameters for backtesting.

        USER: {user_input}

        TEMPLATE: {{"action":"backtest", "strategy_details": "<description>", "symbols": ["<symbol1>", "<symbol2>"], "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD", "strategy_type": "<e.g., mean_reversion, trend_following, custom_indicator>", "parameters": {{ "<param_name>": "<param_value>" }} }}

        Based *only* on the USER input, fill the TEMPLATE. If a value isn't mentioned, use a reasonable default or leave it empty if appropriate (e.g., end_date can often be omitted).

        Example:
        USER: Backtest a simple moving average crossover on SPY from 2021-01-01 to 2023-12-31 using 50 and 200 day SMAs.
        JSON_OUTPUT: {{"action":"backtest", "strategy_details": "simple moving average crossover using 50 and 200 day SMAs", "symbols": ["SPY"], "start_date": "2021-01-01", "end_date": "2023-12-31", "strategy_type": "moving_average_crossover", "parameters": {{ "short_window": 50, "long_window": 200 }} }}
        
        Now, process the actual user input:
        USER: {user_input}
        JSON_OUTPUT:
        """
        
        print(f"Sending prompt to Gemini:\n{prompt}") # Log the prompt
        response = model.generate_content(prompt)
        
        print(f"Raw Gemini Response Text:\n{response.text}") # Log the raw response

        # Attempt to parse the response text as JSON
        try:
            # Basic cleaning: remove potential backticks and language identifiers
            cleaned_response_text = response.text.strip().strip("`json\n`").strip("`")
            parsed_json = json.loads(cleaned_response_text)
            print(f"Successfully parsed JSON: {parsed_json}")
            
            # Basic validation (can be expanded)
            if not isinstance(parsed_json, dict) or "action" not in parsed_json:
                print("Warning: Parsed JSON might be invalid or incomplete.")
                # Fallback or raise error
                raise ValueError("Parsed JSON is not a valid dictionary or missing 'action' key.")
            
            # Ensure required fields for cloud deployment
            required_fields = ["action", "symbols", "strategy_type"]
            missing_fields = [field for field in required_fields if field not in parsed_json]
            if missing_fields:
                raise ValueError(f"Missing required fields for cloud deployment: {missing_fields}")
            
            return parsed_json
            
        except json.JSONDecodeError as e:
            print(f"Error decoding Gemini response JSON: {e}")
            print(f"Problematic response text: {response.text}")
            # Fallback mechanism: Return a default or error structure
            return {
                "error": "Failed to parse Gemini response as JSON",
                "raw_response": response.text,
                # Include placeholders based on the original v1 implementation
                "action": "backtest",
                "symbols": ["SPY"],  
                "start_date": "2020-01-01",
                "strategy_type": "mean_reversion"
            }
        except Exception as e:
            print(f"An unexpected error occurred during JSON parsing: {e}")
            return {"error": f"Unexpected JSON parsing error: {str(e)}", "raw_response": response.text}

    except AttributeError:
         # Handle cases where the response object doesn't have the expected structure
        print(f"Error: Unexpected response structure from Gemini API.")
        try:
            print(f"Full Gemini Response object: {response}") 
        except NameError:
             print("Gemini response object not available.")
        return {"error": "Unexpected response structure from Gemini API."}
    except Exception as e:
        print(f"An error occurred interacting with the Gemini API: {e}")
        # Check if 'response' exists before trying to access '.text'
        raw_response_text = "<Response object not available>"
        if 'response' in locals() and hasattr(response, 'text'):
            raw_response_text = response.text
        return {"error": f"Gemini API interaction failed: {str(e)}", "raw_response": raw_response_text}

# Example usage (for testing):
if __name__ == "__main__":
    test_input = "Backtest SPY with RSI < 30 strategy starting from 2022-05-01"
    print(f"Testing with input: {test_input}")
    result = parse_gemini_response(test_input)
    print(f"\nFinal Parsed Result:\n{json.dumps(result, indent=2)}")

    test_input_complex = "I want to backtest a mean reversion strategy for AAPL and GOOG, using a 20-day lookback period, from the start of 2021 until today."
    print(f"\nTesting with complex input: {test_input_complex}")
    result_complex = parse_gemini_response(test_input_complex)
    print(f"\nFinal Parsed Result (Complex):\n{json.dumps(result_complex, indent=2)}") 