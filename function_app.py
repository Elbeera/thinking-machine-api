import azure.functions as func
import logging
import json
import os

from storage_utils import upload_csv_bytes, send_processing_message, download_csv_bytes
from processing_utils import process_csv_bytes, build_grouping_result

app = func.FunctionApp()

@app.route(route="UploadCsv", auth_level=func.AuthLevel.ANONYMOUS)
def UploadCsv(req: func.HttpRequest) -> func.HttpResponse:
    """Azure functions HTTP endpoint that uploads CSV and queues for processing"""
    logging.info("=== HTTP trigger function processed a request. ===")

    try:
        csv_data = req.get_body()
        
        if not csv_data:
            return func.HttpResponse(
                "Please pass CSV data in the request body",
                status_code=400
            )

        container_name, blob_name = upload_csv_bytes(csv_data)
        logging.info(f"Uploaded CSV to blob: {blob_name}")
        
        send_processing_message(container_name, blob_name)
        logging.info(f"Queued for processing: {blob_name}")
        
        return func.HttpResponse(
            json.dumps({
                "status": "queued",
                "message": f"CSV uploaded and queued for processing. Blob: {blob_name}",
                "blob_name": blob_name
            },indent=2),
            status_code=202,
            mimetype="application/json",
            headers={"Content-Type": "application/json"}
        )

    except Exception as error:
        logging.error(f"Error in upload: {error}")
        return func.HttpResponse(
            json.dumps({"Error": f"Upload failed: {error}"}),
            status_code=500,
            mimetype="application/json"
        )

@app.queue_trigger(
    arg_name="msg",
    queue_name="csv-processing",
    connection="AzureWebJobsStorage",
)
def ProcessCsvQueue(msg: func.QueueMessage) -> None:
    """Queue trigger that processes CSV and writes JSON results to file"""
    logging.info("== Queue trigger function triggered. ===")
    
    try:
        message_data = json.loads(msg.get_body().decode('utf-8'))
        container_name = message_data['container']
        blob_name = message_data['blob']
        
        logging.info(f"Processing CSV from blob: {container_name}/{blob_name}")
        
        csv_bytes = download_csv_bytes(container_name, blob_name)
        logging.info("Downloaded CSV from blob storage")
        
        entries = process_csv_bytes(csv_bytes)
        logging.info("Parsed entries from CSV")
        
        if entries:
            result = build_grouping_result(entries)
            logging.info(f"Horizontal groups: {len(result['horizontal_groups'])}")
            logging.info(f"Vertical groups: {len(result['vertical_groups'])}")
            
            output_filename = f"results_{blob_name.replace('.csv', '')}.json"
            output_path = os.path.join(os.path.dirname(__file__), output_filename)
            
            with open(output_path, 'w') as f:
                json.dump(result, f, indent=2)
            
            logging.info(f"JSON results written to: {output_filename}")
            
            logging.info(f"Grouping result: {json.dumps(result, indent=2)}")
        else:
            logging.warning("No valid entries found in CSV")
                
    except Exception as error:
        logging.error(f"Error in queue processing: {error}")
        raise
