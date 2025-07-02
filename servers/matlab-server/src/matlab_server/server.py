#!/usr/bin/env python

"""
MCP server for executing local MATLAB code and returning the output.
"""

import subprocess
import logging
import json
import asyncio
import os
import tempfile
import base64
from typing import List, Literal, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, ImageContent, ErrorContent

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("matlab-server")

# --- MCP Server Initialization ---
mcp = FastMCP(
    name="matlab-server",
    version="0.1.0",
    description="An MCP server to execute MATLAB code.",
)

# --- MATLAB Interaction Logic ---

_matlab_checked = False
_matlab_available = False


async def check_matlab_installation() -> bool:
    """Checks if MATLAB is installed and accessible."""
    global _matlab_checked, _matlab_available
    if _matlab_checked:
        return _matlab_available

    logger.info("Checking MATLAB installation...")
    # Command to check MATLAB, e.g., by requesting help or version.
    # Using -nodesktop and -nosplash for faster startup and no GUI.
    # `exit` is often needed to make MATLAB actually quit after a simple command.
    # Using `matlab -help` might be too verbose or platform-dependent in its success code.
    # A simple, non-crashing command like `1+1; exit` is better.
    try:
        process = await asyncio.create_subprocess_exec(
            "matlab", "-batch", "disp('MATLAB OK'); exit;",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0 and b"MATLAB OK" in stdout:
            logger.info("MATLAB installation verified.")
            _matlab_available = True
        else:
            logger.error(
                f"MATLAB check command exited with code {process.returncode}. Stdout: {stdout.decode(errors='ignore')}, Stderr: {stderr.decode(errors='ignore')}"
            )
            _matlab_available = False
    except FileNotFoundError:
        logger.error("MATLAB command not found in PATH. Please ensure MATLAB is installed and its bin directory is in the system PATH.")
        _matlab_available = False
    except Exception as e:
        logger.error(f"Error checking MATLAB installation: {e}", exc_info=True)
        _matlab_available = False

    _matlab_checked = True
    return _matlab_available


async def execute_matlab_code(code: str, output_format: Literal["text", "plot"] = "text") -> tuple[str, Optional[str]]:
    """
    Executes MATLAB code using 'matlab -batch'.

    Args:
        code: The MATLAB code to execute.
        output_format: "text" for textual output, "plot" for plot output (returns base64 PNG).

    Returns:
        A tuple containing:
        - The primary output (text or base64 PNG string).
        - An optional string for stderr messages if any.

    Raises:
        RuntimeError: If MATLAB execution fails or MATLAB is not found.
    """
    if not await check_matlab_installation():
        raise RuntimeError(
            "MATLAB is not installed, not found in PATH, or not configured correctly."
        )

    temp_plot_file = None
    matlab_command_code = code

    if output_format == "plot":
        # Create a temporary file for the plot
        # MATLAB will save the plot to this file.
        # We use a unique filename to avoid collisions.
        # The .png extension is important for MATLAB's print command.
        fd, temp_plot_file_path = tempfile.mkstemp(suffix=".png")
        os.close(fd) # Close the file descriptor, MATLAB will open and write to it.
        temp_plot_file = temp_plot_file_path

        # Sanitize the path for MATLAB (especially on Windows)
        safe_plot_file_path = temp_plot_file.replace('\\', '/')

        # Add MATLAB commands to save the current figure and then exit
        # The user's code should generate a figure. We then save it.
        # `print('-dpng', '{filepath}')` saves the current figure.
        # We add `exit;` to ensure MATLAB closes after execution.
        matlab_command_code = f"""
        try
            {code}
            % Check if a figure exists before trying to save
            if ~isempty(get(groot,'CurrentFigure'))
                print('-dpng', '{safe_plot_file_path}');
            else
                disp('MATLAB_WARNING: No figure was generated to save.');
            end
        catch ME
            disp(['MATLAB_ERROR: ' ME.message]);
            % Optional: rethrow(ME); % if we want MATLAB to exit with error code for script errors
        end
        exit; % Ensure MATLAB exits
        """
        logger.info(f"Preparing to execute MATLAB for plot, saving to: {temp_plot_file}")
    else: # text output
        matlab_command_code = f"""
        try
            {code}
        catch ME
            disp(['MATLAB_ERROR: ' ME.message]);
        end
        exit; % Ensure MATLAB exits
        """

    command = ["matlab", "-batch", matlab_command_code]
    logger.info(f"Executing MATLAB command: matlab -batch \"{matlab_command_code[:100]}...\"")

    try:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        stdout_str = stdout.decode(errors='ignore').strip()
        stderr_str = stderr.decode(errors='ignore').strip()

        if "MATLAB_ERROR:" in stdout_str: # Check for our custom error prefix
             # If specific error handling from MATLAB output is needed
            logger.error(f"MATLAB execution reported an error within the script: {stdout_str}")
            # Depending on desired behavior, we might want to raise this as an error
            # or return it as part of the output. For now, returning it in stdout.

        if process.returncode != 0:
            # Even if code has `exit;`, MATLAB might return non-zero for internal errors
            # or if the `exit;` command is not reached due to a script crash.
            error_message = f"MATLAB process exited with code {process.returncode}."
            if stdout_str:
                error_message += f" Stdout: {stdout_str}"
            if stderr_str: # This stderr is from the matlab process itself, not user script's stderr.
                error_message += f" Stderr: {stderr_str}"
            logger.error(error_message)
            # Decide if this should always raise RuntimeError or if some non-zero exits are "ok"
            # For now, let's be strict.
            raise RuntimeError(f"MATLAB execution failed: {error_message}")

        if stderr_str: # Process-level stderr
            logger.warning(f"MATLAB process produced stderr: {stderr_str}")


        if output_format == "plot":
            if temp_plot_file and os.path.exists(temp_plot_file) and os.path.getsize(temp_plot_file) > 0:
                with open(temp_plot_file, "rb") as f:
                    image_data = base64.b64encode(f.read()).decode("utf-8")
                logger.info(f"Successfully read plot image from {temp_plot_file}")
                return image_data, stdout_str # stdout might contain warnings like "No figure generated"
            elif "MATLAB_WARNING: No figure was generated to save." in stdout_str:
                 logger.warning("MATLAB script ran, but no plot was generated or saved.")
                 return "", stdout_str # Return empty image data, but include the warning
            else:
                logger.error(f"Plot file {temp_plot_file} was not created or is empty.")
                # Include stdout in case it has error messages from MATLAB
                raise RuntimeError(f"Failed to generate plot. MATLAB output: {stdout_str}")
        else: # text output
            return stdout_str, None # No separate stderr from script for text, it's part of stdout

    except FileNotFoundError:
        logger.error("`matlab` command not found. Is MATLAB installed and in PATH?")
        raise RuntimeError("`matlab` command not found. Ensure MATLAB is installed and its bin directory is in the system PATH.")
    except Exception as e:
        logger.error(f"Failed to execute MATLAB code: {e}", exc_info=True)
        raise RuntimeError(f"An unexpected error occurred during MATLAB execution: {e}")
    finally:
        if temp_plot_file and os.path.exists(temp_plot_file):
            os.remove(temp_plot_file)
            logger.info(f"Cleaned up temporary plot file: {temp_plot_file}")


# --- MCP Tool Definitions ---

@mcp.tool()
async def execute_matlab(
    code: str,
    output_format: Optional[Literal["text", "plot"]] = "text",
) -> TextContent | ImageContent | ErrorContent:
    """
    Execute MATLAB code and return the result.

    Args:
        code: MATLAB code to execute. Should be a complete, self-contained script.
              For plots, the code should generate a figure.
        output_format: "text" for textual output (default), or "plot" to capture
                       the current MATLAB figure as a PNG image.

    Returns:
        TextContent if output_format is "text".
        ImageContent if output_format is "plot" and a plot is successfully generated.
        ErrorContent if MATLAB is not found, execution fails, or a plot is requested but not generated.
    """
    logger.info(f"Received execute_matlab request (output_format: {output_format})")

    if not await check_matlab_installation():
        return ErrorContent(
            type="error",
            message="MATLAB (matlab command) is not installed or not accessible. Please ensure it's in your PATH and configured correctly.",
        )

    if not code:
        return ErrorContent(type="error", message="MATLAB code cannot be empty.")

    try:
        result, script_stdout_warnings = await execute_matlab_code(code, output_format)

        if output_format == "plot":
            if result: # result is base64 image data
                return ImageContent(type="image", format="png", base64=result)
            else: # No image data, means no plot was generated
                message = "MATLAB code executed, but no plot was generated or an error occurred."
                if script_stdout_warnings and "MATLAB_WARNING: No figure was generated to save." in script_stdout_warnings :
                    message = "MATLAB code executed, but no plot was generated."
                elif script_stdout_warnings: # Other warnings/errors from the script
                     message = f"MATLAB code executed, but no plot was generated. Output: {script_stdout_warnings}"
                return ErrorContent(type="error", message=message)
        else: # text output
            # If script_stdout_warnings is not None, it implies it's actually stdout from plot generation mode
            # that might contain warnings. For pure text mode, this should be None.
            # The primary output is in 'result'.
            return TextContent(type="text", text=result)

    except RuntimeError as e:
        return ErrorContent(type="error", message=str(e))
    except ValueError as e: # Should not happen if checks are done above
        return ErrorContent(type="error", message=str(e))
    except Exception as e: # Catchall for unexpected errors
        logger.error(f"Unexpected error in execute_matlab tool: {e}", exc_info=True)
        return ErrorContent(type="error", message=f"An unexpected server error occurred: {e}")


# --- Main Execution ---
def main():
    """Runs the MCP server."""
    logger.info("Starting MATLAB MCP server (Python)...")
    # Ensure MATLAB check runs at least once at startup, if desired,
    # though it's also run on first tool call.
    # asyncio.run(check_matlab_installation()) # Optional: run once at startup
    mcp.run("stdio")


if __name__ == "__main__":
    main()
