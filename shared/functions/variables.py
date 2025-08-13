# Install python dependencies
from dotenv import load_dotenv
import os

load_dotenv()

class Variables():
    """
    """
    def __init__(self):
        """
        """
        self.chromedriver_path = os.getenv("chromedriver_path", default="chromedriver.exe")
        self.blob_account_connection_string = os.getenv("blob_account_connection_string")
        self.golf_course_name = os.getenv("golf_course_name")
        self.round_site_base_url = os.getenv("round_site_base_url")
        self.round_site_username = os.getenv("round_site_username")
        self.round_site_password = os.getenv("round_site_password")

    def __getitem__(self, key):
        """
        """
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(f"{key} not found in Variables")
