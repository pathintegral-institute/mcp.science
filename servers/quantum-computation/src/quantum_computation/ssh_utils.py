import paramiko
from functools import lru_cache
from getpass import getpass
import os
from loguru import logger
from pydantic import BaseModel
from dynaconf import Dynaconf


class SSHConfig(BaseModel):
    """SSH configuration for remote execution."""

    hostname: str
    username: str
    remote_script_folder_path: str
    python_path: str
    remote_root_path: str
    remote_user_path: str
    use_key_to_connect: bool


class AppSettings(BaseModel):
    ssh_config: SSHConfig


@lru_cache
def load_ssh_config():
    """
    Load configuration from config/ssh_config.toml using dynaconf.
    Returns a Dynaconf settings object.
    """
    # get the current working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = f"{current_dir}/config/settings.toml"
    logger.info(f"Loading config from: {config_path}")
    settings = Dynaconf(
        settings_files=[config_path])
    logger.info(f"Loaded ssh config: {settings.to_dict()}")
    return settings.to_dict()['DEFAULT']['ssh_config']


def connect_ssh(hostname, username):
    ssh = paramiko.SSHClient()
    ssh.load_system_host_keys()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname, username=username)
    logger.info(f"Successfully connected to {hostname}")
    return ssh


def connect_ssh_by_key(hostname, username, key_path):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Expand the key_path if it uses ~
        key_path = os.path.expanduser(key_path)

        # Check if the key file exists
        if not os.path.exists(key_path):
            raise FileNotFoundError(f"SSH key file not found: {key_path}")

        # Try to load the key
        try:
            key = paramiko.RSAKey.from_private_key_file(key_path)
        except paramiko.ssh_exception.PasswordRequiredException:
            # If a password is required, prompt the user
            passphrase = getpass(
                "Enter passphrase for key '{}': ".format(key_path))
            key = paramiko.RSAKey.from_private_key_file(
                key_path, password=passphrase)

        # Connect with the key
        ssh.connect(hostname, username=username, pkey=key)
        logger.info(f"Successfully connected to {hostname}")
        return ssh
    except Exception as e:
        logger.info(f"Failed to connect to {hostname}: {str(e)}")
        return None


def execute_command_on_server(command: str):
    """
    SSH to a computation server and execute a command.

    Args:
        command: The command to execute.
        ssh_config: The configuration of the SSH client. ssh_config needs to contain
            the hostname, username, key_path that are used to connect to the server. In
            addition, it contains remote_root_path, which is the absolute path of the
            parent folder at the remote server where the command will be executed

            Default to the config['ssh_config'] if not specified.
    """
    ssh_config = load_ssh_config()
    hostname = ssh_config["hostname"]
    username = ssh_config["username"]

    # use_key_to_connect is a flag to determine whether to use SSH key to connect
    # If use_key_to_connect is not specified in secrets.json, default to False
    use_key_to_connect = ssh_config.get("use_key_to_connect", False)
    logger.info(f"Connecting to {hostname} as {username}")
    print(f"Connecting to {hostname} as {username}")
    if use_key_to_connect:
        ssh = connect_ssh_by_key(
            hostname, username, key_path=ssh_config["key_filename"])
    else:
        ssh = connect_ssh(hostname, username)

    logger.info(f"Connected {ssh}")

    # remote_folder_path is the repo root path of the remote folder
    remote_root_path = ssh_config["remote_root_path"]

    ssh_command = f"cd {remote_root_path} && {command}"
    logger.info(f"Sending SSH command: \n\n{ssh_command}")
    stdin, stdout, stderr = ssh.exec_command(ssh_command, timeout=60 * 10)
    logger.info("executed")
    return stdin, stdout, stderr
