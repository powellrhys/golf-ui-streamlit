import pytest
from unittest.mock import patch, MagicMock
from shared import BlobClient  # adjust import
import json
from azure.core.exceptions import ResourceNotFoundError

# ------------------------------
# Fixtures
# ------------------------------

@pytest.fixture
def blob_client():
    return BlobClient(source="test")


# ------------------------------
# list_blob_filenames tests
# ------------------------------

@patch("shared.functions.blob_client.BlobServiceClient")
def test_list_blob_filenames_no_prefix(mock_blob_service_client, blob_client):
    mock_container_client = MagicMock()

    # Correctly mock blobs with .name attribute
    mock_blob1 = MagicMock()
    mock_blob1.name = "file1.txt"
    mock_blob2 = MagicMock()
    mock_blob2.name = "file2.txt"

    mock_container_client.list_blobs.return_value = [mock_blob1, mock_blob2]
    mock_blob_service_client \
        .from_connection_string.return_value.get_container_client.return_value = mock_container_client

    result = blob_client.list_blob_filenames(container_name="test-container")
    assert result == ["file1.txt", "file2.txt"]
    mock_container_client.list_blobs.assert_called_once_with(name_starts_with="")

@patch("shared.functions.blob_client.BlobServiceClient")
def test_list_blob_filenames_with_prefix(mock_blob_service_client, blob_client):
    mock_container_client = MagicMock()

    mock_blob = MagicMock()
    mock_blob.name = "folder/file1.txt"

    mock_container_client.list_blobs.return_value = [mock_blob]
    mock_blob_service_client \
        .from_connection_string.return_value.get_container_client.return_value = mock_container_client

    result = blob_client.list_blob_filenames(container_name="test-container", directory_path="folder/")
    assert result == ["folder/file1.txt"]
    mock_container_client.list_blobs.assert_called_once_with(name_starts_with="folder/")

# ------------------------------
# export_dict_to_blob tests
# ------------------------------

@patch("shared.functions.blob_client.BlobServiceClient")
def test_export_dict_to_blob(mock_blob_service_client, blob_client):
    mock_blob_client = MagicMock()
    mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

    data = [{"key": "value"}]
    blob_client.export_dict_to_blob(data, container="test-container", output_filename="output.json")

    # Validate upload_blob was called with serialized JSON
    mock_blob_client.upload_blob.assert_called_once_with(json.dumps(data), overwrite=True)

@patch("shared.functions.blob_client.BlobServiceClient")
def test_export_dict_to_blob_invalid_data(mock_blob_service_client, blob_client):
    mock_blob_client = MagicMock()
    mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

    data = {("invalid", "set")}  # set is not JSON serializable
    with pytest.raises(TypeError):
        blob_client.export_dict_to_blob(data, container="test-container", output_filename="output.json")


# ------------------------------
# read_blob_to_dict tests
# ------------------------------

@patch("shared.functions.blob_client.BlobServiceClient")
def test_read_blob_to_dict_valid_json(mock_blob_service_client, blob_client):
    mock_blob_client = MagicMock()
    mock_blob_client.download_blob.return_value.readall.return_value = b'[{"key": "value"}]'
    mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

    result = blob_client.read_blob_to_dict(container="test-container", input_filename="input.json")
    assert result == [{"key": "value"}]

@patch("shared.functions.blob_client.BlobServiceClient")
def test_read_blob_to_dict_invalid_json(mock_blob_service_client, blob_client):
    mock_blob_client = MagicMock()
    mock_blob_client.download_blob.return_value.readall.return_value = b'invalid json'
    mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

    with pytest.raises(json.JSONDecodeError):
        blob_client.read_blob_to_dict(container="test-container", input_filename="input.json")

@patch("shared.functions.blob_client.BlobServiceClient")
def test_read_blob_to_dict_blob_not_found(mock_blob_service_client, blob_client):
    mock_blob_client = MagicMock()
    mock_blob_client.download_blob.side_effect = ResourceNotFoundError("Blob not found")
    mock_blob_service_client.from_connection_string.return_value.get_blob_client.return_value = mock_blob_client

    with pytest.raises(ResourceNotFoundError):
        blob_client.read_blob_to_dict(container="test-container", input_filename="missing.json")
