from datetime import datetime
from flask import jsonify
from google.cloud import storage
import functions_framework
from helpers.cr_retriever import CommercialRegisterRetriever

@functions_framework.http
def search_companies(request):
    request_json = request.get_json(silent=True)
    request_args = request.args

    if request_json and 'name' in request_json:
        name = request_json['name']
    elif request_args and 'name' in request_args:
        name = request_args['name']
    else:
        return 'Bad Request: Please provide a company name', 400
    
    retriever = CommercialRegisterRetriever()
    companies = retriever.search(name)

    return jsonify(companies)


@functions_framework.http
def download_files(request):
    request_json = request.get_json(silent=True)

    if request_json and 'company' in request_json and 'documents' in request_json:
        company = request_json['company']
        documents = request_json['documents']
    else:
        return 'Bad Request: Please provide a company name and document types', 400
    

    retriever = CommercialRegisterRetriever()

    try:
        company_data = retriever.search(company_name=company)[0]
    except Exception as e:
        return 'Error: {}'.format(e), 500

    retriever.add_documents_to_cart(company=company_data, documents=documents)
    company, documents = retriever.download_documents_from_basket()

    bucket_name = 'cr_documents'
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    response_object = company
    response_object["document_urls"] = []

    for document in documents:
        blob = bucket.blob(document["url"])
        url = blob.generate_signed_url(
            version="v4",
            # This URL is valid for 15 minutes
            expiration=datetime.timedelta(minutes=30),
            # Allow GET requests using this URL.
            method="GET",
        )

        response_object = company
        response_object["document_urls"].append({"type": document["type"], "url": url})

    return jsonify(response_object)
    

    

