# test_variables.py
import pytest
from unittest.mock import patch
from shared import Variables


def test_variables_backend_source(monkeypatch):
    """Test Variables class with source='backend' using environment variables."""
    # Mock environment variables
    monkeypatch.setenv("blob_storage_connection_string", "fake_blob_conn")
    monkeypatch.setenv("golf_course_name", "Pebble Beach")
    monkeypatch.setenv("round_site_player_name", "Tiger Woods")
    monkeypatch.setenv("chromedriver_path", "/usr/local/bin/chromedriver")
    monkeypatch.setenv("round_site_base_url", "https://roundsite.test")
    monkeypatch.setenv("round_site_username", "rounduser")
    monkeypatch.setenv("round_site_password", "roundpass")
    monkeypatch.setenv("trackman_username", "tmuser")
    monkeypatch.setenv("trackman_password", "tmpass")

    vars_obj = Variables(source="backend")

    assert vars_obj.blob_account_connection_string == "fake_blob_conn"
    assert vars_obj.golf_course_name == "Pebble Beach"
    assert vars_obj.round_site_player_name == "Tiger Woods"
    assert vars_obj.chromedriver_path == "/usr/local/bin/chromedriver"
    assert vars_obj.round_site_base_url == "https://roundsite.test"
    assert vars_obj.round_site_username == "rounduser"
    assert vars_obj.round_site_password == "roundpass"
    assert vars_obj.trackman_username == "tmuser"
    assert vars_obj.trackman_password == "tmpass"

    # Test dict-like access
    assert vars_obj["golf_course_name"] == "Pebble Beach"

    with pytest.raises(KeyError):
        _ = vars_obj["nonexistent_key"]


def test_variables_streamlit_source():
    """Test Variables class with source!='backend' using mocked st.secrets."""
    fake_secrets = {
        "general": {
            "blob_storage_connection_string": "secret_blob_conn",
            "golf_course_name": "Augusta National",
            "round_site_player_name": "Jack Nicklaus"
        }
    }

    with patch("shared.functions.variables.st") as mock_st:
        mock_st.secrets = fake_secrets

        vars_obj = Variables(source="streamlit")

        assert vars_obj.blob_account_connection_string == "secret_blob_conn"
        assert vars_obj.golf_course_name == "Augusta National"
        assert vars_obj.round_site_player_name == "Jack Nicklaus"
        # defaults come from os.getenv (will be None if not set in env)
        assert vars_obj.chromedriver_path == "chromedriver.exe"
