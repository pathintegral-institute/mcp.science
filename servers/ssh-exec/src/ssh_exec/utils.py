import os
import logging
from typing import List
from fastapi import HTTPException


def validate_command(
    command: str,
    allowed_commands: List[str],
    allowed_paths: List[str],
    commands_blacklist: List[str],
    arguments_blacklist: List[str]
) -> None:
    """Validate if a command is allowed to be executed

    Args:
        command: Command to validate
        allowed_commands: List of allowed commands
        allowed_paths: List of allowed paths
        commands_blacklist: List of blacklisted commands
        arguments_blacklist: List of blacklisted arguments

    Raises:
        HTTPException: If the command validation fails
    """
    # Strip the command of any leading/trailing whitespace
    command = command.strip()

    # Check if the command is empty
    if not command:
        error_msg = "Command cannot be empty"
        logging.error("Command validation failed: %s", error_msg)
        raise HTTPException(
            status_code=400, detail=f"Command validation failed: {error_msg}")

    # Split the command into parts (command and arguments)
    parts = command.split()
    base_command = parts[0]

    # Check if the command is in the blacklist
    for blacklisted_cmd in commands_blacklist:
        if base_command == blacklisted_cmd or base_command.endswith(f"/{blacklisted_cmd}"):
            error_msg = f"Command '{base_command}' is blacklisted"
            logging.error("Command validation failed: %s", error_msg)
            raise HTTPException(
                status_code=400, detail=f"Command validation failed: {error_msg}")

    # Check for blacklisted arguments
    for arg in parts[1:]:
        for blacklisted_arg in arguments_blacklist:
            if arg == blacklisted_arg:
                error_msg = f"Argument '{arg}' is blacklisted"
                logging.error("Command validation failed: %s", error_msg)
                raise HTTPException(
                    status_code=400, detail=f"Command validation failed: {error_msg}")

    # If allowed_commands is provided, check if the command is in the list
    if allowed_commands:
        is_allowed = False
        for allowed_cmd in allowed_commands:
            if command.startswith(allowed_cmd):
                is_allowed = True
                break

        if not is_allowed:
            error_msg = f"Command '{command}' is not in the allowed commands list"
            logging.error("Command validation failed: %s", error_msg)
            raise HTTPException(
                status_code=400, detail=f"Command validation failed: {error_msg}")

    # If allowed_paths is provided, check if the command operates on allowed paths
    if allowed_paths and any(path_arg for path_arg in parts[1:] if not path_arg.startswith("-")):
        # Extract potential path arguments (those not starting with -)
        potential_paths = [arg for arg in parts[1:] if not arg.startswith("-")]

        for path_arg in potential_paths:
            path_allowed = False

            # Skip empty path arguments
            if not path_arg.strip():
                continue

            # Check if the path is within any of the allowed paths
            for allowed_path in allowed_paths:
                # Normalize paths for comparison
                norm_path_arg = os.path.normpath(path_arg)
                norm_allowed_path = os.path.normpath(allowed_path)

                if (norm_path_arg.startswith(norm_allowed_path) or
                        os.path.abspath(norm_path_arg).startswith(norm_allowed_path)):
                    path_allowed = True
                    break

            if not path_allowed:
                error_msg = f"Path '{path_arg}' is not in the allowed paths list"
                logging.error("Command validation failed: %s", error_msg)
                raise HTTPException(
                    status_code=400, detail=f"Command validation failed: {error_msg}")

    # If we get here, the command is valid
    return
