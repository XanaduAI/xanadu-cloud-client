# pylint: disable=no-self-use,redefined-outer-name
"""
This module tests the :module:`xcc.settings` module.
"""
import os
from tempfile import NamedTemporaryFile, TemporaryDirectory

import pytest
from dotenv import dotenv_values

import xcc


@pytest.fixture()
def env_file(monkeypatch):
    """Returns a mock .env file which :class:`xcc.Settings` is configured to use."""
    with NamedTemporaryFile("w") as env_file:
        monkeypatch.setitem(xcc.Settings.model_config, "env_file", env_file.name)
        yield env_file


def test_get_path_to_env_file(monkeypatch):
    """Tests that the path to the .env file is derived correctly."""

    def user_config_dir(appname: str, appauthor: str) -> str:
        return f"foo/bar/{appauthor}/{appname}"

    monkeypatch.setattr("xcc.settings.user_config_dir", user_config_dir)
    assert xcc.settings.get_path_to_env_file() == "foo/bar/Xanadu/xanadu-cloud/.env"


def test_get_name_of_env_var():
    """Tests that the names of Xanadu Cloud environment variables are derived correctly."""
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

        env_file.write("XANADU_CLOUD_PORT=12345")
        env_file.seek(0)
        assert xcc.Settings().PORT == 12345

        monkeypatch.setenv("XANADU_CLOUD_PORT", "54321")
        assert xcc.Settings().PORT == 54321

    def test_save(self, env_file):
        """Tests that settings can be saved to a .env file."""
        settings = xcc.Settings(REFRESH_TOKEN="j.w.t", HOST="example.com", PORT=80, TLS=False)
        settings.save()

        assert dotenv_values(env_file.name) == {
            "XANADU_CLOUD_REFRESH_TOKEN": "j.w.t",
            "XANADU_CLOUD_HOST": "example.com",
            "XANADU_CLOUD_PORT": "80",
            "XANADU_CLOUD_TLS": "False",
        }

    def test_save_bad_base64_url(self, settings):
        """Tests that a ValueError will be raised
        if REFRESH_TOKEN contains a character outside the Base64URL with
        the addition that the '.' dot character is part of the token as a
        section separator.
        """
        settings.REFRESH_TOKEN = "j.w.t\n"

        match = r"REFRESH_TOKEN contains non-JWT character\(s\)"
        with pytest.raises(ValueError, match=match):
            settings.save()

        # Check that the .env file was not modified since there was a "\n" in the refresh token.
        assert dotenv_values(settings.model_config["env_file"]) == {
            "XANADU_CLOUD_REFRESH_TOKEN": "j.w.t",
            "XANADU_CLOUD_HOST": "example.com",
            "XANADU_CLOUD_PORT": "80",
            "XANADU_CLOUD_TLS": "False",
        }

    def test_save_multiple_times(self, settings):
        """Tests that settings can be saved to a .env file multiple times."""
        path_to_env_file = settings.model_config["env_file"]

        settings.REFRESH_TOKEN = None
        settings.save()
        assert "XANADU_CLOUD_REFRESH_TOKEN" not in dotenv_values(path_to_env_file)

        settings.REFRESH_TOKEN = "f.o.o"
        settings.save()
        assert dotenv_values(path_to_env_file)["XANADU_CLOUD_REFRESH_TOKEN"] == "f.o.o"

        settings.REFRESH_TOKEN = "b.a.r"
        settings.save()
        assert dotenv_values(path_to_env_file)["XANADU_CLOUD_REFRESH_TOKEN"] == "b.a.r"

        settings.REFRESH_TOKEN = None
        settings.save()
        assert "XANADU_CLOUD_REFRESH_TOKEN" not in dotenv_values(path_to_env_file)

    def test_save_to_nonexistent_directory(self, monkeypatch):
        """Tests that settings can be saved to a .env file in a nonexistent directory."""
        with TemporaryDirectory() as env_dir:
            env_file = os.path.join(env_dir, "foo", "bar", ".env")
            monkeypatch.setitem(xcc.Settings.model_config, "env_file", env_file)

            xcc.Settings().save()
            assert os.path.exists(env_file) is True
