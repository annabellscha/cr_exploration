from datetime import datetime, timedelta
from flask import jsonify, send_file
from google.cloud import storage
from google import auth
import functions_framework
from .helpers.cr_retriever import CommercialRegisterRetriever
import zipfile
import io
import os
import magic
from dotenv import load_dotenv



@functions_framework.http
def search_companies(request):
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and "name" in request_json:
        name = request_json["name"]
    elif request_args and "name" in request_args:
        name = request_args["name"]
    else:
        return "Bad Request: Please provide a company name", 400

    retriever = CommercialRegisterRetriever()
    companies = retriever.search(name)

    return jsonify(companies)


@functions_framework.http
def search_companies_by_id(request):
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and "name" in request_json:
        name = request_json["name"]
    elif request_args and "name" in request_args:
        name = request_args["name"]
    else:
        return "Bad Request: Please provide a company name", 400

    retriever = CommercialRegisterRetriever()
    companies = retriever.search(name)

    return jsonify(companies)


@functions_framework.http
def download_files(request):
    load_dotenv()
    credentials, _ = auth.default()
    if os.environ.get("ENV") == "prod":
        credentials.refresh(auth.transport.requests.Request())

    request_json = request.get_json(silent=True)

    # if request_json and "company_name" in request_json and "documents" in request_json and "company_id" in request_json and "register_number" in request_json and "register_mapping" in request_json:
    #     company_name = request_json["company_name"]
    #     documents = request_json["documents"]
    #     company_id = request_json["company_id"]
    #     register_number= request_json["register_number"]
    #     register_mapping = request_json["register_mapping"]
    # else:
    #     return "Bad Request: Please provide a company name and document types", 400
    if request_json and "company_id" in request_json and "documents" in request_json:
        company_id = request_json["company_id"]
        documents = request_json["documents"]
    else:
        return "Bad Request: Please provide a company name and document types", 400

    # company_id = None
    # if request_json and "company_id" in request_json:
    #     # company_id = request_json["company_id"]

    bypass_storage = False
    if request_json and "bypass_storage" in request_json:
        bypass_storage = request_json["bypass_storage"]

    retriever = CommercialRegisterRetriever()

    # try:
    # results = retriever.search(company_name=company)
    # print(results)

    results = retriever.extended_search(company_id=company_id, search_type="startups")

    if results == "normal search":
        print(results)
        retriever = CommercialRegisterRetriever()
        results = retriever.search(company_id=company_id, search_type="startups")
        print(results)
    # if company_id:
    #     company_data = [x for x in results if x["id"] == company_id][0]
    # else:
    company_data = results
    
    # except Exception as e:
    #     return 'Error: {}'.format(e), 500
    retriever.add_documents_to_cart(company=company_data, documents=documents, company_id=company_id)
    company, documents = retriever.download_documents_from_basket(
        bypass_storage=bypass_storage, company_id = company_id, search_type="startups"
    )

    response_object = company
    response_object["document_urls"] = []

    if bypass_storage:
        if len(documents) == 0:
            return "No documents found", 404
        elif len(documents) == 1:
            # Create a BytesIO object from the binary content
            buffer = io.BytesIO(documents[0]["document_binary"])
            mime_type = magic.from_buffer(buffer.read(1024), mime=True)

            if buffer.getbuffer().nbytes == 0:
                print("Warning: Buffer is empty")

            # Reset the buffer's position to the start
            buffer.seek(0)

            # Send the buffer using send_file
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f'{company["name"]}_{company["court"]}.{mime_type.split("/")[1]}',
                mimetype=mime_type,
            )

        else:
           return "You can only bypass storage for a single document", 400

    else:
        bucket_name = "cr_documents"
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        for document in documents:
            blob = bucket.blob(document["url"])
            print(blob)
            url = blob.generate_signed_url(
                version="v4",
                # This URL is valid for 15 minutes
                expiration=timedelta(minutes=30),
                service_account_email=credentials.service_account_email,
                access_token=credentials.token,
                # Allow GET requests using this URL.
                method="GET",
            )

            response_object = company
            response_object["document_urls"].append(
                {"type": document["type"], "url": url}
            )

    return jsonify(response_object)



@functions_framework.http
def get_shareholder_structured_info(request):
#     credentials, _ = auth.default()
    load_dotenv()
    credentials, _ = auth.default()
    if os.environ.get("ENV") == "prod":
        credentials.refresh(auth.transport.requests.Request())

    request_json = request.get_json(silent=True)
    if request_json and "shareholder_id" in request_json:
        shareholder_id = request_json["shareholder_id"]
        documents = request_json["documents"]
        
    else:
        return "Bad Request: Please provide a shareholder id", 400
    
    retriever = CommercialRegisterRetriever()

    results = retriever.extended_search(company_id=shareholder_id, search_type="shareholders")

    bypass_storage = False
    if request_json and "bypass_storage" in request_json:
        bypass_storage = request_json["bypass_storage"]
    # if company_id:
    #     company_data = [x for x in results if x["id"] == company_id][0]
    # else:
    company_data = results
    
    # except Exception as e:
    #     return 'Error: {}'.format(e), 500
    retriever.add_documents_to_cart(company=company_data, documents=documents, company_id=shareholder_id)
    company, documents = retriever.download_documents_from_basket(
        bypass_storage=bypass_storage, company_id = shareholder_id, search_type="shareholders"
    )

    response_object = company
    response_object["document_urls"] = []

    if bypass_storage:
        if len(documents) == 0:
            return "No documents found", 404
        elif len(documents) == 1:
            # Create a BytesIO object from the binary content
            buffer = io.BytesIO(documents[0]["document_binary"])
            mime_type = magic.from_buffer(buffer.read(1024), mime=True)

            if buffer.getbuffer().nbytes == 0:
                print("Warning: Buffer is empty")

            # Reset the buffer's position to the start
            buffer.seek(0)

            # Send the buffer using send_file
            return send_file(
                buffer,
                as_attachment=True,
                download_name=f'{company["name"]}_{company["court"]}.{mime_type.split("/")[1]}',
                mimetype=mime_type,
            )

        else:
           return "You can only bypass storage for a single document", 400

    else:
        bucket_name = "cr_documents"
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)

        for document in documents:
            blob = bucket.blob(document["url"])
            print(blob)
            url = blob.generate_signed_url(
                version="v4",
                # This URL is valid for 15 minutes
                expiration=timedelta(minutes=30),
                service_account_email=credentials.service_account_email,
                access_token=credentials.token,
                # Allow GET requests using this URL.
                method="GET",
            )

            response_object = company
            response_object["document_urls"].append(
                {"type": document["type"], "url": url}
            )

    return jsonify(response_object)

#     request_json = request.get_json(silent=True)

#     if request_json and 'company' in request_json and 'documents' in request_json:
#         company = request_json['company']
#         documents = request_json['documents']
#     else:
#         return 'Bad Request: Please provide a company name and document types', 400

#     if(len(documents) > 1):
#         return 'Bad Request: Please provide a single document type', 400

#     company_id = None
#     if request_json and 'company_id' in request_json:
#         company_id = request_json['company_id']

#     retriever = CommercialRegisterRetriever()

#     # try:
#     results = retriever.search(company_name=company)
#     print(results)

#     if company_id:
#         company_data = [x for x in results if x["id"] == company_id][0]
#     else:
#         company_data = results[0]


#     # except Exception as e:
#     #     return 'Error: {}'.format(e), 500

#     retriever.add_documents_to_cart(company=company_data, documents=documents)
#     company, documents = retriever.download_documents_from_basket()

#     bucket_name = 'cr_documents'
#     storage_client = storage.Client()
#     bucket = storage_client.bucket(bucket_name)

#     response_object = company
#     response_object["document_urls"] = []

#     for document in documents:
#         blob = bucket.blob(document["url"])
#         url = blob.generate_signed_url(
#             version="v4",
#             # This URL is valid for 15 minutes
#             expiration=timedelta(minutes=30),\
#             service_account_email=credentials.service_account_email,
#             access_token=credentials.token,
#             # Allow GET requests using this URL.
#             method="GET",
#         )

#         response_object = company
#         response_object["document_urls"].append({"type": document["type"], "url": url})

#     return jsonify(response_object)
