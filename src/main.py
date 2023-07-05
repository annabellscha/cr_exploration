
from cr_retriever import CommercialRegisterRetriever

def retrieve_pdf():
    crr = CommercialRegisterRetriever()

    result = crr.retrieve_document("Tanso")

    