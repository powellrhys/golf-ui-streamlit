# Import dependencies
from shared import Variables, BlobClient
from datetime import datetime
from collections import defaultdict
import logging
import re

class RoundAggregator(BlobClient):
    """
    """
    def __init__(self, logger: logging.Logger):
        """
        """
        super().__init__()
        self.logger = logger
        self.vars = Variables()

    def aggregate_holes_by_course(self) -> None:
        """
        """
        # Define blob directory name
        directory_path = "scorecards"

        # Define hole data map and iterate through each file in blob container
        hole_data_map = defaultdict(list)
        for filename in self.list_blob_filenames(container_name="golf", directory_path=directory_path):

            # Make sure container file is a json file and has the course of interest in the name
            if filename.lower().endswith(".json") and self.vars.golf_course_name.lower() in filename.lower():

                # Extract date from filename using regex
                match = re.search(r"(\d{4}-\d{2}-\d{2})\.json$", filename)
                if not match:
                    self.logger.info(f"Skipping file with unexpected format: {filename}")
                    continue

                # Read file from blob storage
                file_date = match.group(1)
                try:
                    round_data = self.read_blob_to_dict(container="golf", input_filename=filename)

                # Handle exception if file could not be read
                except Exception as e:
                    self.logger.error(f"Error reading {filename}: {e}")
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
