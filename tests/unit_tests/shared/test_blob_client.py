# Import dependencies
from azure.core.exceptions import ResourceNotFoundError
from unittest.mock import patch, MagicMock
from shared import BlobClient
import streamlit as st
import pytest
import json

@pytest.fixture(autouse=True)
def mock_streamlit_secrets(monkeypatch):
    """
    Replace st.secrets with a fake dictionary.

    This ensures that tests run with controlled
    configuration values instead of real secrets.
    """
    # Fake secrets to mimic Streamlit config
    fake_secrets = {
        "general": {
            "blob_storage_connection_string": "fake-connection-string",
            "golf_course_name": "Fake Course",
            "round_site_player_name": "Fake Player"
        }
    }
    # Patch Streamlit secrets with the fake dictionary
    monkeypatch.setattr(st, "secrets", fake_secrets)


@pytest.fixture
def blob_client():
    """
    Provide a BlobClient instance for testing.

    Uses a test source identifier to avoid
    side effects during execution.
    """
    return BlobClient(source="test")

class TestBlobClient:
    """
    Test suite for BlobClient functionality.

    Covers listing blobs, exporting data, and
    reading data back from blob storage.
    """

    @patch("shared.functions.blob_client.BlobServiceClient")
    def test_list_blob_filenames_no_prefix(self, mock_blob_service_client, blob_client):
        """
        Verify blob listing without a prefix.

        Ensures that all blob filenames are returned
        when no directory path is specified.
        """
        # Mock the container client returned by BlobServiceClient
        mock_container_client = MagicMock()

        # Create fake blob objects with a .name attribute
        mock_blob1 = MagicMock()
        mock_blob1.name = "file1.txt"
        mock_blob2 = MagicMock()
        mock_blob2.name = "file2.txt"

        # Configure list_blobs to return the fake blobs
        mock_container_client.list_blobs.return_value = [mock_blob1, mock_blob2]

        # Patch the connection string to return the mocked container client
        mock_blob_service_client \
            .from_connection_string.return_value.get_container_client.return_value = mock_container_client

        # Call the function under test
        result = blob_client.list_blob_filenames(container_name="test-container")

        # Verify results match expected filenames
        assert result == ["file1.txt", "file2.txt"]

        # Ensure list_blobs was called with the correct prefix
        mock_container_client.list_blobs.assert_called_once_with(name_starts_with="")

    @patch("shared.functions.blob_client.BlobServiceClient")
    def test_list_blob_filenames_with_prefix(self, mock_blob_service_client, blob_client):
        """
        Verify blob listing with a prefix.

        Ensures only blobs under the given folder
        path are included in the results.
        """
        # Mock the container client
        mock_container_client = MagicMock()

        # Create fake blob under a folder
        mock_blob = MagicMock()
        mock_blob.name = "folder/file1.txt"

        # Configure list_blobs to return the fake blob
        mock_container_client.list_blobs.return_value = [mock_blob]

        # Patch to return mocked container client
        mock_blob_service_client \
            .from_connection_string.return_value.get_container_client.return_value = mock_container_client

        # Call the function under test
        result = blob_client.list_blob_filenames(
            container_name="test-container", directory_path="folder/"
        )

        # Verify only the prefixed blob is returned
        assert result == ["folder/file1.txt"]

        # Ensure list_blobs was called with correct prefix
        mock_container_client.list_blobs.assert_called_once_with(name_starts_with="folder/")

    @patch("shared.functions.blob_client.BlobServiceClient")
    def test_export_dict_to_blob(self, mock_blob_service_client, blob_client):
        """
        Verify exporting valid data to blob storage.

        Ensures JSON-serializable input is converted
        and uploaded correctly to the container.
        """
        # Mock the blob client for upload
        mock_blob_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

        # Sample JSON-serializable data
        data = [{"key": "value"}]

        # Call the function under test
        blob_client.export_dict_to_blob(data, container="test-container", output_filename="output.json")

        # Verify that upload_blob was called with correct JSON
        mock_blob_client.upload_blob.assert_called_once_with(json.dumps(data), overwrite=True)

    @patch("shared.functions.blob_client.BlobServiceClient")
    def test_export_dict_to_blob_invalid_data(self, mock_blob_service_client, blob_client):
        """
        Verify error handling for invalid export data.

        Ensures that non-serializable types raise
        a TypeError during JSON conversion.
        """
        # Mock the blob client
        mock_blob_client = MagicMock()
        mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

        # Use invalid data (set is not JSON serializable)
        data = {("invalid", "set")}

        # Expect a TypeError when trying to export
        with pytest.raises(TypeError):
            blob_client.export_dict_to_blob(data, container="test-container", output_filename="output.json")

    @patch("shared.functions.blob_client.BlobServiceClient")
    def test_read_blob_to_dict_valid_json(self, mock_blob_service_client, blob_client):
        """
        Verify reading and parsing valid JSON data.

        Ensures blob contents are deserialized
        into Python objects successfully.
        """
        # Mock the blob client to return JSON bytes
        mock_blob_client = MagicMock()
        mock_blob_client.download_blob.return_value.readall.return_value = b'[{"key": "value"}]'
        mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

        # Call the function under test
        result = blob_client.read_blob_to_dict(container="test-container", input_filename="input.json")

        # Verify JSON is parsed correctly
        assert result == [{"key": "value"}]

    @patch("shared.functions.blob_client.BlobServiceClient")
    def test_read_blob_to_dict_invalid_json(self, mock_blob_service_client, blob_client):
        """
        Verify error handling for invalid JSON.

        Ensures malformed content raises
        a JSONDecodeError exception.
        """
        # Mock the blob client to return invalid JSON
        mock_blob_client = MagicMock()
        mock_blob_client.download_blob.return_value.readall.return_value = b'invalid json'
        mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

        # Expect a JSONDecodeError when parsing invalid data
        with pytest.raises(json.JSONDecodeError):
            blob_client.read_blob_to_dict(container="test-container", input_filename="input.json")

    @patch("shared.functions.blob_client.BlobServiceClient")
    def test_read_blob_to_dict_blob_not_found(self, mock_blob_service_client, blob_client):
        """
        Verify error handling for missing blobs.

        Ensures that attempting to read a non-existent
        blob raises a ResourceNotFoundError.
        """
        # Mock the blob client to raise ResourceNotFoundError
        mock_blob_client = MagicMock()
        mock_blob_client.download_blob.side_effect = ResourceNotFoundError("Blob not found")
        mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

        # Expect ResourceNotFoundError when blob is missing
        with pytest.raises(ResourceNotFoundError):
            blob_client.read_blob_to_dict(container="test-container", input_filename="missing.json")
