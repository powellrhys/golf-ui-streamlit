# Install dependencies
from ..interfaces.blob_client_base import AbstractBlobClient
from azure.storage.blob import BlobServiceClient
from typing import Optional, Union, List
from .variables import Variables
import json

class BlobClient(AbstractBlobClient):
    """
    A client for interacting with Azure Blob Storage.

    This class extends `AbstractBlobClient` and `Variables` to provide
    convenience methods for working with JSON data in Azure Blob Storage.
    It supports listing blobs within a container, exporting Python data
    structures as JSON, and reading JSON blobs back into Python objects.

    Typical usage includes:
    - Enumerating blob filenames in a given container or directory path.
    - Persisting application data (e.g., scorecards, reports) to blob storage.
    - Retrieving stored data for downstream processing.

    Inherits:
        AbstractBlobClient: Base class defining common blob client behavior.
        Variables: Provides configuration variables such as connection strings.

    Attributes:
        blob_account_connection_string (str): Inherited from `Variables`,
            used to authenticate and connect to the Azure Blob account.
    """
    def __init__(self, source: str = "backend"):
        """
        Initialize the BlobClient instance.

        Calls the parent class initializers (`AbstractBlobClient` and `Variables`)
        to ensure that the Azure Blob Storage connection string and other
        required configuration variables are set up before use.
        """
        super().__init__()
        self.vars = Variables(source=source)

    def list_blob_filenames(
        self,
        container_name: str,
        directory_path: Optional[str] = ""
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
        # Create blob service client + container client
        blob_service_client = BlobServiceClient.from_connection_string(self.vars.blob_account_connection_string)
        container_client = blob_service_client.get_container_client(container_name)

        # Collect a list of files in a container
        blob_names = []
        blobs_list = container_client.list_blobs(name_starts_with=directory_path)
        for blob in blobs_list:
            blob_names.append(blob.name)

        return blob_names

    def export_dict_to_blob(
        self,
        data: list,
        container: str,
        output_filename: str
    ) -> None:
        """
        Upload a Python list or dictionary to Azure Blob Storage as a JSON file.

        The method serializes the given data into a JSON string, connects to the
        specified Azure Blob Storage container, and writes the JSON to the given
        blob filename. If the blob already exists, it will be overwritten.

        Args:
            data (list): The Python object (typically a list of dicts) to be serialized and uploaded.
            container (str): Name of the Azure Blob Storage container where the data will be stored.
            output_filename (str): The blob (file) name under which the JSON data will be saved.

        Returns:
            None
        """
        # Convert the data to a JSON string
        json_data = json.dumps(data)

        # Connect to Azure Blob Storage
        blob_service_client = BlobServiceClient.from_connection_string(
            self.vars.blob_account_connection_string)

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
        Download and deserialize JSON data from Azure Blob Storage.

        This method connects to the specified Azure Blob Storage container, retrieves
        the contents of the given blob, and converts the JSON data into a native Python
        object (list or dictionary).

        Args:
            container (str): Name of the Azure Blob Storage container to read from.
            input_filename (str): The name of the blob (JSON file) to retrieve.

        Returns:
            Union[list, dict]: The deserialized JSON content as a Python list or dictionary.

        Raises:
            json.JSONDecodeError: If the blob content cannot be parsed as valid JSON.
            azure.core.exceptions.ResourceNotFoundError: If the specified blob does not exist.
            Exception: For other unexpected errors during retrieval or parsing.
        """
        # Define blob service client
        blob_service_client = BlobServiceClient.from_connection_string(
            self.vars.blob_account_connection_string
        )

        # Define container client
        blob_client = blob_service_client.get_blob_client(
            container=container,
            blob=input_filename
        )

        # Download blob content as bytes
        download_stream = blob_client.download_blob()
        blob_data = download_stream.readall()

        # Convert bytes to Python object
        return json.loads(blob_data)
