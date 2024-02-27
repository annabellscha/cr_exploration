from flask import escape
import openai
import pandas as pd
import tiktoken as tiktok
from datetime import datetime, timedelta
from flask import jsonify, send_file
from google.cloud import storage
from google import auth
import functions_framework

from .helpers.structured_information import StructuredInformation

# Initialize OpenAI client with your API key


@functions_framework.http
def get_structured_content(request):
    request_json = request.get_json(silent=True)
    request_args = request.args
    
    if request_json and 'company_id' in request_json:
        df = request_json['company_id']
    elif request_args and 'company_id' in request_args:
        df = request_args['company_id']
    else:
        return 'No data provided', 400
    
    structurer = StructuredInformation()
    result = structurer.get_shareholder_details_from_si(company_id=df)

    
    # Your existing code to convert the DataFrame to CSV and generate the JSON response
    # ...
    
    # Return the JSON response
    return result

# Remember to exclude your OpenAI API key from the source code before deploying
# Use environment variables to keep your keys secure