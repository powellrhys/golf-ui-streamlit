# Import project dependencies
from backend.functions import (
    configure_logging,
    RoundAggregator,
    RoundData
)
from shared import Variables

# Configure logger
logger = configure_logging()

# Define script variables
vars = Variables()

# Define RoundData object
app = RoundData(logger=logger,
                headless=True,
                driver_path=vars.chromedriver_path)

logger.info("Logging into golf scorecard application...")
app.login_to_round_site()
logger.info("Login successful\n")

logger.info("Navigating to performance tab...")
app.navigate_to_performance_tab()
logger.info("Performance tab successfully loaded\n")

logger.info("Loading all historic round data...")
app.load_all_round_data()
logger.info("All historic round data loaded\n")

logger.info("Collecting report urls...")
round_report_links = app.collect_round_urls()
logger.info("All report urls collected\n")

logger.info("Collect scorecard data...")
app.collect_scorecard_data(round_links=round_report_links[0:1])
logger.info("Scorecard data collected\n")

logger.info("Aggregating Hole by Hole Data...")
aggregator = RoundAggregator(logger=logger)
aggregator.aggregate_holes_by_course()
logger.info("Hole by hole data aggregated\n")
