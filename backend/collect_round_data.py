# Install python dependencies
from dotenv import load_dotenv
import os

# Import project dependencies
from functions.logging_functions import (
    configure_logging
)
from functions.data_functions import (
    RoundData
)


# Load environment variables
load_dotenv()
email = os.getenv('email')
password = os.getenv('password')

# Configure logger
logger = configure_logging()

# Define RoundData object
app = RoundData(logger=logger)

logger.info("Logging into golf record site...")
app.login_to_round_site()
logger.info("Login successful\n")

# logger.info("Navigating to performance tab...")
# app.navigate_to_performance_tab()
# logger.info("Performance tab successfully loaded\n")

# logger.info("Loading all historic round data...")
# app.load_all_round_data()
# logger.info("All historic round data loaded\n")

# logger.info("Collect round report urls...")
# round_report_links = app.collect_round_urls()
# logger.info("All round urls collected\n")

x = app.collect_scorecard_data(round_links=['https://www.hole19golf.com/performance/rounds/mXw0hA'])

print(x)
