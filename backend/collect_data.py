# Install python dependencies
from dotenv import load_dotenv
import os

# Import project functions
from backend.functions_old import (
    collect_trackman_access_token,
    collect_clubs_used_at_range,
    collect_range_session_data,
    collect_range_session_ids,
    summarise_range_club_data,
    collect_yardage_book_data,
    configure_logging,
    login_to_trackman,
    configure_driver
)

# Load environment variables
load_dotenv()
email = os.getenv('email')
password = os.getenv('password')

# Configure logger
logger = configure_logging()

# Configure Selenium Driver
driver = configure_driver(driver_path='chromedriver.exe',
                          headless=True,
                          logger=logger)

# Login to trackman
driver = login_to_trackman(driver=driver,
                           email=email,
                           password=password,
                           logger=logger)

# Collect trackman access token
access_token = collect_trackman_access_token(driver=driver,
                                             logger=logger)

# Collect range session ids
session_ids = collect_range_session_ids(access_token=access_token,
                                        logger=logger)

# Collect range session id
for i, range_id in enumerate(session_ids):
    logger.info(f'{i + 1}/{len(session_ids)} Collecting range data for session: {range_id}')
    collect_range_session_data(session_id=range_id,
                               logger=logger)

# Collect a list of clubs used on the range
clubs = collect_clubs_used_at_range(logger=logger)

# Summarise club data
for i, club in enumerate(clubs):
    logger.info(f'{i + 1}/{len(clubs)} Summarising club data for {club}')
    summarise_range_club_data(club)

# Generate yardage book
collect_yardage_book_data(clubs=clubs,
                          logger=logger)
