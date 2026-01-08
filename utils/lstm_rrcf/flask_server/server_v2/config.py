import os
import yaml
import copy
from dataclasses import asdict
from typing import Any
from config_types import (
    Redis, RedisConfig,  GlobalConfig
)
from logger import logger

# Default Redis configuration
DefaultRedis = Redis(
    write=[],
    read=[]
)

# Default Global configuration
DefaultConfig = GlobalConfig(
    logLevel='info',
    environment='dev',
    enableServicabilityMetrics=True,
    redis=DefaultRedis
)

# Deep merge utility
def deep_merge(default: Any, override: Any) -> Any:
    try:
        if isinstance(default, dict) and isinstance(override, dict):
            merged = copy.deepcopy(default)
            for key, value in override.items():
                if key in merged:
                    merged[key] = deep_merge(merged[key], value)
                else:
                    merged[key] = value
            return merged
        return override if override is not None else default
    except Exception as e:
        logger.error(f"Error during deep merge: {e}")
        logger.warning("Falling back to default configuration due to merge failure")
        return default

# Load and merge configuration
def get_config() -> Any:
    config_file_path = os.getenv('FISSION_ENV_CONFIG', '')
    if not config_file_path:
        logger.error('Empty ENV variable FISSION_ENV_CONFIG')
        return None

    try:
        with open(config_file_path, 'r') as f:
            config_content = f.read()
            logger.info(f"[FISSION_ENV_CONFIG] config file {config_file_path} loaded")
    except Exception as e:
        logger.error(f"Failed to read config file: {e}")
        return None

    try:
        yaml_partial_config = yaml.safe_load(config_content)
    except yaml.YAMLError as e:
        logger.error(f"YAML parsing error in config file: {e}")
        return None

    # Convert dataclass to dict for merging
    default_config_dict = asdict(DefaultConfig)
    merged_config_dict = deep_merge(default_config_dict, yaml_partial_config)

    # Return merged config as dict (can be converted to GlobalConfig if needed)
    return merged_config_dict