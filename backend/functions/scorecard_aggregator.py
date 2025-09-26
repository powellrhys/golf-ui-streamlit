# Import dependencies
from shared import Variables, BlobClient
from collections import defaultdict
from datetime import datetime
import logging
import re

class RoundAggregator(BlobClient):
    """
    Aggregates golf round data from blob storage by hole number and organizes it
    into structured JSON files for easier analysis.

    This class extends the `BlobClient` to interact with Azure Blob Storage,
    reading scorecard files, extracting hole-level information, and exporting
    aggregated summaries for each hole. Data is sorted chronologically (most
    recent first) to support time-series analysis of golf performance.
    """
    def __init__(self, logger: logging.Logger):
        """
        Initialize the RoundAggregator with logging and variable configurations.

        Args:
            logger (logging.Logger): Logger instance for recording aggregation progress and errors.
        """
        super().__init__()
        self.logger = logger
        self.vars = Variables()

    def aggregate_holes_by_course(self) -> None:
        """
        Aggregate hole-level data across scorecards for the configured golf course.

        Reads scorecard JSON files from blob storage, groups hole data by hole number,
        sorts them by date, and writes aggregated summaries back to storage.

        Args: None

        Returns: None

        Raises: Exception: If a scorecard file cannot be read from blob storage.
        """
        # Define hole data map and iterate through each file in blob container
        hole_data_map = defaultdict(list)
        for filename in self.list_blob_filenames(container_name="golf", directory_path="scorecards"):

            # Make sure container file is a json file and has the course of interest in the name
            if filename.lower().endswith(".json") and self.vars.golf_course_name.lower() in filename.lower():

                # Find date in filename
                match = re.search(r"\d{4}-\d{2}-\d{2}", filename)
                if match:
                    file_date = match.group(0)
                else:
                    self.logger.warning("A file was skipped as no valid round date could be found")
                    continue

                self.logger.info(f"Collecting scorecard from the {file_date}...")
                try:
                    round_data = self.read_blob_to_dict(container="golf", input_filename=filename)

                # Handle exception if file could not be read
                except Exception as e:
                    self.logger.error(f"Error reading round data from the {file_date}: {e}")
                    continue

                # Iterate through each hole and append data to hole data map
                for hole in round_data:
                    hole_number = hole.get("hole")
                    if hole_number:
                        hole_with_date = dict(hole)
                        hole_with_date["date"] = file_date
                        hole_data_map[hole_number].append(hole_with_date)

        # Save each hole’s data sorted by date (most recent first)
        for index, (hole_num, hole_list) in enumerate(hole_data_map.items(), start=1):

            # Log progress and sort data by mmost recent datetime
            self.logger.info(f"{index}/{len(hole_data_map)} - Aggregating data for hole {hole_num}")
            sorted_holes = sorted(
                hole_list,
                key=lambda h: datetime.strptime(h["date"], "%Y-%m-%d"),
                reverse=True
            )

            # Export aggregated data to blob
            self.export_dict_to_blob(
                data=sorted_holes,
                container='golf',
                output_filename=f'{self.vars.golf_course_name}_golf_course_hole_summary/hole_{hole_num}.json')

    def summarize_course_strokes(self) -> None:
        """
        Collects stroke data for all 18 holes of the golf course,
        aggregates par and stroke information per hole, and exports
        the summarized results to a course overview JSON file in blob storage.

        Args: None

        Return: None
        """
        # Iterate through each hole summary and collect data
        strokes = []
        for hole in range(1, 19, 1):
            self.logger.info(f"Collecting strokes for hole: {hole}")

            # Define input file name
            input_filename = f"{self.vars.golf_course_name}_golf_course_hole_summary/hole_{hole}.json"

            # Read data from blob
            hole_data = self.read_blob_to_dict(container="golf", input_filename=input_filename)

            # Append data to strokes list
            strokes.append(
                {
                    f"Hole {hole}": {
                        "Par": hole_data[0]["Par"],
                        "Strokes": [stroke["Strokes"] for stroke in hole_data]
                    }
                }
            )

        # Export aggregated data to blob
        self.export_dict_to_blob(
            data=strokes,
            container='golf',
            output_filename=f'{self.vars.golf_course_name}_golf_course_hole_summary/course_overview.json')
