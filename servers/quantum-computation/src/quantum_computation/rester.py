from mp_api.client import MPRester
from loguru import logger
from .config import load_mp_api_config


def get_mp_rester():
    mp_api_key = load_mp_api_config()["mp_api_key"]
    if not mp_api_key:
        raise ValueError("cannot find MP_API_KEY in environment variables")
    logger.info("initializing mp_rester")
    return MPRester(mp_api_key)


mp_rester = get_mp_rester()
