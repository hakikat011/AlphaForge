import subprocess
import asyncio

class LeanBridge:
    async def execute(self, command: str):
        """Execute LEAN CLI command inside the container"""
        # Ensure the command is executed in the context where LEAN CLI is available
        # This might depend on the docker setup (e.g., executing within lean_engine service or ensuring LEAN CLI is in mcp_server)
        # For now, assuming `lean` is accessible in the environment where this script runs.
        full_command = f"lean {command}" # Consider adding path to lean if not in PATH
        print(f"Executing command: {full_command}")
        try:
            process = await asyncio.create_subprocess_shell(
                full_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            # Decode stdout and stderr, handling potential decoding errors
            stdout_decoded = stdout.decode(errors='replace') if stdout else ""
            stderr_decoded = stderr.decode(errors='replace') if stderr else ""

            print(f"Return Code: {process.returncode}")
            print(f"STDOUT:\n{stdout_decoded}")
            print(f"STDERR:\n{stderr_decoded}")

            return {
                "success": process.returncode == 0,
                "output": stdout_decoded,
                "error": stderr_decoded,
                "return_code": process.returncode
            }
        except FileNotFoundError:
            print("Error: 'lean' command not found. Is LEAN CLI installed and in PATH?")
            return {
                "success": False,
                "output": "",
                "error": "'lean' command not found. Check LEAN installation and PATH.",
                "return_code": -1
            }
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return {
                "success": False,
                "output": "",
                "error": f"An unexpected error occurred: {str(e)}",
                "return_code": -1
            } 