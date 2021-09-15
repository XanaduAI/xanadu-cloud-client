"""
This module contains the :class:`~xcc.Settings` class and related helper functions.
"""

import os
from typing import Optional

from appdirs import user_config_dir
from dotenv import set_key
from pydantic import BaseSettings


def get_path_to_env_file() -> str:
    """Returns the path to the .env file containing the Xanadu Cloud connection settings."""
    path_to_config_dir = user_config_dir("xanadu-cloud")
    return os.path.join(path_to_config_dir, ".env")


def get_name_of_env_var(key: str = "") -> str:
    """Returns the name of the Xanadu Cloud environment variable associated with the given key."""
    return f"XANADU_CLOUD_{key}"


class Settings(BaseSettings):
    """Represents the configuration for connecting to the Xanadu Cloud."""

    API_KEY: Optional[str] = None
    HOST: str = "platform.strawberryfields.ai"
    PORT: int = 443
    TLS: bool = True

    # pylint: disable=missing-class-docstring,too-few-public-methods
    class Config:
        case_sensitive = True
        env_file = get_path_to_env_file()
        env_prefix = get_name_of_env_var()

    def save(self) -> None:
        """Saves the current settings to the .env file."""
        env_file = Settings.Config.env_file
        env_dir = os.path.dirname(env_file)
        os.makedirs(env_dir, exist_ok=True)

        for key, val in self.__dict__.items():
            if val is not None:
                set_key(
                    dotenv_path=env_file,
                    key_to_set=get_name_of_env_var(key),
                    value_to_set=str(val),
                    quote_mode="auto",
                )
