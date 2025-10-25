# Import dependencies
from backend.functions.trackman import TrackmanScrapper
from backend.functions.logging import configure_logging
from shared import Variables

# Configure logger
logger = configure_logging()

# Define script variables
vars = Variables()

# Initiate Hole 19 Scrapper and execute scrapper
app = TrackmanScrapper(logger=logger)

# Trackman scrapper is currently out of action due to new captcha additions to the trackman UI
# app.run(headless=True, driver_path=vars.chromedriver_path)
