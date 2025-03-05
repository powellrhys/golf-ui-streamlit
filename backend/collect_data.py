# Install python dependencies
from dotenv import load_dotenv
import os

# Import project functions
from functions import (
    configure_driver,
    login_to_trackman,
    collect_trackman_access_token,
    collect_range_session_ids,
    collect_range_session_data,
    collect_clubs_used_at_range,
    summarise_range_club_data
)

# Load environment variables
load_dotenv()
email = os.getenv('email')
password = os.getenv('password')

# Configure Selenium Driver
driver = configure_driver(driver_path='chromedriver.exe',
                          headless=False)

driver = login_to_trackman(driver=driver,
                           email=email,
                           password=password)

access_token = collect_trackman_access_token(driver=driver)

session_ids = collect_range_session_ids(access_token=access_token)


session_ids = ['3ccb36d7-a99c-4fad-8c0a-de1eea457a1d',
               'bb5f8124-9f77-4e3a-8f2e-87c7badab8e7',
               '09bd755e-53de-4745-a7b0-08965a10b89c',
               'c75105f6-2f76-4e91-bbf7-60af36a81767',
               '97c0f6c4-9302-43f2-a758-5633ecfbabe8',
               'f012d33b-2777-41bb-9be9-3d9489f4e1d6',
               '57ccdd1a-fae5-49ce-8a37-024367ecf06c']

for range_id in session_ids:
    collect_range_session_data(range_id)

clubs = collect_clubs_used_at_range()

for club in clubs:
    summarise_range_club_data(club)
