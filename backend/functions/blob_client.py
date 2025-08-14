# Install python dependencies
from azure.storage.blob import BlobServiceClient
from typing import (
    Optional,
    Union,
    List
)
import json

# Import project dependencies
from backend.interfaces import AbstractBlobClient
from shared import Variables

class BlobClient(AbstractBlobClient, Variables):
    """
    """
    def __init__(self):
        """
        """
        super().__init__()

    def list_blob_filenames(
        self,
        container_name: str,
        directory_path: Optional[str] = None
    ) -> List[str]:
        """
        List blob filenames in a container, optionally filtered by a directory prefix.

        Args:
            connection_string (str): Azure Blob Storage connection string.
            container_name (str): Name of the container.
            directory_path (Optional[str]): Directory prefix inside the container (e.g. "folder1/subfolder/").
                                        Should end with '/' if used.

        Returns:
            List[str]: List of blob names matching the prefix.
        """
        blob_service_client = BlobServiceClient.from_connection_string(self.blob_account_connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        prefix = directory_path or ""

        blob_names = []
        blobs_list = container_client.list_blobs(name_starts_with=prefix)
        for blob in blobs_list:
            blob_names.append(blob.name)
        return blob_names

    def export_dict_to_blob(
            self,
            data: list,
            container: str,
            output_filename: str) -> None:
        """
        """
        # Convert the data to a JSON string
        json_data = json.dumps(data)

        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(
            self.blob_account_connection_string)

        # Connect to the specific blob in the container
        blob_client = blob_service_client.get_blob_client(
            container=container,
            blob=output_filename
        )

        # Upload the JSON string to Azure Blob Storage
        blob_client.upload_blob(json_data, overwrite=True)

    def read_blob_to_dict(
        self,
        container: str,
        input_filename: str
    ) -> Union[list, dict]:
        """
        Read JSON data from Azure Blob Storage and return as Python object.
        """
        blob_service_client = BlobServiceClient.from_connection_string(
            self.blob_account_connection_string
        )

        blob_client = blob_service_client.get_blob_client(
            container=container,
            blob=input_filename
        )

        # Download blob content as bytes
        download_stream = blob_client.download_blob()
        blob_data = download_stream.readall()

        # Convert bytes to Python object
        return json.loads(blob_data)
