import pytest
from typing import List
from cr_extraction.helpers.cr_retriever import CommercialRegisterRetriever
from cr_extraction.helpers.gcp import upload_blob
from google.cloud import storage
import os
import requests

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/niklas/Documents/Github/cr-exploration/env/lumpito-cloud-storage.json"

def test_cr_search_companies():
    retriever = CommercialRegisterRetriever()
    companies = retriever.search("Mueller")
    assert len(companies) > 0
    # assert len(session_id) > 0

def test_cr_download_files():
    session_id: str = None
    documents: List[str] = ["gs", "si"] 
    company_name: str = 'Tanso'

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
    result = retriever.download_documents_from_basket()

    assert len(result) > 0

def test_upload_blob_original():
    cr_retriever = CommercialRegisterRetriever()
    storage_client = storage.Client(project="cr-extraction")

    cr_retriever._upload_file_to_gcp(storage_client=storage_client, response=requests.Response(), full_path="test/GS-Liste-Tanso Technologies GmbH-26.04.2023.pdf")


def test_upload_blob():
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/niklas/Documents/Github/cr-exploration/env/lumpito-cloud-storage.json"
    storage_client = storage.Client(project="cr-extraction")
    bucket_name = "cr_documents"
    bucket = storage_client.get_bucket(bucket_name)
    blob = bucket.blob("test.pdf")
    blob.upload_from_filename("/Users/niklas/Documents/Github/cr-exploration/out/Tanso Technologies GmbH/GS-Liste-Tanso Technologies GmbH-26.04.2023.pdf")
