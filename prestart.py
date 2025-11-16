from azure.storage.blob import BlobServiceClient
from azure.storage.queue import QueueClient
from azure.core.exceptions import ResourceExistsError

def precreate_resources():
    conn_str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
    
    print("Pre-creating Azure Storage resources")
    
    blob_service = BlobServiceClient.from_connection_string(conn_str)
    container_client = blob_service.get_container_client("uploads")
    try:
        container_client.create_container()
        print("Created uploads container")
    except ResourceExistsError:
        print("uploads container already exists")
    
    queue_client = QueueClient.from_connection_string(conn_str, "csv-processing")

    try:
        queue_client.create_queue()
        print("Created csv-processing queue")
    except ResourceExistsError:
        print("csv-processing queue already exists")
    
    internal_queue_name = "azure-webjobs-blobtrigger-mac-1831452541"
    internal_queue_client = QueueClient.from_connection_string(conn_str, internal_queue_name)
    try:
        internal_queue_client.create_queue()
        print(f"Created internal queue '{internal_queue_name}'")
    except ResourceExistsError:
        print(f"Internal queue '{internal_queue_name}' already exists")
    
    print("Resource pre-creation complete")

if __name__ == "__main__":
    precreate_resources()