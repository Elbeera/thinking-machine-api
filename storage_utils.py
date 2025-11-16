import os
import json
import logging
from datetime import datetime, timezone

from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient, TextBase64EncodePolicy, TextBase64DecodePolicy
from azure.core.exceptions import ResourceExistsError, ResourceNotFoundError


def get_connection_string() -> str:
    conn = os.getenv("AzureWebJobsStorage")
    if not conn:
        raise RuntimeError("Azure Storage connection string not found in environment variables. ")

    return conn


def get_blob_service_client() -> BlobServiceClient:
    conn_str = get_connection_string()
    return BlobServiceClient.from_connection_string(conn_str)


def ensure_queue_exists(queue_client: QueueClient, queue_name: str) -> None:
    """Ensure the queue exists, create it if it doesn't."""
    try:
        queue_client.get_queue_properties()
        logging.debug(f"Queue '{queue_name}' already exists")
    except ResourceNotFoundError:
        try:
            queue_client.create_queue()
            logging.info(f"Created queue '{queue_name}'")
        except ResourceExistsError:
            logging.debug(f"Queue '{queue_name}' already exists (race condition)")
        except Exception as error:
            logging.warning(f"Unexpected error creating queue '{queue_name}': {error}")
            raise


def upload_csv_bytes(
    data: bytes,
    container_name: str = "uploads",
) -> tuple[str, str]:
    """Uploads raw CSV bytes to Blob Storage and returns (container_name, blob_name)."""

    blob_service = get_blob_service_client()
    container_client = blob_service.get_container_client(container_name)

    try:
        container_client.create_container()
        logging.info(f"Created container '{container_name}'")
    except Exception as error:
        logging.debug(f"create_container for '{container_name}' raised: {error}")

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")
    blob_name = f"upload-{timestamp}.csv"

    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(data, overwrite=False)
    logging.info(f"Uploaded blob '{blob_name}' to container '{container_name}'")

    return container_name, blob_name


def download_csv_bytes(container_name: str, blob_name: str) -> bytes:
    """Downloads CSV bytes from Blob Storage for the given container/blob."""
    blob_service = get_blob_service_client()
    blob_client = blob_service.get_blob_client(container=container_name, blob=blob_name)
    data = blob_client.download_blob().readall()
    return data


def send_processing_message(
    container_name: str,
    blob_name: str,
    queue_name: str = "csv-processing",
) -> None:
    """Sends a JSON message to the given queue with CSV metadata. Uses Base64 encoding which is compatible with Azure Functions."""
    conn_str = get_connection_string()

    queue_client = QueueClient.from_connection_string(
        conn_str, 
        queue_name=queue_name,
        message_encode_policy=TextBase64EncodePolicy(),
        message_decode_policy=TextBase64DecodePolicy()
    )

    ensure_queue_exists(queue_client, queue_name)

    payload = {
        "container": container_name,
        "blob": blob_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    message_text = json.dumps(payload)
    
    try:
        queue_client.send_message(message_text)
        logging.info(f"Sent queue message to '{queue_name}' for blob '{blob_name}'")
    except ResourceNotFoundError:
        logging.warning(f"Queue '{queue_name}' not found, recreating...")
        try:
            queue_client.create_queue()
            queue_client.send_message(message_text)
            logging.info(f"Sent queue message to recreated queue '{queue_name}' for blob '{blob_name}'")
        except Exception as error:
            logging.error(f"Failed to send message after recreating queue '{queue_name}': {error}")
            raise
    except Exception as error:
        logging.error(f"Failed to send message to queue '{queue_name}': {error}")
        raise
