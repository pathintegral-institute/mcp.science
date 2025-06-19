#!/usr/bin/env python

"""
MCP server for executing local Mathematica (Wolfram Script) code and returning the output.
Python version.
"""

import subprocess
import logging
import json
import asyncio
from typing import List, Literal, Optional

from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent

# --- Logging Setup ---
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger("mathematica-check")

# --- MCP Server Initialization ---
mcp = FastMCP(
    name="mathematica-check",
    version="0.1.0",
)

# --- Mathematica Interaction Logic ---

_mathematica_checked = False
_mathematica_available = False


async def check_mathematica_installation() -> bool:
    """Checks if wolframscript is installed and accessible."""
    global _mathematica_checked, _mathematica_available
    if _mathematica_checked:
        return _mathematica_available

    logger.info("Checking Mathematica (wolframscript) installation...")
    try:
        process = await asyncio.create_subprocess_exec(
            "wolframscript", "-help", stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            logger.info("Mathematica installation verified.")
            _mathematica_available = True
        else:
            logger.error(
                f"wolframscript -help exited with code {process.returncode}. Stderr: {stderr.decode()}"
            )
            _mathematica_available = False
    except FileNotFoundError:
        logger.error("Mathematica (wolframscript) not found in PATH.")
        _mathematica_available = False
    except Exception as e:
        logger.error(
            f"Error checking Mathematica installation: {e}", exc_info=True)
        _mathematica_available = False

    _mathematica_checked = True
    return _mathematica_available


async def execute_mathematica_code(code: str, format: str = "text") -> str:
    """Executes Mathematica code using wolframscript."""
    command = ["wolframscript", "-format", format.lower(), "-code", code]

    # Avoid logging potentially large code
    logger.info(
        f"Executing Mathematica command: {' '.join(command[:3])} -code '<code>...'"
    )
    try:
        process = await asyncio.create_subprocess_exec(
            *command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        stdout, stderr = await process.communicate()

        stdout_str = stdout.decode().strip()
        stderr_str = stderr.decode().strip()

        if process.returncode != 0:
            logger.error(
                f"wolframscript execution failed (Code: {process.returncode}). Stderr: {stderr_str}. Stdout: {stdout_str}"
            )
            raise RuntimeError(
                f"Mathematica execution failed: {stderr_str or stdout_str or 'Unknown error'}"
            )

        if stderr_str:
            logger.warning(
                f"Mathematica execution produced stderr: {stderr_str}")

        logger.info("Mathematica execution completed successfully.")
        return stdout_str

    except FileNotFoundError:
        logger.error(
            "wolframscript command not found. Is Mathematica installed and in PATH?"
        )
        raise RuntimeError("wolframscript command not found.")
    except Exception as e:
        logger.error(f"Failed to execute Mathematica code: {e}", exc_info=True)
        raise RuntimeError(f"Failed to execute Mathematica code: {e}")


async def verify_derivation_steps(steps: List[str], format: str = "text") -> str:
    """Verifies a mathematical derivation by checking equivalence between steps."""
    if len(steps) < 2:
        raise ValueError("At least two steps are required for a derivation.")

    logger.info(f"Verifying derivation with {len(steps)} steps.")

    # Safely embed the list of steps into Mathematica code
    # Using JSON ensures proper escaping of special characters within steps
    steps_json = json.dumps(steps)

    verification_code = f"""
      steps = {steps_json};
      results = {{}};

      (* Check if each step follows from the previous *)
      For[i = 2, i <= Length[steps], i++,
        prevExpr = Check[ToExpression[steps[[i-1]], InputForm, Hold], $Failed];
        currentExpr = Check[ToExpression[steps[[i]], InputForm, Hold], $Failed];

        equivalent = False;
        errorMsg = "";

        If[prevExpr === $Failed || currentExpr === $Failed,
            errorMsg = "Syntax error in step expression.";
            equivalent = False;,

            (* Use TimeConstrained to prevent hangs on complex Simplify *)
            result = TimeConstrained[Simplify[ReleaseHold[prevExpr] == ReleaseHold[currentExpr]], 5, $TimedOut];
            If[result === $TimedOut,
                errorMsg = "Simplification timed out.";
                equivalent = False;,
                If[!MemberQ[{{True, False}}, result],
                    errorMsg = "Simplification failed or produced unexpected result.";
                    equivalent = False;
                ,
                    equivalent = result;
                ];
            ];
        ];

        AppendTo[results, <|
          "step" -> i,
          "expression" -> steps[[i]],
          "equivalent" -> equivalent,
          "error" -> errorMsg
        |>];
      ];

      (* Format the results *)
      formattedResults = "Derivation Verification Results:\\n\\n";

      For[i = 1, i <= Length[results], i++,
        result = results[[i]];
        stepNum = result["step"];
        expr = result["expression"];
        isEquiv = result["equivalent"];
        errMsg = result["error"];

        formattedResults = formattedResults <>
          "Step " <> ToString[stepNum] <> ": " <> expr <> "\\n" <>
          "  Valid: " <> ToString[isEquiv];
        If[errMsg =!= "",
           formattedResults = formattedResults <> "\\n  Note: " <> errMsg;
        ];
         formattedResults = formattedResults <> "\\n\\n";
      ];

      (* Ensure final output is a string *)
      ToString[formattedResults, OutputForm]
    """
    return await execute_mathematica_code(verification_code, format)


# --- MCP Tool Definitions ---


@mcp.tool()
async def execute_mathematica(
    code: str, format: Optional[Literal["text", "mathematica"]] = "text"
) -> TextContent:
    """
    Execute Mathematica code and return the result.

    IMPORTANT: Each code block should be self-contained and complete. Variables, functions, 
    or definitions from previous executions are not preserved between calls.

    Args:
        code: Mathematica code to execute. Should be a complete, self-contained code block.
        format: Output format (text, latex, or mathematica). Defaults to text.

    Returns:
        The result of the execution as text.

    Raises:
        RuntimeError: If Mathematica execution fails or wolframscript is not found.
        ValueError: If the input code is empty.
    """
    logger.info(f"Received execute_mathematica request (format: {format})")

    if not await check_mathematica_installation():
        raise RuntimeError(
            "Mathematica (wolframscript) is not installed or not accessible. Please ensure it's in your PATH."
        )

    if not code:
        raise ValueError("Mathematica code cannot be empty.")

    result = await execute_mathematica_code(code, format)
    return TextContent(type="text", text=result)


@mcp.tool()
async def verify_derivation(
    steps: List[str], format: Optional[Literal["text", "mathematica"]] = "text"
) -> TextContent:
    """
    Verify a mathematical derivation step by step using Mathematica's Simplify.

    Checks if Simplify[step_i == step_{i-1}] evaluates to True for i > 1.

    IMPORTANT: Each step expression should be self-contained and valid Mathematica syntax.
    The verification is performed in a single execution, so all steps are processed together.

    Args:
        steps: Array of mathematical expressions (as strings) representing steps in a derivation. Requires at least two steps.
        format: Output format for the verification report (text, latex, or mathematica). Defaults to text.

    Returns:
        A report indicating the validity of each step.

    Raises:
        RuntimeError: If Mathematica execution fails or wolframscript is not found.
        ValueError: If the input steps are invalid (e.g., not a list, < 2 steps).
    """
    logger.info(
        f"Received verify_derivation request ({len(steps)} steps, format: {format})"
    )

    if not await check_mathematica_installation():
        raise RuntimeError(
            "Mathematica (wolframscript) is not installed or not accessible. Please ensure it's in your PATH."
        )

    if not steps or not isinstance(steps, list) or len(steps) < 2:
        raise ValueError(
            "At least two derivation steps (as a list of strings) are required."
        )

    result = await verify_derivation_steps(steps, format)
    return TextContent(type="text", text=result)


# --- Main Execution ---


def main():
    """Runs the MCP server."""
    logger.info("Starting Mathematica MCP server (Python)...")
    # Use the standard run method, which handles the loop for async tools
    mcp.run("stdio")


if __name__ == "__main__":
    main()
