import argparse
import json
import base64
from .local_python_executor import evaluate_python_code
from .schemas import BASE_BUILTIN_MODULES, DEFAULT_MAX_LEN_OUTPUT
from mcp.types import ImageContent, EmbeddedResource


def main():
    """
    Main function to execute the evaluate_python_code function.
    This serves as an entry point for the code evaluation functionality.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description='Execute Python code in a sandboxed environment')
    parser.add_argument('--code', type=str, required=True,
                        help='Python code to evaluate')
    parser.add_argument('--authorized-imports', type=str, nargs='+', default=BASE_BUILTIN_MODULES,
                        help='List of authorized Python modules that can be imported')
    parser.add_argument('--max-print-length', type=int, default=DEFAULT_MAX_LEN_OUTPUT,
                        help='Maximum length of print outputs')
    parser.add_argument('--max-memory-mb', type=int, default=100,
                        help='Maximum memory usage in MB')
    parser.add_argument('--max-cpu-time-sec', type=int, default=15,
                        help='Maximum CPU time in seconds')

    args = parser.parse_args()

    # Execute the evaluation and print the result directly
    try:
        result, images = evaluate_python_code(
            code=args.code,
            state=None,  # No state file input
            authorized_imports=args.authorized_imports,
            max_print_outputs_length=args.max_print_length,
            max_memory_mb=args.max_memory_mb,
            max_cpu_time_sec=args.max_cpu_time_sec
        )

        # If there are response objects (images or embedded resources), format the output as JSON
        if images:
            output = {
                "text": result,
                "content": []
            }
            for obj in images:
                if isinstance(obj, ImageContent):
                    output["content"].append({
                        "type": "image",
                        "data": obj.data,
                        "mimeType": obj.mimeType
                    })
                elif isinstance(obj, EmbeddedResource):
                    output["content"].append({
                        "type": "resource",
                        "resource": {
                            "uri": str(obj.resource.uri),
                            "text": obj.resource.text,
                            "mimeType": obj.resource.mimeType
                        },
                        "extra_type": obj.extra_type
                    })

            print(json.dumps(output))
        else:
            # If no response objects, just print the text result
            print(result)

    except Exception as e:
        resource_error_msg = (
            f"\n⚠️ RESOURCE LIMIT EXCEEDED ⚠️\n"
            f"This tool is meant for basic scientific calculations only.\n"
            f"Attempting to bypass resource limits or execute malicious code may result in account termination.\n"
            f"Error: {type(e).__name__}: {e}"
        )
        print(resource_error_msg)


if __name__ == "__main__":
    main()
