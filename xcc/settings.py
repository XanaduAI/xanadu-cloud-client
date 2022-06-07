"""
This module contains the :class:`~xcc.Settings` class and related helper functions.
"""

import os
import re
from typing import Optional

from appdirs import user_config_dir
from dotenv import dotenv_values, set_key, unset_key
from pydantic import BaseSettings

# Matches when string contains chars outside Base64URL set
# https://base64.guru/standards/base64url
# https://en.wikipedia.org/wiki/Base64#Variants_summary_table
# Also, the dot '.' to separate sections.
_BASE64URLRE = re.compile(r"[^\.A-Za-z0-9_-]+")


def get_path_to_env_file() -> str:
    """Returns the path to the .env file containing the Xanadu Cloud connection settings."""
    path_to_config_dir = user_config_dir(appname="xanadu-cloud", appauthor="Xanadu")
    return os.path.join(path_to_config_dir, ".env")


def get_name_of_env_var(key: str = "") -> str:
    """Returns the name of the Xanadu Cloud environment variable associated with the given key."""
    return f"XANADU_CLOUD_{key}"


def _check_for_invalid_values(key: str, val: str) -> None:
    """
    Check for conditions that make saving the env_file
    dangerous to the user.

    - REFRESH_TOKEN must not contain characters outside Base64URL set

    Args:
        key (str): .env file key
        val (str): .env file value

    Raises:
        ValueError: if the value should not be saved to the .env file

    """

    if key == "REFRESH_TOKEN" and val is not None and re.search(_BASE64URLRE, val) is not None:
        raise ValueError("REFRESH_TOKEN contains non-JWT character(s)")


class Settings(BaseSettings):
    """Represents the configuration for connecting to the Xanadu Cloud.

    The location where this configuration is saved depends on the current
    operating system. Specifically,

    * Windows: ``C:\\Users\\%USERNAME%\\AppData\\Local\\Xanadu\\xanadu-cloud\\.env``

    * MacOS: ``/home/$USER/Library/Application\\ Support/xanadu-cloud/.env``

    * Linux: ``/home/$USER/.config/xanadu-cloud/.env``

    **Example:**

    The following example shows how to use the :class:`Settings` class to load
    and save a Xanadu Cloud configuration. To begin, loading a configuration is
    as simple as instantiating a settings object:

    >>> import xcc
    >>> settings = xcc.Settings()
    >>> settings
    REFRESH_TOKEN=None ACCESS_TOKEN=None HOST='platform.xanadu.ai' PORT=443 TLS=True

    Now, individual options can be accessed or assigned through their
    corresponding attribute:

    >>> settings.PORT
    443
    >>> settings.PORT = 80
    >>> settings.PORT
    80

    .. note::

        Several aggregate representations of options are also available, such as

        >>> settings.dict()
        {'REFRESH_TOKEN': None, 'ACCESS_TOKEN': None, ..., 'TLS': True}
        >>> settings.json()
        '{"REFRESH_TOKEN": null, "ACCESS_TOKEN": null, ..., "TLS": true}'

    Finally, saving a configuration can be done by invoking :meth:`Settings.save`:

    >>> settings.save()
    """

    REFRESH_TOKEN: Optional[str] = None
    """JWT refresh token that can be used to fetch access tokens from the Xanadu Cloud."""

    ACCESS_TOKEN: Optional[str] = None
    """JWT access token that can be used to authenticate requests to the Xanadu Cloud."""

    HOST: str = "platform.xanadu.ai"
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

        # must be done first as dict is not ordered
        for key, val in self.dict().items():
            _check_for_invalid_values(key, val)

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
