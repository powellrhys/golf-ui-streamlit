# Import project dependencies
from backend.functions import (
    TrackManAggregator,
    configure_logging,
    TrackMan
)
from shared import Variables

# Configure logger
logger = configure_logging()

# Define script variables
vars = Variables()

# Define TrackMan object
app = TrackMan(logger=logger,
               headless=True,
               driver_path=vars.chromedriver_path)

# Login to trackman site
logger.info("Logging into golf Trackman application...")
app.login_to_website()
logger.info("Login successful\n")

# Collect trackman access token
logger.info("Collecting Trackman access token...")
access_token = app.collect_trackman_access_token()
logger.info("Access token collected\n")

# Collect range session ids
logger.info("Collecting range session ids...")
session_ids = app.collect_range_session_ids(access_token=access_token)
logger.info("Range session ids collected\n")

# Collect range session data
for i, range_id in enumerate(session_ids):
    logger.info(f'{i + 1}/{len(session_ids)} Collecting range data for session: {range_id}...')
    app.collect_range_session_data(session_id=range_id)

# Collect a list of clubs used in a trackman range
logger.info("Collecting list of clubs used at Trackman Range...")
aggregator = TrackManAggregator(logger=logger)
clubs = aggregator.collect_clubs_used_at_range()
logger.info("Clubs used at Trackman range collected\n")

# Summarise club data
for i, club in enumerate(clubs):
    logger.info(f'{i + 1}/{len(clubs)} Summarising club data for {club}')
    aggregator.summarise_range_club_data(club)

# Generate yardage book
aggregator.collect_yardage_book_data(clubs=clubs)
