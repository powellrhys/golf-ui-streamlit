# Import dependencies
from typing import List, Union, Optional
from abc import ABC, abstractmethod

class AbstractBlobClient(ABC):
    """
    Abstract base class defining the interface for interacting with blob storage backends.

    Subclasses must implement methods for listing blobs, uploading JSON data,
    and reading JSON data from the storage backend.
    """
    @abstractmethod
    def list_blob_filenames(self, container_name: str, directory_path: Optional[str] = None) -> List[str]:
        """
        List the names of blobs in a given container, optionally filtered by directory prefix.

        Args:
            container_name (str): The name of the container.
            directory_path (Optional[str]): Prefix filter for blob names (e.g., "folder/").

        Returns:
            List[str]: A list of blob filenames matching the prefix.
        """
        pass

    @abstractmethod
    def export_dict_to_blob(self, data: list, container: str, output_filename: str) -> None:
        """
        Uploads a list (or dict) as a JSON blob to the specified container.

        Args:
            data (list): The data to serialize and upload.
            container (str): The target container name.
            output_filename (str): The name of the output blob.
        """
        pass

    @abstractmethod
    def read_blob_to_dict(self, container: str, input_filename: str) -> Union[list, dict]:
        """
        Downloads a blob and parses its content as JSON into a Python object.

        Args:
            container (str): The container name.
            input_filename (str): The name of the blob to read.

        Returns:
            Union[list, dict]: The deserialized JSON object from the blob.
        """
        pass
