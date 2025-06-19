from dynaconf import Dynaconf
from functools import lru_cache
import os
from loguru import logger


@lru_cache
def load_config():
    """
    Load configuration from config/settings.toml using dynaconf.
    Returns a Dynaconf settings object.
    """
    # get the current working directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = f"{current_dir}/config/settings.toml"
    logger.info(f"Loading config from: {config_path}")
    settings = Dynaconf(
        settings_files=[config_path],
        secrets=f"{current_dir}/config/secrets.toml")
    config_dict = settings.to_dict()
    logger.info(f"Loaded config: {config_dict}")
    return config_dict


def load_ssh_config():
    return load_config()['SSH_CONFIG']


def load_mp_api_config():
    return load_config()['MP_API']
