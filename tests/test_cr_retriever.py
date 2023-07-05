import pytest
from src.cr_retriever import CommercialRegisterRetriever

def test_cr_init():
    retriever = CommercialRegisterRetriever()

    assert isinstance(retriever.jsession_id, str)
    assert len(retriever.jsession_id) > 0

    assert isinstance(retriever.view_state, str)
    assert len(retriever.view_state) > 0

