# Import dependencies
from .scorecard_aggregator import RoundAggregator
from .scorecard_navigator import Hole19Navigator
from .scorecard_parser import ScorecardParser
from shared import BlobClient
import logging

class Hole19Scrapper:
    """
    Orchestrates the scraping of Hole19 scorecards.

    Coordinates navigation, parsing, exporting to blob storage, and
    aggregation of round-level and hole-level data.
    """
    def __init__(self, logger: logging.Logger) -> None:
        """
        Initialize the Hole19Scrapper.

        Args: logger (logging.Logger): Logger instance for recording progress and errors.
        """
        self.logger = logger

    def run(self, driver_path: str, headless: bool):
        """
        Execute the full Hole19 scraping workflow.

        Logs into Hole19, collects round URLs, parses scorecards, saves data
        to blob storage, and aggregates hole-level results.

        Args:
            driver_path (str): Path to the ChromeDriver executable.
            headless (bool): Whether to run Chrome in headless mode.

        Returns: None

        Raises: BaseException: If scorecard data cannot be collected or exported.
        """
        # Initiate Hole19Navigator object
        self.navigator = Hole19Navigator(logger=self.logger, driver_path=driver_path, headless=headless)
        self.navigator.initiate_driver()

        # Login to Hole 19 website and collect scorecard urls
        self.logger.info("Logging into Hole 19...")
        self.navigator.login_to_website()
        self.logger.info("Login to Hole 19 completed \n")

        # Navigate to performance tab
        self.logger.info("Navigating to hole 19 performance tab...")
        self.navigator.navigate_to_performance_tab()
        self.logger.info("Performance tab navigated to successfully \n")

        # Load all rounds into memory
        self.logger.info("Loading all scorecards into view...")
        self.navigator.load_all_hole19_rounds()
        self.logger.info("All scorecards loaded into view \n")

        # Collect round urls
        self.logger.info("Collecting round urls...")
        urls = self.navigator.collect_round_urls()
        self.logger.info("Round url collect \n")

        # Close down selenium driver
        self.logger.info("Closing driver...")
        self.navigator.driver.close()
        self.logger.info("Driver successfully closed \n")

        # Initiate Scorecard Parser object
        self.parser = ScorecardParser(logger=self.logger, driver_path=driver_path, headless=headless)
        self.parser.initiate_driver()

        # Iterate through urls and collect scorecard data
        for index, url in enumerate(iterable=urls, start=1):
            try:
                # Log progress message
                self.logger.info(f"Scraping round {index} of {len(urls)}")

                # Collect Scorecard Data
                scorecard, file_name = self.parser.collect_scorecard_data(url=url)

                # Export data to blob
                BlobClient().export_dict_to_blob(data=scorecard, container="golf", output_filename=file_name)

            except BaseException as e:
                self.logger.error(f"Failed to collect and export scorecard data - {e}")

        # Initiate Round Aggregator
        self.aggregator = RoundAggregator(logger=self.logger)

        # Aggregate round data
        self.logger.info("Aggregating data at hole level...")
        self.aggregator.aggregate_holes_by_course()
        self.logger.info("Data aggregated to hole level \n")
