from azure.storage.queue import QueueClient, TextBase64EncodePolicy, TextBase64DecodePolicy

def clear_poison_queue():
    """Clear the poison queue using direct connection"""
    conn_str = "DefaultEndpointsProtocol=http;AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;"
    poison_queue_name = "csv-processing-poison"
    
    poison_queue_client = QueueClient.from_connection_string(
        conn_str, 
        queue_name=poison_queue_name,
        message_encode_policy=TextBase64EncodePolicy(),
        message_decode_policy=TextBase64DecodePolicy()
    )
    
    try:
        poison_queue_client.delete_queue()
        print("Deleted poison queue successfully")
    except Exception as error:
        print(f"Failed to delete poison queue: {error}")

if __name__ == "__main__":
    clear_poison_queue()