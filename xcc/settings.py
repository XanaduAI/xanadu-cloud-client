"""
This module contains the :class:`~xcc.Settings` class and related helper functions.
"""

import os
from typing import Optional

from appdirs import user_config_dir
from dotenv import dotenv_values, set_key, unset_key
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

    REFRESH_TOKEN: Optional[str] = None
    """JWT refresh token that can be used to fetch access tokens from the Xanadu Cloud."""

    ACCESS_TOKEN: Optional[str] = None
    """JWT access token that can be used to authenticate requests to the Xanadu Cloud."""

    HOST: str = "platform.strawberryfields.ai"
    """Hostname of the Xanadu Cloud server."""

    PORT: int = 443
    """Port of the Xanadu Cloud server."""

    TLS: bool = True
    """Whether to use HTTPS for requests to the Xanadu Cloud."""

    class Config:  # pylint: disable=missing-class-docstring
        case_sensitive = True
        env_file = get_path_to_env_file()
        env_prefix = get_name_of_env_var()

    def save(self) -> None:
        """Saves the current settings to the .env file."""
        env_file = Settings.Config.env_file
        env_dir = os.path.dirname(env_file)
        os.makedirs(env_dir, exist_ok=True)

        saved = dotenv_values(dotenv_path=env_file)

        for key, val in self.dict().items():
            field = get_name_of_env_var(key)

            # Remove keys that are assigned to None.
            if val is None and field in saved:
                unset_key(
                    dotenv_path=env_file,
                    key_to_unset=field,
                    quote_mode="auto",
                )

            # Replace keys that are not assigned to None.
            elif val is not None and val != saved.get(field):
                set_key(
                    dotenv_path=env_file,
                    key_to_set=field,
                    value_to_set=str(val),
                    quote_mode="auto",
                )
