# Import dependencies
from shared import Variables, BlobClient
from datetime import datetime
import statistics as stat
import logging

class TrackManAggregator(BlobClient):
    """
    Aggregates and summarizes TrackMan session data from Azure Blob Storage.

    Provides methods to extract clubs used, summarize range data per club,
    and generate yardage book summaries.

    Attributes:
        logger (logging.Logger): Logger for tracking events and errors.
        vars (Variables): Configuration variables.
    """
    def __init__(self, logger: logging.Logger):
        """
        Initialize the TrackManAggregator with a logger and variable configuration.

        Args:
            logger (logging.Logger): Logger instance for logging messages.
        """
        super().__init__()
        self.logger = logger
        self.vars = Variables()

    def collect_clubs_used_at_range(self) -> list:
        """
        Collect a sorted list of unique clubs used across all range sessions.

        Returns:
            list: Alphabetically sorted list of clubs used.
        """
        # Collect a list of files in a blob container
        files = self.list_blob_filenames(container_name="golf", directory_path="trackman_session_summary")

        clubs = []
        for file_name in files:
            # Read the JSON file
            data = self.read_blob_to_dict(container="golf", input_filename=file_name)

            # Collect a list of clubs used in the session
            session_clubs = [club['Club'] for club in data['StrokeGroups']]
            clubs.extend(session_clubs)

        # Sort clubs alphabetically
        clubs = list(set(clubs))
        clubs.sort()

        return clubs

    def summarise_range_club_data(self, club: str) -> None:
        """
        Summarize all range session data for a specific club.

        Filters strokes by the given club and exports the sorted summary to Blob Storage.

        Args:
            club (str): Club name to summarize data for.
        """
        # List all files in the full_session_summary directory
        files = self.list_blob_filenames(container_name="golf", directory_path="trackman_session_summary")

        # Iterate through all sessions and summarise data at a club level
        range_club_summary = []
        for file_name in files:
            # Read the JSON file
            data = self.read_blob_to_dict(container="golf", input_filename=file_name)

            # Filter data based on club being inspected
            range_data = [club_data['Strokes'] for club_data in data['StrokeGroups'] if club_data['Club'] == club]
            range_club_summary.extend(range_data)

        # Sort by 'Time' key in descending order (most recent first)
        sorted_data = sorted(range_club_summary[0], key=lambda x: datetime.fromisoformat(x['Time']), reverse=True)

        # Write the list to the JSON file
        self.export_dict_to_blob(
            data=sorted_data,
            container='golf',
            output_filename=f'trackman_club_summary/{club}.json')

    def collect_yardage_book_data(self, clubs: str) -> None:
        """
        Generate yardage book summaries for multiple clubs using recent shots.

        Aggregates statistics such as average carry, max/min distance, ball speed, launch angle,
        and exports JSON summaries for the latest 10, 20, 30, 40, 50, and 100 shots per club.

        Args:
            clubs (str): List of club names to include in the yardage book summaries.
        """
        # Iterate through clubs and latest x amount of shots
        for shots in [10, 20, 30, 40, 50, 100]:
            yardage_book = []
            for club in clubs:
                # Read the JSON file
                data = self.read_blob_to_dict(container="golf",
                                              input_filename=f"trackman_club_summary/{club}.json")[0:shots]

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
            self.export_dict_to_blob(
                data=yardage_book,
                container='golf',
                output_filename=f'trackman_yardage_summary/latest_{shots}_shot_summary.json')
