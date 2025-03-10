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
import functools
import requests
import warnings
import logging
import json
import time
import os


def configure_logging() -> logging.Logger:
    '''
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
    '''
    # Configure logging to suppress unwanted messages
    chrome_options = Options()
    chrome_options.add_argument("--log-level=3")

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
    '''
    driver.get("https://portal.trackmangolf.com/api/account/me")

    # Locate the <body> tag and get its inner HTML (content inside the body tag)
    body_content = driver.find_element("tag name", "pre").get_attribute("innerHTML")

    # Parse the JSON string
    try:
        json_data = json.loads(body_content)

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
    '''
    # Define the URL for the GraphQL endpoint
    url = "https://api.trackmangolf.com/graphql"

    # Define the headers
    headers = {
        "authority": "api.trackmangolf.com",
        "method": "POST",
        "path": "/graphql",
        "scheme": "https",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,en-GB;q=0.8",
        "authorization": "Bearer " + access_token,
        "origin": "https://portal.trackmangolf.com",
        "priority": "u=1, i",
        "referer": "https://portal.trackmangolf.com/",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Microsoft Edge";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

    # Define the payload (GraphQL query and variables)
    body = {
        "query": """
            query getPlayerActivities($take: Int, $skip: Int, $kind: ImageKinds, $activityKinds: [ActivityKind!]) {
                me {
                    profile {
                        fullName
                    }
                    activities(take: $take, skip: $skip, kinds: $activityKinds) {
                        items {
                            id
                            kind
                            time
                            ... on DynamicReportActivity {
                                id
                                kind
                                reportLink
                                time
                                type
                            }
                            ... on CombineTestActivity {
                                id
                                kind
                                score
                                dynamicReportPath
                                time
                                maxClubSpeed
                                longestDrive
                                unit
                                bestDeci
                                numberOfStrokesAboveBestDeci
                                bestTarget
                            }
                            ... on ScreencastActivity {
                                id
                                kind
                                thumbnailUrl
                                videoUrl
                                time
                            }
                            ... on VideoActivityType {
                                videoId
                                kind
                                thumbnailUrl
                                videoUrl
                                time
                            }
                            ... on TestActivity {
                                id
                                kind
                                dynamicReportPath
                                time
                                avgScore
                            }
                            ... on RangeFindMyDistanceActivity {
                                numberOfStrokes
                            }
                            ... on RangePracticeActivity {
                                numberOfStrokes
                            }
                            ... on VirtualRangeSessionActivity {
                                strokeCount
                            }
                            ... on ShotAnalysisSessionActivity {
                                strokeCount
                            }
                            ... on SessionActivity {
                                strokeCount
                            }
                            ... on CoursePlayActivity {
                                kind
                                gameType
                                id
                                isInTournament
                                gameType
                                grossScore
                                stablefordPoints
                                netToPar
                                toPar
                                tournament {
                                    id
                                    mediaAssets {
                                        ...TournamentMediaAssets
                                    }
                                }
                                scorecard {
                                    dbId
                                }
                                course {
                                    displayName
                                    image(kind: $kind) {
                                        url
                                    }
                                }
                            }
                            ... on RangeBullsEyeActivity {
                                youPlaced
                                youWon
                                leaderboard {
                                    value1
                                    player {
                                        colorHex
                                        nickname
                                    }
                                    position
                                }
                                time
                            }
                            ... on RangeCaptureTheFlagActivity {
                                youPlaced
                                youWon
                                leaderboard {
                                    value1
                                    player {
                                        colorHex
                                        nickname
                                    }
                                    position
                                }
                                time
                            }
                            ... on RangeHitItActivity {
                                youPlaced
                                youWon
                                leaderboard {
                                    value1
                                    player {
                                        colorHex
                                        nickname
                                    }
                                    position
                                }
                                time
                            }
                        }
                        pageInfo {
                            hasNextPage
                            hasPreviousPage
                        }
                        totalCount
                    }
                }
            }
            fragment TournamentMediaAssets on MediaAsset {
                kind
                url
                isDefault
            }
        """,
        "variables": {
            "take": 50,
            "skip": 0,
            "activityKinds": ["DYNAMIC_REPORT", "TEST"],
            "kind": "SPLASH_WEBP"
        }
    }

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
    '''
    # URL and API endpoint
    url = "https://golf-player-activities.trackmangolf.com/api/reports/getreport"

    # Headers
    headers = {
        "authority": "golf-player-activities.trackmangolf.com",
        "method": "POST",
        "path": "/api/reports/getreport",
        "scheme": "https",
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-US,en;q=0.9,en-GB;q=0.8",
        "origin": "https://web-dynamic-reports.trackmangolf.com",
        "priority": "u=1, i",
        "referer": "https://web-dynamic-reports.trackmangolf.com/",
        "sec-ch-ua": '"Not A(Brand)";v="8", "Chromium";v="132", "Microsoft Edge";v="132"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site"
    }

    # JSON payload (body)
    payload = {
        "ReportId": session_id
    }

    # Set the user-agent and other headers
    headers["User-Agent"] = \
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) " + \
        "Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0"

    # Implement retires into report collection
    for retry in range(5):
        try:
            # Send POST request
            response = requests.post(url, json=payload, headers=headers, timeout=10)

            # Check if request was successful
            if response.status_code == 200:

                file_path = \
                    'data/full_session_summary/session-' + \
                    f'{response.json()['StrokeGroups'][0]['Date']}-' + \
                    f'{session_id}.json'

                # Write the list to the JSON file
                with open(file_path, 'w') as json_file:
                    json.dump(response.json(), json_file, indent=5)

                logger.info(f'{response.json()['StrokeGroups'][0]['Date']}-'
                            f'{session_id}.json range data collected')

                return

        except BaseException:
            time.sleep(3 + (2 ** retry))

    logger.error('Failed to collect range session data')


@log_execution
def collect_clubs_used_at_range(
    logger: logging.Logger = None
) -> list:
    '''
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

        session_clubs = [club['Club'] for club in data['StrokeGroups']]
        clubs.extend(session_clubs)

    clubs = list(set(clubs))
    clubs.sort()

    return clubs


@log_execution
def summarise_range_club_data(
    club: str,
    logger: logging.Logger = None
) -> None:

    # Specify the directory path
    directory = "data/full_session_summary/"

    # List all files in the directory
    files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

    range_club_summary = []
    for file_name in files:
        # Read the JSON file
        with open(f'{directory}/{file_name}', 'r') as json_file:
            data = json.load(json_file)

        range_data = [club_data['Strokes'] for club_data in data['StrokeGroups'] if club_data['Club'] == club]
        range_club_summary.extend(range_data)

    # Sort by 'Time' key in descending order (most recent first)
    sorted_data = sorted(range_club_summary[0], key=lambda x: datetime.fromisoformat(x['Time']), reverse=True)

    # Write the list to the JSON file
    with open(f'data/club_summary/{club}.json', 'w') as json_file:
        json.dump(sorted_data, json_file, indent=5)
