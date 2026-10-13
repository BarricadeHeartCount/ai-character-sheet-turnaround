"""Config package: schema, defaults, and loader."""
from config.schema import AppConfig, CONFIG_VERSION
from config.loader import load_config

__all__ = ["AppConfig", "CONFIG_VERSION", "load_config"]