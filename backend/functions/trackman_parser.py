# Import dependencies
from backend.functions.selenium_driver import SeleniumDriver
from shared import Variables, BlobClient
import logging
import requests
import time

class TrackManParser(SeleniumDriver, BlobClient):
    """
    A parser for collecting and managing TrackMan range session data.

    This class integrates Selenium-based automation utilities with Azure Blob
    Storage client functionality to:
      - Retrieve session IDs via the TrackMan GraphQL API.
      - Identify new sessions not yet collected.
      - Download and upload session data into Azure Blob Storage.

    It inherits from:
        SeleniumDriver: Provides driver configuration and web automation tools.
        BlobClient: Provides methods to interact with Azure Blob Storage.
    """
    def __init__(
        self,
        logger: logging.Logger,
    ) -> None:
        """
        Initialize the TrackManParser with logging and configuration variables.

        Args:
            logger (logging.Logger): Logger instance for structured logging.
        """
        super().__init__()
        self.logger = logger
        self.vars = Variables()

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

    def identify_new_data(self, range_session_ids: list) -> list:
        """
        Identify TrackMan session IDs that have not yet been collected.

        Compares the provided list of session IDs against session summary files
        already stored in the "golf/trackman_session_summary" blob container.
        Any session IDs not present in storage are returned as new.

        Args: range_session_ids (list): A list of session IDs to check for new data.

        Returns: list: A list of session IDs that are not yet collected.
        """
        collected_sessions = self.list_blob_filenames(container_name="golf", directory_path="trackman_session_summary")

        collected_sessions_ids = [file.split("-session-")[-1].replace(".json", "") for file in collected_sessions]

        return list(set(range_session_ids) - set(collected_sessions_ids))

    def collect_range_session_data(self, session_id: str) -> None:
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
