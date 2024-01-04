from dotenv import load_dotenv
from datetime import timedelta
import datetime
from typing import List
from cr_extraction.helpers.cr_retriever import CommercialRegisterRetriever
from cr_extraction.main import search_companies, download_files
from google.cloud import storage
import os
import logging
import pytest
from flask import Flask, request

# load env
load_dotenv()

# set logging
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

def test_cr_search_companies():
    retriever = CommercialRegisterRetriever()
    companies = retriever.search("BCN Food Tech GmbH")
    assert len(companies) > 0   

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
    company_name, result = retriever.download_documents_from_basket(bypass_storage=True)

    assert len(result) > 0


def test_cr_find_company_by_hrb():
    retriever = CommercialRegisterRetriever()
    companies = retriever.extended_search(company_id="HRB 269123")
    assert len(companies) > 0
    
