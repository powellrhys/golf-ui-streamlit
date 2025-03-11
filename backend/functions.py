# Import selenium dependencies
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium import webdriver

# Import python dependencies
from datetime import datetime
from typing import Callable
import statistics as stat
import functools
import requests
import warnings
import logging
import json
import time
import os


def configure_logging() -> logging.Logger:
    '''
    Configures and returns a logger instance.

    This function sets up a basic logger named 'BASIC' with an INFO level.
    It ignores warnings, formats log messages with timestamps, and outputs
    logs to the console via a stream handler.

    Returns:
        logging.Logger: Configured logger instance.
    '''
    # Ignore warnings
    warnings.filterwarnings("ignore")

    # Configure Logger
    logger = logging.getLogger('BASIC')
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(formatter)
    logger.addHandler(log_handler)

    return logger


def log_execution(
    func: Callable
) -> Callable:
    '''
    '''
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Collect logger from kwargs
        logger = kwargs.get('logger')

        # Log execution of function
        if logger:
            logger.info(f"Executing {func.__name__}...")

        try:

            # Execute function passed into decorator
            result = func(*args, **kwargs)

            # Log successful execution of function
            if logger:
                logger.info(f"Function {func.__name__} executed successfully \n")

            return result

        except BaseException as e:
            logger.error(f"Failed to execute {func.__name__} - {e}")
            raise

    return wrapper


@log_execution
def configure_driver(
    driver_path: str = 'chromedriver.exe',
    headless: bool = False,
    logger: logging.Logger = None
) -> WebDriver:
    '''
    Decorator that logs the execution of a function.

    This decorator retrieves a logger from the function's keyword arguments (if provided),
    logs the function's execution start, and logs either a success or failure message
    upon completion or exception.

    Args:
        func (Callable): The function to be decorated.

    Returns:
        Callable: The wrapped function with logging functionality.

    Raises:
        BaseException: If the decorated function raises an exception, it is logged and re-raised.
    '''
    # Configure logging to suppress unwanted messages
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")

    # If headless declared, activate headless mode
    if headless:
        chrome_options.add_argument("--headless")

    # Configure Driver with options
    service = Service(executable_path=driver_path)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.maximize_window()

    return driver


@log_execution
def login_to_trackman(
    driver: WebDriver,
    email: str,
    password: str,
    logger: logging.Logger = None
) -> WebDriver:
    '''
    Attempts to log in to the Trackman portal using the provided credentials.

    The function navigates to the Trackman reports page, enters the email and password,
    and triggers the login process using JavaScript. It retries up to 5 times in case of failure.

    Args:
        driver (WebDriver): The Selenium WebDriver instance.
        email (str): The email address for login.
        password (str): The password for login.
        logger (logging.Logger, optional): Logger instance for logging attempts and failures.

    Returns:
        WebDriver: The WebDriver instance after a successful login.

    Raises:
        Exception: If login fails after 5 attempts.
    '''
    for retries in range(5):
        try:
            # Navigate the trackman report page
            driver.get("https://portal.trackmangolf.com/player/activities?type=reports")

            # Enter Password into login form
            WebDriverWait(driver, 10) \
                .until(EC.presence_of_element_located((By.ID, 'Email')))
            driver.find_element(By.ID, 'Email').send_keys(email)

            # Enter Password into login form
            WebDriverWait(driver, 10) \
                .until(EC.presence_of_element_located((By.ID, 'Password')))
            password_field = driver.find_element(By.ID, 'Password')
            password_field.send_keys(password)

            # Trigger JavaScript directly to simulate the button click
            time.sleep(1)
            logger.info(f"Attempt {retries + 1}: Logging into Trackman")
            driver.execute_script("signinBtnClicked()")

            return driver

        except BaseException:
            time.sleep(1)
            driver.close()

    logger.error('Failed to login to trackman')
    raise


@log_execution
def collect_trackman_access_token(
    driver: WebDriver,
    logger: logging.Logger
) -> str:
    '''
    Retrieves the Trackman access token from the API.

    This function navigates to the Trackman API endpoint, extracts the JSON response
    from the page, and retrieves the access token. If an error occurs, it logs the failure.

    Args:
        driver (WebDriver): The Selenium WebDriver instance used for navigation.
        logger (logging.Logger): Logger instance for logging errors.

    Returns:
        str: The access token extracted from the API response.

    Raises:
        BaseException: If an error occurs while parsing the response or retrieving the token.
    '''
    # Navigate to authentication url
    driver.get("https://portal.trackmangolf.com/api/account/me")

    # Locate the <body> tag and get its inner HTML (content inside the body tag)
    body_content = driver.find_element("tag name", "pre").get_attribute("innerHTML")

    # Parse the JSON string
    try:
        # Collect json response
        json_data = json.loads(body_content)

        # Close driver
        driver.close()

        return json_data['accessToken']

    except BaseException as e:
        logger.error(f"Failed to collect trackman access token - {e}")


@log_execution
def collect_range_session_ids(
    access_token: str,
    logger: logging.Logger = None
) -> list:
    '''
    Fetches range session report IDs from the Trackman API.

    This function queries the Trackman GraphQL API to retrieve a list of
    range session activities associated with the authenticated user. It extracts
    and returns session report IDs from the API response. The function attempts
    up to 5 retries in case of request failures.

    Args:
        access_token (str): The authentication token required for API access.
        logger (logging.Logger, optional): Logger instance for logging attempts and failures.

    Returns:
        list: A list of extracted range session report IDs.

    Raises:
        Exception: If the function fails to retrieve data after 5 attempts.
    '''
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
            logger.info(f'Attempt {retry + 1}: Fetching range session ids')
            response = requests.post(url, json=body, headers=headers)

            # Check for a successful response
            if response.status_code == 200:
                data = response.json()['data']['me']['activities']['items']
                return [activitiy['reportLink'].split('ReportId=')[-1] for activitiy in data]

        except BaseException:
            time.sleep(3 + (2 ** retry))

    logger.error('Failed to collect range session ids')
    raise


@log_execution
def collect_range_session_data(
    session_id: str,
    logger: logging.Logger = None
) -> None:
    '''
    Collects and saves range session data from the Trackman API.

    This function sends a POST request to retrieve session data for a
    given session ID. If successful, it saves the response as a JSON
    file in the 'data/full_session_summary' directory. The function
    retries the request up to 5 times in case of failures.

    Args:
        session_id (str): The unique identifier of the range session.
        logger (logging.Logger, optional): Logger instance for logging attempts and failures.

    Returns:
        None

    Raises:
        Exception: If the function fails to retrieve the session data after 5 attempts.
    '''
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

                # Define output file path
                file_path = \
                    'data/full_session_summary/session-' + \
                    f"{response.json()['StrokeGroups'][0]['Date']}-" + \
                    f"{session_id}.json"

                # Write the list to the JSON file
                with open(file_path, 'w') as json_file:
                    json.dump(response.json(), json_file, indent=5)

                # Log successful action
                logger.info(f"{response.json()['StrokeGroups'][0]['Date']}-"
                            f"{session_id}.json range data collected")

                return

        except BaseException:
            time.sleep(3 + (2 ** retry))

    logger.error('Failed to collect range session data')


@log_execution
def collect_clubs_used_at_range(
    logger: logging.Logger = None
) -> list:
    '''
    Collects and returns a list of unique clubs used in all range sessions.

    This function iterates through all JSON files in the specified directory
    (`data/full_session_summary/`), extracts the clubs used in each session,
    and returns a sorted list of unique club names.

    Args:
        logger (logging.Logger, optional): Logger instance for logging actions. Default is None.

    Returns:
        list: A sorted list of unique club names used in the range sessions.

    Raises:
        Exception: If there is an error in reading the files or processing the data.
    '''
    # Specify the directory path
    directory = "data/full_session_summary/"

    # List all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    clubs = []
    for file_name in files:
        # Read the JSON file
        with open(f'{directory}/{file_name}', 'r') as json_file:
            data = json.load(json_file)

        # Collect a list of clubs used in the session
        session_clubs = [club['Club'] for club in data['StrokeGroups']]
        clubs.extend(session_clubs)

    # Sort clubs alphabetically
    clubs = list(set(clubs))
    clubs.sort()

    return clubs


@log_execution
def summarise_range_club_data(
    club: str,
    logger: logging.Logger = None
) -> None:
    '''
    Summarizes and stores range session data for a specific club.

    This function processes all JSON files in the `data/full_session_summary/`
    directory, extracts the stroke data for a specified club, sorts it by
    time in descending order, and saves the summarized data to a JSON file
    in the `data/club_summary/` directory.

    Args:
        club (str): The name of the club to summarize data for.
        logger (logging.Logger, optional): Logger instance for logging actions. Default is None.

    Returns:
        None

    Raises:
        Exception: If there is an error in reading the files, processing the data
                    or writing the summary to a file.
    '''
    # Specify the directory path
    directory = "data/full_session_summary/"

    # List all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    # Iterate through all sessions and summarise data at a club level
    range_club_summary = []
    for file_name in files:
        # Read the JSON file
        with open(f'{directory}/{file_name}', 'r') as json_file:
            data = json.load(json_file)

        # Filter data based on club being inspected
        range_data = [club_data['Strokes'] for club_data in data['StrokeGroups'] if club_data['Club'] == club]
        range_club_summary.extend(range_data)

    # Sort by 'Time' key in descending order (most recent first)
    sorted_data = sorted(range_club_summary[0], key=lambda x: datetime.fromisoformat(x['Time']), reverse=True)

    # Write the list to the JSON file
    with open(f'data/club_summary/{club}.json', 'w') as json_file:
        json.dump(sorted_data, json_file, indent=5)


@log_execution
def collect_yardage_book_data(
    clubs: str,
    logger: logging.Logger = None
) -> None:
    '''
    Collects and summarizes yardage data for a list of clubs and stores it in JSON files.

    This function processes yardage data for multiple clubs, calculating various
    statistics (such as average carry, max distance, ball speed, etc.) for each
    club across a range of shot counts (10, 20, 30, 40, 50, 100). The summarized
    data is saved in JSON files with the respective shot count in the filename.

    Args:
        clubs (list): A list of club names to process yardage data for.
        logger (logging.Logger, optional): Logger instance for logging actions. Default is None.

    Returns:
        None

    Raises:
        Exception: If there is an error in reading the files, processing the data,
                    or writing the summary to a file.
    '''
    # Iterate through clubs and latest x amount of shots
    for shots in [10, 20, 30, 40, 50, 100]:
        yardage_book = []
        for club in clubs:

            # Read the JSON file
            with open(f'data/club_summary/{club}.json', 'r') as json_file:
                data = json.load(json_file)[0:shots]

            # Generate dictionary of club data
            club_data = {
                'avg_carry': round(stat.mean([i['Measurement']['Carry'] for i in data]), 2),
                'min_carry': round(min([i['Measurement']['Carry'] for i in data]), 2),
                'max_carry': round(max([i['Measurement']['Carry'] for i in data]), 2),
                'avg_distance': round(stat.mean([i['Measurement']['Total'] for i in data]), 2),
                'min_distance': round(min([i['Measurement']['Total'] for i in data]), 2),
                'max_distance': round(max([i['Measurement']['Total'] for i in data]), 2),
                'avg_all_speed': round(stat.mean([i['Measurement']['BallSpeed'] for i in data]), 2),
                'avg_max_height': round(stat.mean([i['Measurement']['MaxHeight'] for i in data]), 2),
                'avg_launch_angle': round(stat.mean([i['Measurement']['LaunchAngle'] for i in data]), 2)
            }
            yardage_book.append({club: club_data})

        # Write the list to the JSON file
        with open(f'data/yardage_summary/latest_{shots}_shot_summary.json', 'w') as json_file:
            json.dump(yardage_book, json_file, indent=5)
