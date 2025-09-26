# Import dependencies
from backend.functions.logging import configure_logging
from backend.functions.scorecard import Hole19Scrapper
from shared import Variables

# Configure logger
logger = configure_logging()

# Define script variables
vars = Variables()

# Initiate Hole 19 Scrapper and execute scrapper
app = Hole19Scrapper(logger=logger)
app.run(headless=True, driver_path=vars.chromedriver_path)
