from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium import webdriver
from datetime import datetime
import requests
import json
import os


def configure_driver(
    driver_path: str = 'chromedriver.exe',
    headless: bool = False
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


def login_to_trackman(
    driver: WebDriver,
    email: str,
    password: str
) -> WebDriver:
    '''
    '''
    while True:
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
            driver.execute_script("signinBtnClicked()")

            break

        except:
            driver.close()

    return driver


def collect_trackman_access_token(
    driver: WebDriver
) -> str:
    '''
    '''
    driver.get("https://portal.trackmangolf.com/api/account/me")

    # Locate the <body> tag and get its inner HTML (content inside the body tag)
    body_content = driver.find_element("tag name", "pre").get_attribute("innerHTML")

    # Parse the JSON string
    try:
        json_data = json.loads(body_content)
        return json_data['accessToken']

    except json.JSONDecodeError:
        print("Error: The content is not valid JSON.")


def collect_range_session_ids(
    access_token: str
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

    # Make the POST request
    response = requests.post(url, json=body, headers=headers)

    # Check for a successful response
    if response.status_code == 200:
        data = response.json()['data']['me']['activities']['items']
        return [activitiy['reportLink'].split('ReportId=')[-1] for activitiy in data]

        # print("Response data:", response.json()['data']['activities']['items'])
    else:
        print(f"Failed to fetch data. Status code: {response.status_code}")
        print("Response:", response.text)


def collect_range_session_data(
    session_id: str
) -> None:
    '''
    '''
    # URL and API endpoint
    url = "https://golf-player-activities.trackmangolf.com/api/reports/getreport"

    # Headers
    headers = {}

    # JSON payload (body)
    payload = {
        "ReportId": session_id
    }

    # Set the user-agent and other headers
    headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/132.0.0.0 Safari/537.36 Edg/132.0.0.0"

    # Send POST request
    response = requests.post(url, json=payload, headers=headers)

    # Check if request was successful
    if response.status_code == 200:

        file_path = f'data/full_session_summary/session-{response.json()['StrokeGroups'][0]['Date']}.json'

        print(file_path)

        # Write the list to the JSON file
        with open(file_path, 'w') as json_file:
            json.dump(response.json(), json_file, indent=5)


def collect_clubs_used_at_range() -> list:
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


def summarise_range_club_data(club: str) -> None:

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