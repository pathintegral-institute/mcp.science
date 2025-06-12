"""
At the highest level, a Jupyter notebook is a dictionary with a few keys:
- metadata
- nbformat
- nbformat_minor
- cells

```json
{
    "metadata": {
        "kernel_info": {
            # if kernel_info is defined, its name field is required.
            "name": "the name of the kernel"
        },
        "language_info": {
            # if language_info is defined, its name field is required.
            "name": "the programming language of the kernel",
            "version": "the version of the language",
            "codemirror_mode": "The name of the codemirror mode to use [optional]",
        },
    },
    "nbformat": 4,
    "nbformat_minor": 4,
    "cells": [
        # list of cell dictionaries, see below
    ],
}
```
The official Jupyter Notebook format is defined with [JSON Schema](https://github.com/jupyter/nbformat/blob/main/nbformat/v4/nbformat.v4.schema.json)
"""

from typing import Dict, List, Union, Optional, Any, Literal, Annotated
from pydantic import BaseModel, Field, RootModel

# Define multiline string type
MultilineString = Union[str, List[str]]

# Define MIME bundle type
class MimeBundle(RootModel):
    """Dictionary of MIME type data"""
    root: Dict[str, Union[MultilineString, Any]] = Field(description="Dictionary of MIME type key-value pairs")

# Define output metadata
class OutputMetadata(BaseModel):
    """Cell output metadata"""
    class Config:
        extra = "allow"

class CellMetadata(BaseModel):
    """Cell metadata"""
    class Config:
        extra = "allow"

# Define output types

# Execute result output
class ExecuteResult(BaseModel):
    output_type: Literal["execute_result"] = Field(..., description="Cell output type")
    execution_count: Optional[int] = Field(None, description="Execution count", ge=0)
    data: MimeBundle = Field(..., description="MIME type data")
    metadata: OutputMetadata = Field(..., description="Output metadata")

# Display data output
class DisplayData(BaseModel):
    output_type: Literal["display_data"] = Field(..., description="Cell output type")
    data: MimeBundle = Field(..., description="MIME type data")
    metadata: OutputMetadata = Field(..., description="Output metadata")

# Stream output
class Stream(BaseModel):
    output_type: Literal["stream"] = Field(..., description="Cell output type")
    name: str = Field(..., description="Stream name (stdout, stderr)")
    text: MultilineString = Field(..., description="Stream text output")

# Error output
class Error(BaseModel):
    output_type: Literal["error"] = Field(..., description="Cell output type")
    ename: str = Field(..., description="Error name")
    evalue: str = Field(..., description="Error value or message")
    traceback: List[str] = Field(..., description="Error traceback")

# Output union type
Output = Annotated[Union[ExecuteResult, DisplayData, Stream, Error], Field(discriminator="output_type")]

# Raw cell
class RawCell(BaseModel):
    id: Optional[str] = Field(
        None,
        description="Cell identifier",
        pattern=r"^[a-zA-Z0-9-_]+$",
        min_length=1,
        max_length=64
    )
    cell_type: Literal["raw"] = Field(..., description="Cell type")
    metadata: CellMetadata = Field(..., description="Cell-level metadata")
    source: MultilineString = Field(..., description="Cell content")

# Markdown cell
class MarkdownCell(BaseModel):
    id: Optional[str] = Field(
        None,
        description="Cell identifier",
        pattern=r"^[a-zA-Z0-9-_]+$",
        min_length=1,
        max_length=64
    )
    cell_type: Literal["markdown"] = Field(..., description="Cell type")
    metadata: CellMetadata = Field(..., description="Cell-level metadata")
    source: MultilineString = Field(..., description="Cell content")

# Code cell
class CodeCell(BaseModel):
    # id is introduced in jupyter notebook v4.5
    id: Optional[str] = Field(
        None,
        description="Cell identifier",
        pattern=r"^[a-zA-Z0-9-_]+$",
        min_length=1,
        max_length=64
    )
    cell_type: Literal["code"] = Field(..., description="Cell type")
    metadata: CellMetadata = Field(..., description="Cell-level metadata")
    source: MultilineString = Field(..., description="Cell content")
    outputs: List[Output] = Field(..., description="Execution, display, or stream outputs")
    execution_count: Optional[int] = Field(None, description="Code cell prompt number", ge=0)


# Cell union type
Cell = Annotated[Union[RawCell, MarkdownCell, CodeCell], Field(discriminator="cell_type")]

# Kernel specification
class KernelSpec(BaseModel):
    name: str = Field(..., description="Name of the kernel specification")
    display_name: str = Field(..., description="Name to display in UI")

    class Config:
        extra = "allow"

# Language information
class LanguageInfo(BaseModel):
    name: str = Field(..., description="The programming language which this kernel runs")
    codemirror_mode: Optional[Union[str, Dict[str, Any]]] = Field(None, description="The codemirror mode to use for code in this language")
    file_extension: Optional[str] = Field(None, description="The file extension for files in this language")
    mimetype: Optional[str] = Field(None, description="The mimetype corresponding to files in this language")
    pygments_lexer: Optional[str] = Field(None, description="The pygments lexer to use for code in this language")

    class Config:
        extra = "allow"

# Notebook metadata
class NotebookMetadata(BaseModel):
    kernelspec: Optional[KernelSpec] = Field(None, description="Kernel information")
    language_info: Optional[LanguageInfo] = Field(None, description="Kernel information")

    class Config:
        extra = "allow"

# Notebook class
class Notebook(BaseModel):
    """Jupyter Notebook v4.5 format"""
    metadata: NotebookMetadata = Field(..., description="Notebook root-level metadata")
    nbformat_minor: int = Field(..., description="Notebook format (minor number)", ge=4)
    nbformat: Literal[4] = Field(..., description="Notebook format (major number)")
    cells: List[Cell] = Field(..., description="Array of cells of the current notebook")

# Define Jupyter API return content information model
class ContentInfo(BaseModel):
    name: str = Field(..., description="File or directory name")
    path: str = Field(..., description="File or directory relative path")
    last_modified: str = Field(..., description="Last modified time")
    created: str = Field(..., description="Created time")
    format: Optional[str] = Field(None, description="Content format, such as text, json, etc.")
    mimetype: Optional[str] = Field(None, description="MIME type")
    size: Optional[int] = Field(None, description="File size, unit is byte")
    writable: bool = Field(..., description="Whether the file is writable")
    hash: Optional[str] = Field(None, description="File hash value")
    hash_algorithm: Optional[str] = Field(None, description="Hash algorithm")
    type: str = Field(..., description="Content type, can be file, directory or notebook")

class DirectoryItem(ContentInfo):
    content: Optional[str] = Field(None, description="File content, usually a string")

class FileContent(ContentInfo):
    type: Literal["file"] = Field(..., description="File type")
    content: Optional[str] = Field(None, description="File content, usually a string")

class DirectoryContent(ContentInfo):
    type: Literal["directory"] = Field(..., description="Directory type")
    content: List[DirectoryItem] = Field(..., description="Directory content")

class NotebookContent(ContentInfo):
    type: Literal["notebook"] = Field(..., description="Notebook type")
    content: Optional[Notebook] = Field(None, description="Notebook content")

# Use Annotated and discriminator parameter to represent any possible content type returned by the API
class ContentResponseModel(RootModel):
    root: Annotated[
        Union[FileContent, DirectoryContent, NotebookContent],
        Field(discriminator="type")
    ]
