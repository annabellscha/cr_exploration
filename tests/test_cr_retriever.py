import pytest
from src.cr_retriever import CommercialRegisterRetriever

def test_cr_init():
    retriever = CommercialRegisterRetriever(view_state="example_view_state")

    assert isinstance(retriever.get_jsession_id(), str)
    assert len(retriever.get_jsession_id()) > 0

