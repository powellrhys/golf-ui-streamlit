# Import dependencies
from unittest.mock import patch
from shared import Variables
import pytest

class TestVariables:
    """
    Test suite for the Variables class.

    Covers both 'backend' and 'streamlit' sources, ensuring
    environment variables or mocked secrets are correctly loaded
    into the Variables object.
    """

    def test_variables_backend_source(self, monkeypatch):
        """
        Verify Variables with source='backend'.

        Ensures environment variables are read correctly,
        attributes are assigned, and dict-like access works.
        """
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

        # Initialize Variables object using 'backend' source
        vars_obj = Variables(source="backend")

        # Verify attributes are correctly assigned
        assert vars_obj.blob_account_connection_string == "fake_blob_conn"
        assert vars_obj.golf_course_name == "Pebble Beach"
        assert vars_obj.round_site_player_name == "Tiger Woods"
        assert vars_obj.chromedriver_path == "/usr/local/bin/chromedriver"
        assert vars_obj.round_site_base_url == "https://roundsite.test"
        assert vars_obj.round_site_username == "rounduser"
        assert vars_obj.round_site_password == "roundpass"
        assert vars_obj.trackman_username == "tmuser"
        assert vars_obj.trackman_password == "tmpass"

        # Test dict-like access returns correct values
        assert vars_obj["golf_course_name"] == "Pebble Beach"

        # Accessing a nonexistent key raises KeyError
        with pytest.raises(KeyError):
            _ = vars_obj["nonexistent_key"]

    def test_variables_streamlit_source(self):
        """
        Verify Variables with source other than 'backend'.

        Ensures Streamlit secrets are read correctly and
        default values are used when environment variables are missing.
        """
        # Define fake Streamlit secrets
        fake_secrets = {
            "general": {
                "blob_storage_connection_string": "secret_blob_conn",
                "golf_course_name": "Augusta National",
            }
        }

        # Patch Streamlit module to use fake secrets
        with patch("shared.functions.variables.st") as mock_st:
            mock_st.secrets = fake_secrets

            # Initialize Variables object with 'streamlit' source
            vars_obj = Variables(source="streamlit")

            # Verify attributes are correctly loaded from secrets
            assert vars_obj.blob_account_connection_string == "secret_blob_conn"
            assert vars_obj.golf_course_name == "Augusta National"

            # Defaults for unspecified attributes come from os.getenv or fallback
            assert vars_obj.chromedriver_path == "chromedriver.exe"
