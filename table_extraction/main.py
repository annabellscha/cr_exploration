from flask import escape
import openai
import pandas as pd
import tiktoken as tiktok
from datetime import datetime, timedelta
from flask import jsonify, send_file
from google.cloud import storage
from google import auth
import functions_framework

from .helpers.table_extraction import TableExtractor

# Initialize OpenAI client with your API key
openai.api_key = 'your-api-key'


@functions_framework.http
def extract_table(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    if request_json and 'company_id' in request_json:
        company_id = request_json['company_id']
    elif request_args and 'company_id' in request_args:
        company_id = request_args['company_id']
    else:
        return 'No data provided', 400
    extractor =  TableExtractor()

    result = extractor.get_pdf_data(company_id)

    # Your existing code to convert the DataFrame to CSV and generate the JSON response
    # ...
    
    # Return the JSON response
    return result

# Remember to exclude your OpenAI API key from the source code before deploying
# Use environment variables to keep your keys secure