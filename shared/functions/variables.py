# Install python dependencies
from dotenv import load_dotenv
import streamlit as st
import os

load_dotenv()

class Variables():
    """
    Centralized configuration manager for environment-based application variables.

    This class loads application configuration values from environment variables
    (via `python-dotenv`) and exposes them as attributes. It supports both
    general backend settings, golf round site credentials, Trackman credentials,
    and Azure Blob Storage connection details.
    """
    def __init__(self, source: str = "backend"):
        """
        Initialize and load all required environment variables into attributes.

        Attributes:
            chromedriver_path (str): Path to the ChromeDriver executable.
            blob_account_connection_string (str): Azure Blob Storage connection string.
            golf_course_name (str): Name of the golf course for filtering/aggregation.

            round_site_base_url (str): Base URL for the golf round tracking site.
            round_site_username (str): Username for the round site login.
            round_site_password (str): Password for the round site login.
            round_site_player_name (str): Display name of the player on the round site.

            trackman_username (str): Username for Trackman login.
            trackman_password (str): Password for Trackman login.
        """
        # Shared variables
        if source == "backend":
            self.blob_account_connection_string = os.getenv("blob_storage_connection_string")
            self.golf_course_name = os.getenv("golf_course_name")
            self.round_site_player_name = os.getenv("round_site_player_name")
        else:
            self.blob_account_connection_string = st.secrets["general"]["blob_storage_connection_string"]
            self.golf_course_name = st.secrets["general"]["golf_course_name"]
            self.round_site_player_name = st.secrets["general"]["round_site_player_name"]

        # General Backend variables
        self.chromedriver_path = os.getenv("chromedriver_path", default="chromedriver.exe")

        # Backend - Scorecard variables
        self.round_site_base_url = os.getenv("round_site_base_url")
        self.round_site_username = os.getenv("round_site_username")
        self.round_site_password = os.getenv("round_site_password")

        # Backend - Trackman variables
        self.trackman_username = os.getenv("trackman_username")
        self.trackman_password = os.getenv("trackman_password")

    def __getitem__(self, key):
        """
        Allow dictionary-style access to environment variable attributes.

        Args:
            key (str): The attribute name to retrieve.

        Returns:
            Any: The value of the requested attribute.

        Raises:
            KeyError: If the requested key does not exist as an attribute.
        """
        # If class as attributes, return items
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in Variables")
