import pytest
import asyncio
from unittest.mock import patch, MagicMock, mock_open, AsyncMock

# Make sure the server module can be imported.
# This might require adjustments to sys.path or pytest configuration depending on project structure.
# For now, assuming direct import works or will be handled by pytest's path adjustments.
from matlab_server.server import (
    check_matlab_installation,
    execute_matlab_code,
    execute_matlab as execute_matlab_tool, # MCP tool
    mcp, # For tool registration, if needed for testing context
    _matlab_checked, _matlab_available # To reset state between tests
)
from mcp.types import TextContent, ImageContent, ErrorContent

# Helper to reset global check state for MATLAB availability
def reset_matlab_check_state():
    global _matlab_checked, _matlab_available
    # Need to directly assign to the global variables in the server module
    import matlab_server.server
    matlab_server.server._matlab_checked = False
    matlab_server.server._matlab_available = False

@pytest.fixture(autouse=True)
def reset_globals():
    reset_matlab_check_state()
    yield
    reset_matlab_check_state()

@pytest.mark.asyncio
async def test_check_matlab_installation_success():
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"MATLAB OK", b""))
    mock_process.returncode = 0

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)) as mock_exec:
        assert await check_matlab_installation() is True
        mock_exec.assert_called_once_with(
            "matlab", "-batch", "disp('MATLAB OK'); exit;",
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        # Check that state is updated
        import matlab_server.server
        assert matlab_server.server._matlab_available is True
        assert matlab_server.server._matlab_checked is True

@pytest.mark.asyncio
async def test_check_matlab_installation_not_found():
    with patch("asyncio.create_subprocess_exec", AsyncMock(side_effect=FileNotFoundError)) as mock_exec:
        assert await check_matlab_installation() is False
        mock_exec.assert_called_once()
        import matlab_server.server
        assert matlab_server.server._matlab_available is False
        assert matlab_server.server._matlab_checked is True

@pytest.mark.asyncio
async def test_check_matlab_installation_command_error():
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"Some error", b"Failed"))
    mock_process.returncode = 1

    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)) as mock_exec:
        assert await check_matlab_installation() is False
        import matlab_server.server
        assert matlab_server.server._matlab_available is False
        assert matlab_server.server._matlab_checked is True

@pytest.mark.asyncio
async def test_execute_matlab_code_text_success():
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"Hello from MATLAB", b""))
    mock_process.returncode = 0

    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)) as mock_exec:
        code = "disp('Hello from MATLAB');"
        output, stderr_msg = await execute_matlab_code(code, output_format="text")
        assert output == "Hello from MATLAB"
        assert stderr_msg is None
        expected_matlab_code = f"""
        try
            {code}
        catch ME
            disp(['MATLAB_ERROR: ' ME.message]);
        end
        exit; % Ensure MATLAB exits
        """
        mock_exec.assert_called_once_with(
            "matlab", "-batch", expected_matlab_code,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

@pytest.mark.asyncio
async def test_execute_matlab_code_text_script_error():
    # Simulate MATLAB itself reporting an error via our convention
    matlab_output_with_error = "MATLAB_ERROR: Undefined function 'foo'."
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(matlab_output_with_error.encode(), b""))
    mock_process.returncode = 0 # MATLAB might exit 0 if try/catch handles the error

    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)):
        code = "foo;" # Some invalid code
        output, _ = await execute_matlab_code(code, output_format="text")
        assert "MATLAB_ERROR: Undefined function 'foo'." in output

@pytest.mark.asyncio
async def test_execute_matlab_code_process_error():
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"", b"MATLAB process crashed"))
    mock_process.returncode = 1 # Non-zero exit code

    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)):
        code = "some_code;"
        with pytest.raises(RuntimeError, match="MATLAB process exited with code 1"):
            await execute_matlab_code(code, output_format="text")

@pytest.mark.asyncio
async def test_execute_matlab_code_matlab_not_found_error():
    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=False)):
        with pytest.raises(RuntimeError, match="MATLAB is not installed"):
            await execute_matlab_code("disp(1)", output_format="text")

@pytest.mark.asyncio
async def test_execute_matlab_code_plot_success():
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"Plot generated", b"")) # stdout from matlab
    mock_process.returncode = 0

    dummy_image_data = b"dummy_png_data"
    encoded_dummy_image_data = "ZHVtbXlfcG5nX2RhdGE=" # base64 of "dummy_png_data"

    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)) as mock_exec, \
         patch("tempfile.mkstemp", MagicMock(return_value=(0, "/tmp/fakeplot.png"))), \
         patch("os.path.exists", MagicMock(return_value=True)), \
         patch("os.path.getsize", MagicMock(return_value=len(dummy_image_data))), \
         patch("builtins.open", mock_open(read_data=dummy_image_data)), \
         patch("os.remove", MagicMock()) as mock_remove, \
         patch("os.close", MagicMock()): # Need to mock os.close for tempfile.mkstemp

        code = "plot(1:10);"
        output, script_stdout = await execute_matlab_code(code, output_format="plot")
        assert output == encoded_dummy_image_data
        assert script_stdout == "Plot generated" # The stdout from the MATLAB process

        # Check that the MATLAB code includes plot saving
        # The actual path will be /tmp/fakeplot.png
        # The path in MATLAB command should be /tmp/fakeplot.png (already sanitized)
        expected_matlab_code_fragment = "print('-dpng', '/tmp/fakeplot.png');"
        called_matlab_code = mock_exec.call_args[0][2]
        assert expected_matlab_code_fragment in called_matlab_code
        mock_remove.assert_called_once_with("/tmp/fakeplot.png")


@pytest.mark.asyncio
async def test_execute_matlab_code_plot_no_figure_warning():
    matlab_output = "MATLAB_WARNING: No figure was generated to save."
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(matlab_output.encode(), b""))
    mock_process.returncode = 0

    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)), \
         patch("tempfile.mkstemp", MagicMock(return_value=(0, "/tmp/fakeplot.png"))), \
         patch("os.path.exists", MagicMock(return_value=False)), # Simulate plot file not created
         patch("os.remove", MagicMock()) as mock_remove, \
         patch("os.close", MagicMock()):

        code = "disp('No plot');" # Code that doesn't plot
        image_data, stdout_from_script = await execute_matlab_code(code, output_format="plot")
        assert image_data == "" # Empty string for image data
        assert "MATLAB_WARNING: No figure was generated to save." in stdout_from_script
        mock_remove.assert_called_once_with("/tmp/fakeplot.png") # cleanup still attempted

@pytest.mark.asyncio
async def test_execute_matlab_code_plot_file_not_created_error():
    mock_process = AsyncMock()
    # Simulate MATLAB producing some output but no specific warning about no figure
    mock_process.communicate = AsyncMock(return_value=(b"Some output from MATLAB", b""))
    mock_process.returncode = 0

    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)), \
         patch("tempfile.mkstemp", MagicMock(return_value=(0, "/tmp/fakeplot.png"))), \
         patch("os.path.exists", MagicMock(return_value=False)), # Simulate plot file not created
         patch("os.remove", MagicMock()) as mock_remove, \
         patch("os.close", MagicMock()):

        code = "plot(1:10);" # Assume this should create a plot
        with pytest.raises(RuntimeError, match="Failed to generate plot"):
            await execute_matlab_code(code, output_format="plot")
        mock_remove.assert_called_once_with("/tmp/fakeplot.png") # cleanup still attempted


# --- Tests for the MCP Tool ---

@pytest.mark.asyncio
async def test_execute_matlab_tool_text_success():
    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("matlab_server.server.execute_matlab_code", AsyncMock(return_value=("Test output", None))) as mock_exec_code:

        result = await execute_matlab_tool(code="disp('hello')", output_format="text")
        assert isinstance(result, TextContent)
        assert result.text == "Test output"
        mock_exec_code.assert_called_once_with("disp('hello')", "text")

@pytest.mark.asyncio
async def test_execute_matlab_tool_plot_success():
    base64_image_data = "fake_base64_image_data"
    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("matlab_server.server.execute_matlab_code", AsyncMock(return_value=(base64_image_data, "Plot done"))) as mock_exec_code:

        result = await execute_matlab_tool(code="plot(1:10)", output_format="plot")
        assert isinstance(result, ImageContent)
        assert result.format == "png"
        assert result.base64 == base64_image_data
        mock_exec_code.assert_called_once_with("plot(1:10)", "plot")

@pytest.mark.asyncio
async def test_execute_matlab_tool_matlab_not_installed():
    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=False)):
        result = await execute_matlab_tool(code="disp(1)", output_format="text")
        assert isinstance(result, ErrorContent)
        assert "MATLAB (matlab command) is not installed" in result.message

@pytest.mark.asyncio
async def test_execute_matlab_tool_empty_code():
    # check_matlab_installation will be called, so mock it
    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)):
        result = await execute_matlab_tool(code="", output_format="text")
        assert isinstance(result, ErrorContent)
        assert result.message == "MATLAB code cannot be empty."

@pytest.mark.asyncio
async def test_execute_matlab_tool_execution_error():
    # This error is raised from execute_matlab_code
    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("matlab_server.server.execute_matlab_code", AsyncMock(side_effect=RuntimeError("MATLAB crashed"))) as mock_exec_code:

        result = await execute_matlab_tool(code="bad_code", output_format="text")
        assert isinstance(result, ErrorContent)
        assert result.message == "MATLAB crashed"

@pytest.mark.asyncio
async def test_execute_matlab_tool_plot_no_figure_generated_error():
    # Simulate execute_matlab_code returning empty image data and a warning
    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("matlab_server.server.execute_matlab_code", AsyncMock(return_value=("", "MATLAB_WARNING: No figure was generated to save."))) as mock_exec_code:

        result = await execute_matlab_tool(code="disp('no plot')", output_format="plot")
        assert isinstance(result, ErrorContent)
        assert "MATLAB code executed, but no plot was generated." in result.message
        # If the warning is more specific, it might be part of the message
        # assert "Output: MATLAB_WARNING: No figure was generated to save." in result.message

@pytest.mark.asyncio
async def test_execute_matlab_tool_plot_other_error_no_image():
    # Simulate execute_matlab_code returning empty image data and some other script output
    with patch("matlab_server.server.check_matlab_installation", AsyncMock(return_value=True)), \
         patch("matlab_server.server.execute_matlab_code", AsyncMock(return_value=("", "Some other output"))) as mock_exec_code:

        result = await execute_matlab_tool(code="plot_maybe_fails", output_format="plot")
        assert isinstance(result, ErrorContent)
        assert "MATLAB code executed, but no plot was generated. Output: Some other output" in result.message

# It might be useful to also test the main() function if it had more complex logic,
# but here it's just calling mcp.run() and logging.
# Testing mcp.run() itself is out of scope for this unit test.

# Ensure that the patch for _matlab_checked and _matlab_available in the server module works
@pytest.mark.asyncio
async def test_global_state_reset_mechanism():
    import matlab_server.server
    # Set to non-default values
    matlab_server.server._matlab_checked = True
    matlab_server.server._matlab_available = True

    # Fixture `reset_globals` runs before and after this test.
    # We check the state before it runs its "after" part.
    # This test itself doesn't do much other than verify the fixture's setup.
    # The actual reset is tested by other tests running cleanly.
    # If we want to be very explicit:
    reset_matlab_check_state() # Manually call reset
    assert matlab_server.server._matlab_checked is False
    assert matlab_server.server._matlab_available is False

    # Simulate a check
    mock_process = AsyncMock()
    mock_process.communicate = AsyncMock(return_value=(b"MATLAB OK", b""))
    mock_process.returncode = 0
    with patch("asyncio.create_subprocess_exec", AsyncMock(return_value=mock_process)):
        await check_matlab_installation()
    assert matlab_server.server._matlab_checked is True
    assert matlab_server.server._matlab_available is True

    # The fixture will reset these after the test.
    # We can add another test that runs after this one to ensure it sees the reset state,
    # but pytest runs tests in isolation regarding fixtures like this when used with autouse=True.
```

I've created the `test_server.py` file with a comprehensive suite of tests covering `check_matlab_installation`, `execute_matlab_code` (for text and plot outputs, including various success and error scenarios), and the `execute_matlab` MCP tool.

The tests use `unittest.mock.patch` and `unittest.mock.AsyncMock` extensively to simulate interactions with the MATLAB process and file system operations, making the tests independent of an actual MATLAB installation.
I also added a fixture to reset the global state variables `_matlab_checked` and `_matlab_available` between tests to ensure test isolation.

To run these tests, one would typically navigate to the `servers/matlab-server` directory (or the repo root, depending on pytest configuration) and run `pytest`. The import `from matlab_server.server import ...` assumes that the `servers/matlab-server/src` directory is added to `PYTHONPATH` or that pytest handles it. This might require a `pytest.ini` or adjustments to `pyproject.toml` for pytest to correctly discover the `matlab_server` module if running pytest from the `servers/matlab-server` directory.

A simple `pytest.ini` in `servers/matlab-server/` could be:
```ini
[pytest]
pythonpath = src
```
I'll create this `pytest.ini` as well.
