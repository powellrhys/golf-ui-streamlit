# Import dependencies
from .trackman_aggregator import TrackManAggregator
from .trackman_parser import TrackManParser
from .trackman_auth import TrackManAuth
import logging

class TrackmanScrapper:
    """
    """
    def __init__(self, logger: logging.Logger) -> None:
        """
        Initialize the Hole19Scrapper.

        Args: logger (logging.Logger): Logger instance for recording progress and errors.
        """
        self.logger = logger

    def run(self, driver_path: str, headless: bool):
        """
        Execute the full Trackman scraping workflow.

        Logs into Trackman, collects round URLs, parses scorecards, saves data
        to blob storage, and aggregates hole-level results.

        Args:
            driver_path (str): Path to the ChromeDriver executable.
            headless (bool): Whether to run Chrome in headless mode.

        Returns: None

        Raises: BaseException: If scorecard data cannot be collected or exported.
        """
        # Initiate Trackman object
        self.auth = TrackManAuth(logger=self.logger, driver_path=driver_path, headless=headless)
        self.auth.initiate_driver()

        # Login to trackman site
        self.logger.info("Logging into golf Trackman application...")
        self.auth.login_to_website()
        self.logger.info("Login successful\n")

        # Collect trackman access token
        self.logger.info("Collecting Trackman access token...")
        access_token = self.auth.collect_trackman_access_token()
        self.logger.info("Access token collected\n")

        # Initiate Trackman Parser
        self.parser = TrackManParser(logger=self.logger)

        # Collect range session ids
        self.logger.info("Collecting range session ids...")
        session_ids = self.parser.collect_range_session_ids(access_token=access_token)
        new_session_ids = self.parser.identify_new_data(range_session_ids=session_ids)
        self.logger.info("Range session ids collected\n")

        # Collect new range session data
        if new_session_ids:

            # Collect range session data
            self.logger.info("Collecting new range session data...")
            for i, range_id in enumerate(new_session_ids, start=1):
                self.logger.info(f'{i}/{len(new_session_ids)} Collecting range data for session: {range_id}...')
                self.parser.collect_range_session_data(session_id=range_id)
            self.logger.info("All new range session data collected \n")

            # Initialise Trackman Aggregator Class
            self.aggregator = TrackManAggregator(logger=self.logger)

            # Collect a list of clubs used in a trackman range
            self.logger.info("Collecting list of clubs used at Trackman Range...")
            clubs = self.aggregator.collect_clubs_used_at_range()
            self.logger.info("Clubs used at Trackman range collected\n")

            # Summarise club data
            self.logger.info("Summarising data...")
            for i, club in enumerate(clubs):
                self.logger.info(f'{i + 1}/{len(clubs)} Summarising club data for {club}')
                self.aggregator.summarise_range_club_data(club)
            self.logger.info("All club data summarised \n")

            # Generate yardage book
            self.logger.info("Generating yardage book...")
            self.aggregator.collect_yardage_book_data(clubs=clubs)
            self.logger.info("Yardage Book Generated")

        # Handle scenario when no new range data has been collected
        else:
            self.logger.info("Pipeline Complete - No new range data recorded since last pipeline run")
