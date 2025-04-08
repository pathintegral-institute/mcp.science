import math
import io
import base64
from typing import List, Literal
from mcp.types import ImageContent
from matplotlib.figure import Figure

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
    "matplotlib"
]


def send_image_to_client(fig: Figure) -> ImageContent:
    """
    Convert a matplotlib figure to a list of ImageContent objects.

    Args:
        fig (Figure): A matplotlib figure object

    Returns:
        List[ImageContent]: A list containing one ImageContent object
    """
    # Create a buffer and save the figure to it
    buf = io.BytesIO()
    fig.savefig(buf, format='png')
    buf.seek(0)

    # Encode the image data as base64
    img_data = base64.b64encode(buf.getvalue()).decode('utf-8')

    # Create an ImageContent object
    image_content = ImageContent(
        type="image",
        data=img_data,
        mimeType="image/png"
    )

    # Clean up
    buf.close()

    return image_content


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
