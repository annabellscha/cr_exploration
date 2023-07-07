import pytest
from src.cr_retriever import CommercialRegisterRetriever

def test_cr_init():
    retriever = CommercialRegisterRetriever()

def test_cr_search_companies():
    retriever = CommercialRegisterRetriever()
    companies = retriever.search("Mueller")
    assert len(companies) > 0
    # assert len(session_id) > 0

