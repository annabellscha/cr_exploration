import pytest
from flask import Flask, request
from cr_extraction.main import search_companies, download_files
import os



@pytest.fixture
def app():
    app = Flask(__name__)
    return app

def test_search_companies(app):
    with app.test_request_context('/?name=Tanso'):
        response = search_companies(request)
        assert response.status_code == 200
        assert 'Tanso' in response.get_data(as_text=True)

def test_download_files(app):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/niklas/Documents/Github/cr-exploration/env/lumpito-cloud-function.json"
    with app.test_request_context('/', json={'company': 'Tanso', 'documents': ['gs']}):
        response = download_files(request)
        assert response.status_code == 200

def test_download_files_single_file_bypass_storage(app):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/niklas/Documents/Github/cr-exploration/env/lumpito-cloud-function.json"
    with app.test_request_context('/', json={'company': 'Tanso', 'documents': ['gs'], 'bypass_storage': True}):
        response = download_files(request)
        assert response.status_code == 200

def test_download_files_multiple_files_bypass_storage(app):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/Users/niklas/Documents/Github/cr-exploration/env/lumpito-cloud-function.json"
    with app.test_request_context('/', json={'company': 'Tanso', 'documents': ['gs', 'si'], 'bypass_storage': True}):
        response = download_files(request)
        assert response.status_code == 200

        