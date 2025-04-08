import argparse
import sys
from .local_python_executor import evaluate_python_code
from .schemas import BASE_BUILTIN_MODULES, DEFAULT_MAX_LEN_OUTPUT
import resource


def main():
    """
    Main function to execute the evaluate_python_code function.
    This serves as an entry point for the code evaluation functionality.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(
        description="Execute Python code in a sandboxed environment"
    )
    parser.add_argument(
        "--code", type=str, required=True, help="Python code to evaluate"
    )
    parser.add_argument(
        "--authorized-imports",
        type=str,
        nargs="+",
        default=BASE_BUILTIN_MODULES,
        help="List of authorized Python modules that can be imported",
    )
    parser.add_argument(
        "--max-print-length",
        type=int,
        default=DEFAULT_MAX_LEN_OUTPUT,
        help="Maximum length of print outputs",
    )
    parser.add_argument(
        "--max-memory-mb", type=int, default=-1, help="Maximum memory usage in MB, lower than 0 means no limit"
    )
    parser.add_argument(
        "--max-cpu-time-sec", type=int, default=-1, help="Maximum CPU time in seconds, lower than 0 means no limit"
    )

    args = parser.parse_args()

    # only for linux
    if sys.platform == "linux":
        if args.max_cpu_time_sec > 0:
            resource.setrlimit(
                resource.RLIMIT_CPU, (args.max_cpu_time_sec, args.max_cpu_time_sec + 10)
            )
        if args.max_memory_mb > 0:
            resource.setrlimit(
                resource.RLIMIT_AS,
                (
                    args.max_memory_mb * 1024 * 1024,
                    args.max_memory_mb * 2 * 1024 * 1024,
                ),
            )
        # Prevent file creation by setting file size limit to 0
        # resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
        # # Prevent file opening by setting open file limit to 0
        # resource.setrlimit(resource.RLIMIT_NOFILE, (0, 0))

    # Execute the evaluation and print the result directly
    try:
        result = evaluate_python_code(
            code=args.code,
            state=None,  # No state file input
            authorized_imports=args.authorized_imports,
            max_print_outputs_length=args.max_print_length,
        )

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
