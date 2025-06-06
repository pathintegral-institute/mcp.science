import os
import logging
import json
from typing import Annotated, cast
from mcp.server import FastMCP
from pydantic import Field
from mcp.types import ImageContent, TextContent
from jupyter_code_execution.schema import DirectoryContent, FileContent, NotebookContent
from jupyter_code_execution.utils import add_new_cell_to_notebook, execute_and_capture_output, get_kernel_by_notebook_path, RemoteKernelClientManager, get_content

DEFAULT_EXECUTION_WAIT_TIMEOUT = 60

mcp = FastMCP(name="jupyter", description="Jupyter MCP Server for Code Execution")
logger = logging.getLogger(__name__)

@mcp.tool(
    name="execute_code",
    description="Execute code in a notebook with specific notebook path"
)
def execute_code(
    notebook_path: Annotated[str, Field(..., description="A relative path to the notebook file")],
    code: Annotated[str, Field(..., description="Code to execute")],
) -> list[TextContent]:
    """ Execute code in a notebook with specific notebook path """
    kernel_id = get_kernel_by_notebook_path(notebook_path)
    if kernel_id is None:
        return [
            TextContent(
                type="text",
                text=f"Can not find kernel id with notebook path: {notebook_path}, please make sure the session is running on this notebook"
            )
        ]

    # use context manager to manage client resources
    with RemoteKernelClientManager(kernel_id) as client:
        # execute code
        code_cell, run_timeout = execute_and_capture_output(
            client,
            code,
            read_channel_timeout=1,
            execution_timeout=int(os.getenv("WAIT_EXECUTION_TIMEOUT", DEFAULT_EXECUTION_WAIT_TIMEOUT))
        )

    if run_timeout:
        return [
            TextContent(
                type="text",
                text="Waiting execution result timed out. The kernel may still be running the code."
            )
        ]

    return [
        TextContent(
            type="text",
            text=code_cell.model_dump_json()
        )
    ]


@mcp.tool(
    name="add_cell_and_execute_code",
    description="Add a cell to the notebook and execute it"
)
def add_cell_and_execute_code(
    notebook_path: Annotated[str, Field(..., description="A relative path to the notebook file")],
    code: Annotated[str, Field(..., description="Code to execute")],
) -> list[TextContent]:
    """ Add a cell to the notebook and execute it """
    kernel_id = get_kernel_by_notebook_path(notebook_path)
    if kernel_id is None:
        return [
            TextContent(
                type="text",
                text=f"Can not find kernel id with notebook path: {notebook_path}, please make sure the session is running on this notebook"
            )
        ]

    # use context manager to manage client resources
    with RemoteKernelClientManager(kernel_id) as client:
        # execute code
        code_cell, run_timeout = execute_and_capture_output(
            client,
            code,
            read_channel_timeout=1,
            execution_timeout=int(os.getenv("WAIT_EXECUTION_TIMEOUT", DEFAULT_EXECUTION_WAIT_TIMEOUT))
        )

    if run_timeout:
        return [
            TextContent(
                type="text",
                text="Waiting execution result timed out. The kernel may still be running the code."
            )
        ]

    # add cell to notebook with put method
    try:
        add_new_cell_to_notebook(notebook_path, code_cell)
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Failed to add cell to notebook: {e}"
            )
        ]

    return [
        TextContent(
            type="text",
            text=code_cell.model_dump_json()
        )
    ]

@mcp.tool(
    name="read_file_from_jupyter_workdir",
    description="Read file content. For regular files, returns the entire content; for .ipynb files, returns notebook cells in pages. Each read returns metadata containing cursor, has_more, and reverse values for subsequent reads. For example, if returned metadata is {\"cursor\": 10, \"has_more\": true}, the next read should use {\"cursor\": 10} as parameter."
)
def read_content(
    file_path: Annotated[str, Field(..., description="File path, supports both regular files and .ipynb files, this path should be the relative path to the working directory")],
    cursor: Annotated[int, Field(default=0, description="Starting position for reading, only applies to .ipynb files. Use 0 for first read, then use the cursor value from previous read's metadata")],
    cell_count: Annotated[int, Field(default=10, description="Number of cells to read, only applies to .ipynb files")],
    reverse: Annotated[bool, Field(default=True, description="Reading direction, only applies to .ipynb files. True means read from end to beginning, False means read from beginning to end. Should match the reverse value from previous read's metadata")],
) -> list[TextContent | ImageContent]:
    try:
        # get file content
        content_response = get_content(file_path)

        # handle different file types
        if content_response.root.type == "file":
            return _handle_file_content(cast(FileContent, content_response.root))
        elif content_response.root.type == "notebook":
            return _handle_notebook_content(cast(NotebookContent, content_response.root), cursor, cell_count, reverse)
        else:
            return [
                TextContent(
                    type="text",
                    text=f"Unsupported file type: {content_response.root.type}"
                )
            ]

    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Error reading file: {str(e)}"
            )
        ]

def _handle_file_content(file_content: FileContent) -> list[TextContent | ImageContent]:
    """handle file content"""
    # check if it is an image file
    mimetype = file_content.mimetype
    if mimetype and mimetype.startswith("image/"):
        # for image files, return the content directly
        if file_content.content:
            return [
                ImageContent(
                    type="image",
                    mimeType=mimetype,
                    data=file_content.content
                )
            ]
        else:
            return [
                TextContent(
                    type="text",
                    text="Image content is empty or not available"
                )
            ]

    if file_content.content is None:
        return [
            TextContent(
                type="text",
                text="File content is empty or not available"
            )
        ]

    return [
        TextContent(
            type="text",
            text=file_content.content
        )
    ]

def _handle_notebook_content(notebook_content: NotebookContent, cursor: int, cell_count: int, reverse: bool) -> list[TextContent | ImageContent]:
    """handle notebook content"""
    # get notebook cells
    if notebook_content.content is None or not notebook_content.content.cells:
        return [
            TextContent(
                type="text",
                text="Notebook content is empty or not available"
            )
        ]

    cells = notebook_content.content.cells
    total_cells = len(cells)

    # calculate the cell range to return
    if reverse:
        start = max(0, total_cells - cursor - cell_count)
        end = max(0, total_cells - cursor)
        selected_cells = cells[start:end]
        new_cursor = cursor + (end - start)  # Update cursor by the actual number of cells read
        has_more = start > 0  # More content if we haven't reached the beginning
    else:
        start = min(cursor, total_cells)
        end = min(cursor + cell_count, total_cells)
        selected_cells = cells[start:end]
        new_cursor = end  # Next cursor is the end position
        has_more = new_cursor < total_cells  # More content if we haven't reached the end

    # handle each cell content
    result = []

    for i, cell in enumerate(selected_cells):
        # compatible with notebook without cell.id
        global_cursor = start + i

        source = cell.source
        if isinstance(source, list):
            source = "\n".join(source)

        result.append(
            TextContent(
                type="text",
                text=json.dumps( # type: ignore
                    {
                        "cell_type": cell.cell_type,
                        "cell_id": cell.id or global_cursor,
                        "content_type": "source",
                        "content": source
                    }
                )
            )
        )

        if cell.cell_type == "code" and hasattr(cell, "outputs"):
            for output_idx, output in enumerate(cell.outputs):
                if output.output_type in ["execute_result", "display_data"]:
                    for mime_type, data in output.data.root.items(): # type: ignore
                        if mime_type.startswith("image/"):
                            # return image data
                            result.append(
                                ImageContent(
                                    type="image",
                                    mimeType=mime_type,
                                    data=cast(str, data),
                                    metadata=json.dumps( # type: ignore
                                        {
                                            "cell_type": cell.cell_type,
                                            "cell_id": cell.id or global_cursor,
                                            "content_type": "output",
                                            "output_idx": output_idx
                                        }
                                    )
                                )
                            )
                        else:
                            # return other data types
                            if isinstance(data, list):
                                data = "\n".join(data)
                            result.append(
                                TextContent(
                                    type="text",
                                    text=json.dumps( # type: ignore
                                        {
                                            "cell_type": cell.cell_type,
                                            "cell_id": cell.id or global_cursor,
                                            "content_type": "output",
                                            "content": data,
                                            "output_idx": output_idx
                                        }
                                    )
                                )
                            )
                else:
                    result.append(
                        TextContent(
                            type="text",
                            text=json.dumps( # type: ignore
                                {
                                    "cell_type": cell.cell_type,
                                    "cell_id": cell.id or global_cursor,
                                    "content_type": "output",
                                    "output_idx": output_idx,
                                    "content": output.model_dump_json()
                                }
                            )
                        )
                    )

    # add metadata
    result.append(
        TextContent(
            type="text",
            text=json.dumps({
                "metadata": {
                    "total_cells": total_cells,
                    "current_range": {
                        "start": start,
                        "end": end
                    },
                    "cursor": new_cursor,
                    "has_more": has_more,
                    "reverse": reverse
                }
            })
        )
    )

    return result


@mcp.tool(
    name="list_files_from_jupyter_workdir",
    description="List files in the given file path. Use this tool to navigate and explore subdirectories after discovering the root directory structure. Provide a relative path to browse specific folders within the workspace."
)
def list_files(
    file_path: Annotated[str, Field(...,description="Relative path to the working directory")],
) -> list[TextContent]:
    try:
        contents = cast(DirectoryContent, get_content(file_path).root)
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Failed to list files: {e}"
            )
        ]
    return [
        TextContent(
            type="text",
            text=content.model_dump_json()
        ) for content in contents.content
    ]


@mcp.tool(
    name="list_root_files_from_jupyter_workdir",
    description="List files in the jupyter root directory. This should be used as the starting point for file exploration before navigating to specific subdirectories. Call this tool first to discover available files and directories in the workspace root."
)
def list_root_files() -> list[TextContent]:
    try:
        contents = cast(DirectoryContent, get_content("").root)
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Failed to list files: {e}"
            )
        ]
    return [
        TextContent(
            type="text",
            text=content.model_dump_json()
        ) for content in contents.content
    ]
