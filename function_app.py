import azure.functions as func
import datetime
import json
import logging

app = func.FunctionApp()

@app.route(route="UploadCsv", auth_level=func.AuthLevel.ANONYMOUS)
def UploadCsv(req: func.HttpRequest) -> func.HttpResponse:
    logging.info(f'Uploading file: {file_name}')

    file_name = req.params.get('file_name')
    if not file_name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            file_name = req_body.get('file_name')

    if file_name:
        return func.HttpResponse(f"Successfully uploaded {file_name}.", status_code=200)
    else:
        return func.HttpResponse(
             "Failed to upload file. Pass a file_name in the request body.",
             status_code=400
        )