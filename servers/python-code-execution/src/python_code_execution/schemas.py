import math
import io
import base64
from typing import cast
import uuid
from mcp.types import ImageContent
from matplotlib.figure import Figure
from plotly.graph_objects import Figure as PlotlyFigure
from mcp.types import EmbeddedResource, TextResourceContents, ImageContent
import plotly.io

DEFAULT_MAX_LEN_OUTPUT = 50000
MAX_OPERATIONS = 10000
MAX_WHILE_ITERATIONS = 10000
MAX_LENGTH_TRUNCATE_CONTENT = 20000


BASE_BUILTIN_MODULES = [
    "collections",
    "datetime",
    "itertools",
    "math",
    "queue",
    "random",
    "re",
    "stat",
    "statistics",
    "time",
    "unicodedata",
    "numpy",
    "matplotlib",
    "plotly"
]


def send_image_to_client(fig: Figure | PlotlyFigure) -> list[ImageContent | EmbeddedResource]:
    """
    Convert a matplotlib or plotly figure to an ImageContent object.

    Args:
        fig (Figure | PlotlyFigure): A matplotlib or plotly figure object

    Returns:
        ImageContent: An ImageContent object
    """
    # Create a buffer
    buf = io.BytesIO()
    result = []
    # Handle different figure types
    if isinstance(fig, PlotlyFigure):
        # For Plotly figures
        img_data = plotly.io.to_image(fig, format="png")
        img_str = base64.b64encode(img_data).decode('utf-8')
        result.append(
            EmbeddedResource(
                type="resource",
                resource=TextResourceContents(
                    uri=f"project://{uuid.uuid4()}",
                    text=cast(str, fig.to_json()),
                    mimeType="application/json"
                ),
                # EmbeddedResource has enabled extra fields, so add an extra_type to indicate it's a plotly figure
                extra_type="plotly",
            )
        )
    else:
        # For Matplotlib figures
        fig.savefig(buf, format='png')
        buf.seek(0)
        img_str = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Create an ImageContent object
    image_content = ImageContent(
        type="image",
        data=img_str,
        mimeType="image/png"
    )
    result.append(image_content)
    # Clean up
    buf.close()

    return result


BASE_PYTHON_TOOLS = {
    "print": print,
    "send_image_to_client": send_image_to_client,
    "isinstance": isinstance,
    "range": range,
    "float": float,
    "int": int,
    "bool": bool,
    "str": str,
    "set": set,
    "list": list,
    "dict": dict,
    "tuple": tuple,
    "round": round,
    "ceil": math.ceil,
    "floor": math.floor,
    "log": math.log,
    "exp": math.exp,
    "sin": math.sin,
    "cos": math.cos,
    "tan": math.tan,
    "asin": math.asin,
    "acos": math.acos,
    "atan": math.atan,
    "atan2": math.atan2,
    "degrees": math.degrees,
    "radians": math.radians,
    "pow": pow,
    "sqrt": math.sqrt,
    "len": len,
    "sum": sum,
    "max": max,
    "min": min,
    "abs": abs,
    "enumerate": enumerate,
    "zip": zip,
    "reversed": reversed,
    "sorted": sorted,
    "all": all,
    "any": any,
    "map": map,
    "filter": filter,
    "ord": ord,
    "chr": chr,
    "next": next,
    "iter": iter,
    "divmod": divmod,
    "callable": callable,
    "getattr": getattr,
    "hasattr": hasattr,
    "setattr": setattr,
    "issubclass": issubclass,
    "type": type,
    "complex": complex,
}

DANGEROUS_FUNCTIONS = [
    "builtins.compile",
    "builtins.eval",
    "builtins.exec",
    "builtins.globals",
    "builtins.locals",
    "builtins.__import__",
    "os.popen",
    "os.system",
    "posix.system",
]
