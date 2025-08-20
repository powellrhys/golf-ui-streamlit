# Import dependencies
from ..interfaces.data_collection_base import AbstractDataCollection
from selenium.webdriver.support import expected_conditions as EC
from backend.functions.selenium_driver import SeleniumDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from shared import Variables, BlobClient
from datetime import datetime
import statistics as stat
import logging
import requests
import time
import json

class TrackMan(AbstractDataCollection, SeleniumDriver, BlobClient):
    """
    Client for collecting and uploading TrackMan golf range session data.

    This class uses Selenium to log in to the TrackMan portal, collect range session IDs,
    retrieve session data via the TrackMan API, and export the data to Azure Blob Storage.

    Attributes:
        driver (WebDriver): Selenium WebDriver instance for web automation.
        logger (logging.Logger): Logger for tracking events and errors.
        vars (Variables): Configuration variables (e.g., credentials).
    """
    def __init__(
        self,
        logger: logging.Logger,
        driver_path: str = 'chromedriver.exe',
        headless: bool = False
    ) -> None:
        """
        Initialize the TrackMan client with Selenium WebDriver and logger.

        Args:
            logger (logging.Logger): Logger instance for logging messages.
            driver_path (str, optional): Path to the ChromeDriver executable. Defaults to 'chromedriver.exe'.
            headless (bool, optional): Whether to run the browser in headless mode. Defaults to False.
        """
        super().__init__()
        self.driver = self.configure_driver(driver_path=driver_path, headless=headless)
        self.logger = logger
        self.vars = Variables()

    def login_to_website(self) -> None:
        """
        Log in to the TrackMan portal using credentials from Variables.

        Raises:
            Exception: If login fails due to any unexpected error.
        """
        try:
            # Navigate the trackman report page
            self.driver.get("https://portal.trackmangolf.com/player/activities?type=reports")

            # Enter Password into login form
            WebDriverWait(self.driver, 10) \
                .until(EC.presence_of_element_located((By.ID, 'Email')))
            self.driver.find_element(By.ID, 'Email').send_keys(self.vars.trackman_username)

            # Enter Password into login form
            WebDriverWait(self.driver, 10) \
                .until(EC.presence_of_element_located((By.ID, 'Password')))
            password_field = self.driver.find_element(By.ID, 'Password')
            password_field.send_keys(self.vars.trackman_password)

            # Trigger JavaScript directly to simulate the button click
            self.driver.execute_script("signinBtnClicked()")

        # Handle exception if driver fails to login
        except BaseException:
            self.logger.error('Failed to login to trackman')
            raise

    def collect_trackman_access_token(self) -> str:
        """
        Collect the TrackMan API access token for authenticated requests.

        Returns:
            str: Access token string.

        Raises:
            Exception: If the access token cannot be retrieved.
        """
        # Navigate to authentication url
        self.driver.get("https://portal.trackmangolf.com/api/account/me")

        # Locate the <body> tag and get its inner HTML (content inside the body tag)
        body_content = self.driver.find_element("tag name", "pre").get_attribute("innerHTML")

        # Parse the JSON string
        try:
            # Collect json response
            json_data = json.loads(body_content)

            return json_data['accessToken']

        # Handle exception if driver fails to collect access token
        except BaseException as e:
            self.logger.error(f"Failed to collect trackman access token - {e}")

    def collect_range_session_ids(
        self,
        access_token: str
    ) -> list:
        """
        Collect a list of range session IDs using the TrackMan GraphQL API.

        Args:
            access_token (str): TrackMan API access token.

        Returns:
            list: List of range session IDs.

        Raises:
            Exception: If session IDs cannot be retrieved after multiple retries.
        """
        # Define the URL for the GraphQL endpoint
        url = "https://api.trackmangolf.com/graphql"

        # Define the headers
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        # Define the payload (GraphQL query and variables)
        body = {
            "query": """
                query getPlayerActivities($take: Int, $skip: Int, $activityKinds: [ActivityKind!]) {
                    me {
                        activities(take: $take, skip: $skip, kinds: $activityKinds) {
                            items {
                                id
                                kind
                                ... on DynamicReportActivity {
                                    reportLink
                                }
                                ... on CombineTestActivity {
                                    dynamicReportPath
                                }
                                ... on TestActivity {
                                    dynamicReportPath
                                }
                            }
                        }
                    }
                }""",
            "variables": {
                "take": 50,
                "skip": 0,
                "activityKinds": ["DYNAMIC_REPORT", "TEST"]
            }
        }

        # Attempt to collect range session ids at least 5 times
        for retry in range(5):
            try:
                # Make the POST request
                self.logger.info(f'Attempt {retry + 1}: Fetching range session ids')
                response = requests.post(url, json=body, headers=headers)

                # Check for a successful response
                if response.status_code == 200:
                    data = response.json()['data']['me']['activities']['items']
                    return [activitiy['reportLink'].split('ReportId=')[-1] for activitiy in data]

            except BaseException:
                time.sleep(3 + (2 ** retry))

        # Handle error if failure occured
        self.logger.error('Failed to collect range session ids')
        raise

    def collect_range_session_data(
        self,
        session_id: str
    ) -> None:
        """
        Collect and upload data for a specific range session.

        Retrieves session data from the TrackMan API and uploads it to Azure Blob Storage.

        Args:
            session_id (str): The ID of the range session to collect.

        Raises:
            Exception: If session data cannot be retrieved or uploaded.
        """
        # URL and API endpoint
        url = "https://golf-player-activities.trackmangolf.com/api/reports/getreport"

        # Headers
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0"
            )
        }

        # JSON payload (body)
        payload = {
            "ReportId": session_id
        }

        # Implement retires into report collection
        for retry in range(5):
            try:
                # Send POST request
                response = requests.post(url, json=payload, headers=headers, timeout=10)

                # Check if request was successful
                if response.status_code == 200:

                    # Define file name
                    file_name = f"{response.json()['StrokeGroups'][0]['Date']}-session-{session_id}.json"

                    self.export_dict_to_blob(
                        data=response.json(),
                        container='golf',
                        output_filename=f'trackman_session_summary/{file_name}')

                    return

            except BaseException:
                time.sleep(3 + (2 ** retry))

        self.logger.error(f'Failed to collect range session data for session id {session_id}')


class TrackManAggregator(BlobClient):
    """
    Aggregates and summarizes TrackMan session data from Azure Blob Storage.

    Provides methods to extract clubs used, summarize range data per club,
    and generate yardage book summaries.

    Attributes:
        logger (logging.Logger): Logger for tracking events and errors.
        vars (Variables): Configuration variables.
    """
    def __init__(self, logger: logging.Logger):
        """
        Initialize the TrackManAggregator with a logger and variable configuration.

        Args:
            logger (logging.Logger): Logger instance for logging messages.
        """
        super().__init__()
        self.logger = logger
        self.vars = Variables()

    def collect_clubs_used_at_range(self) -> list:
        """
        Collect a sorted list of unique clubs used across all range sessions.

        Returns:
            list: Alphabetically sorted list of clubs used.
        """
        # Collect a list of files in a blob container
        files = self.list_blob_filenames(container_name="golf", directory_path="trackman_session_summary")

        clubs = []
        for file_name in files:
            # Read the JSON file
            data = self.read_blob_to_dict(container="golf", input_filename=file_name)

            # Collect a list of clubs used in the session
            session_clubs = [club['Club'] for club in data['StrokeGroups']]
            clubs.extend(session_clubs)

        # Sort clubs alphabetically
        clubs = list(set(clubs))
        clubs.sort()

        return clubs

    def summarise_range_club_data(self, club: str) -> None:
        """
        Summarize all range session data for a specific club.

        Filters strokes by the given club and exports the sorted summary to Blob Storage.

        Args:
            club (str): Club name to summarize data for.
        """
        # List all files in the full_session_summary directory
        files = self.list_blob_filenames(container_name="golf", directory_path="trackman_session_summary")

        # Iterate through all sessions and summarise data at a club level
        range_club_summary = []
        for file_name in files:
            # Read the JSON file
            data = self.read_blob_to_dict(container="golf", input_filename=file_name)

            # Filter data based on club being inspected
            range_data = [club_data['Strokes'] for club_data in data['StrokeGroups'] if club_data['Club'] == club]
            range_club_summary.extend(range_data)

        # Sort by 'Time' key in descending order (most recent first)
        sorted_data = sorted(range_club_summary[0], key=lambda x: datetime.fromisoformat(x['Time']), reverse=True)

        # Write the list to the JSON file
        self.export_dict_to_blob(
            data=sorted_data,
            container='golf',
            output_filename=f'trackman_club_summary/{club}.json')

    def collect_yardage_book_data(self, clubs: str) -> None:
        """
        Generate yardage book summaries for multiple clubs using recent shots.

        Aggregates statistics such as average carry, max/min distance, ball speed, launch angle,
        and exports JSON summaries for the latest 10, 20, 30, 40, 50, and 100 shots per club.

        Args:
            clubs (str): List of club names to include in the yardage book summaries.
        """
        # Iterate through clubs and latest x amount of shots
        for shots in [10, 20, 30, 40, 50, 100]:
            yardage_book = []
            for club in clubs:

                # Read the JSON file
                data = self.read_blob_to_dict(container="golf",
                                              input_filename=f"trackman_club_summary/{club}.json")[0:shots]

                # Generate dictionary of club data
                club_data = {
                    'avg_carry': round(stat.mean([i['Measurement']['Carry'] for i in data]), 2),
                    'min_carry': round(min([i['Measurement']['Carry'] for i in data]), 2),
                    'max_carry': round(max([i['Measurement']['Carry'] for i in data]), 2),
                    'avg_distance': round(stat.mean([i['Measurement']['Total'] for i in data]), 2),
                    'min_distance': round(min([i['Measurement']['Total'] for i in data]), 2),
                    'max_distance': round(max([i['Measurement']['Total'] for i in data]), 2),
                    'avg_all_speed': round(stat.mean([i['Measurement']['BallSpeed'] for i in data]), 2),
                    'avg_max_height': round(stat.mean([i['Measurement']['MaxHeight'] for i in data]), 2),
                    'avg_launch_angle': round(stat.mean([i['Measurement']['LaunchAngle'] for i in data]), 2)
                }
                yardage_book.append({club: club_data})

            # Write the list to the JSON file
            self.export_dict_to_blob(
                data=yardage_book,
                container='golf',
                output_filename=f'trackman_yardage_summary/latest_{shots}_shot_summary.json')
