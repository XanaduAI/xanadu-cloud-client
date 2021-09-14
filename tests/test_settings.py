# pylint: disable=no-self-use,redefined-outer-name
"""
This module tests the :module:`xcc.settings` module.
"""

from tempfile import NamedTemporaryFile

import pytest
from dotenv import dotenv_values

import xcc


@pytest.fixture()
def env_file(monkeypatch):
    """Returns a mock .env file."""
    with NamedTemporaryFile() as env_file:
        monkeypatch.setattr("xcc.settings.Settings.Config.env_file", env_file.name)
        yield env_file


def test_get_path_to_env_file(monkeypatch):
    """Tests that the path to the .env file is derived correctly."""
    monkeypatch.setattr("xcc.settings.user_config_dir", lambda path: f"foo/bar/{path}")
    assert xcc.settings.get_path_to_env_file() == "foo/bar/xanadu-cloud/.env"


def test_get_name_of_env_var():
    """Tests that the names of Xanadu Cloud environment variables is derived correctly."""
    assert xcc.settings.get_name_of_env_var() == "XANADU_CLOUD_"
    assert xcc.settings.get_name_of_env_var("KEY") == "XANADU_CLOUD_KEY"


class TestSettings:
    """Tests the :class:`xcc.Settings` class."""

    def test_precedence(self, monkeypatch, env_file):
        """Tests that default field values have the lowest precedence, variables
        in the .env file have medium precedence, and environment variables have
        the highest precedence.
        """
        assert xcc.Settings().PORT == 443

        env_file.write(b"XANADU_CLOUD_PORT=12345")
        env_file.seek(0)
        assert xcc.Settings().PORT == 12345

        monkeypatch.setenv("XANADU_CLOUD_PORT", "54321")
        assert xcc.Settings().PORT == 54321

    def test_save(self, env_file):
        """Tests that settings can be saved to the .env file."""
        settings = xcc.Settings()

        settings.API_KEY = "j.w.t"
        settings.HOST = "example.com"
        settings.PORT = 80
        settings.TLS = False

        settings.save()

        assert dotenv_values(env_file.name) == {
            "XANADU_CLOUD_API_KEY": "j.w.t",
            "XANADU_CLOUD_HOST": "example.com",
            "XANADU_CLOUD_PORT": "80",
            "XANADU_CLOUD_TLS": "False",
        }

    def test_save_missing_api_key(self, env_file):
        """Tests that missing API keys are not saved to the .env file."""
        xcc.Settings().save()
        assert "XANADU_CLOUD_API_KEY" not in dotenv_values(env_file.name)
