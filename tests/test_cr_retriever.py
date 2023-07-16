from datetime import timedelta
import datetime
from typing import List
from cr_extraction.helpers.cr_retriever import CommercialRegisterRetriever
from google.cloud import storage
import os

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/niklas/Documents/Github/cr-exploration/env/lumpito-cloud-storage.json"

def test_cr_search_companies():
    retriever = CommercialRegisterRetriever()
    companies = retriever.search("BCN Food Tech GmbH", "HRB 272187")
    assert len(companies) > 0
    # assert len(session_id) > 0

def test_cr_download_files():
    session_id: str = None
    documents: List[str] = ["gs", "si"] 
    company_name: str = 'Tacto'

    # initialize retriever
    retriever = CommercialRegisterRetriever(session_id=session_id)

    # load company data
    try:
        company = retriever.search(company_name=company_name)[0]
    except Exception as e:
        print(e)
    
    # add documents to cart
    retriever.add_documents_to_cart(company=company, documents=documents)

    # download documents
    company_name, result = retriever.download_documents_from_basket()

    assert len(result) > 0

def test_main_download_files():
    company = "Forto"
    documents = ["gs", "si"]
    
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

    return response_object
    
def test_new_test():
    retriever = CommercialRegisterRetriever()

    company_id = "HRA 103700"


    results = retriever.search(company_name="Müller")

    if company_id:
        company_data = [x for x in results if x["id"] == company_id][0]
    else:
        company_data = results[0]

    print(company_data)
