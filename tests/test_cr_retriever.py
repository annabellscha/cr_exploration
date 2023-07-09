import pytest
from typing import List
from src.cr_retriever import CommercialRegisterRetriever

def test_cr_init():
    retriever = CommercialRegisterRetriever()

def test_cr_search_companies():
    retriever = CommercialRegisterRetriever()
    companies = retriever.search("Mueller")
    assert len(companies) > 0
    # assert len(session_id) > 0

def test_cr_download_files():
    session_id: str = None
    documents: List[str] = ["gs", "si"] 
    company: str = 'Tanso'

    # initialize retriever
    retriever = CommercialRegisterRetriever(session_id=session_id)

    # load company data
    try:
        company = retriever.search(company_name=company)[0]
    except Exception as e:
        print(e)
    
    # add documents to cart
    retriever.add_documents_to_cart(company=company, documents=documents)

    # download documents
    retriever.download_documents_from_basket()