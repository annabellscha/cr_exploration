from openai import OpenAI
import os
from .db_manager import DocumentManager


from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import pandas as pd

from .db_manager import DocumentManager

# Load environment variables from .env file


# Access the environment variables
endpoint = os.getenv("FORM_RECOGNIZER_ENDPOINT")
key = os.getenv("FORM_RECOGNIZER_KEY")
# endpoint ="https://scraper.cognitiveservices.azure.com/"
# key ="8b2877ef2b52444886bb09e0c5be84e5"

print(key)
print(endpoint)
# iniitalize the client
document_analysis_client = DocumentAnalysisClient(
    endpoint=endpoint, credential=AzureKeyCredential(key)
)



# def open_file(file_path):
#     #open pdf from file path
#     with open(file_path, "rb") as f:
#         buffer = f.read()
#     return buffer
import PyPDF2
import io
chunk_size = 2


from google.cloud import storage
import io
import PyPDF2
import pandas as pd
import xml.etree.ElementTree as ET
import chardet

class StructuredInformation:


  def _get_xml_for_company(self,company_id:int,document_type:str,download:bool):
    documentManager = DocumentManager(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))
    documentManager._get_file_path(company_id)

    gcs_file_path=documentManager._get_file_path(company_id)
  
    storage_client = storage.Client(project="cr-extraction")
    bucket = storage_client.bucket('cr_documents')
    blob = bucket.blob(gcs_file_path)
    
    # Download the blob to an in-memory file-like object
    bytes_buffer = io.BytesIO()
    blob.download_to_file(bytes_buffer)
    bytes_buffer.seek(0)  # Rewind the buffer to the beginning
    print(bytes_buffer)
    encodings = ['utf-8', 'iso-8859-1', 'windows-1252', 'utf-16']
    true_encoding=None
    for enc in encodings:
        try:
            content = bytes_buffer.getvalue().decode(enc)
            print(f"Decoded with encoding: {enc}")
            true_encoding = enc
            break
        except UnicodeDecodeError:
            continue
    else:
        print("Failed to detect encoding.")
        content = None  # or handle the undecodable data as you see fit

    xml_string = bytes_buffer.getvalue().decode(true_encoding)
    print(xml_string)
    return xml_string




  def get_shareholder_details_from_si(self,company_id:int):
  
    file_content = self._get_xml_for_company(company_id,'si',True)

    root = ET.fromstring(file_content)

    df_shareholder_info = pd.DataFrame(columns=['name','aktenzeichen','total_MDs','gegenstand','vorname', 'nachname', 'geburtsdatum', 'geschlecht'])
    # Define the namespace
    namespaces = {'tns': 'http://www.xjustiz.de'}
    name_json = {}

    # Find elements with the given namespace
    people = root.findall('.//tns:beteiligung', namespaces)
    aktenzeichen = root.find(".//{http://www.xjustiz.de}aktenzeichen.absender").text
    total_MDs = len(people)-2
    # Find and extract the gegenstand element
    gegenstand = root.find('.//tns:basisdatenRegister/tns:gegenstand', {'tns': 'http://www.xjustiz.de'}).text
    for person in people:
        
        vorname = person.find('.//tns:vorname', namespaces)
        nachname = person.find('.//tns:nachname', namespaces)
        geburtsdatum = person.find('.//tns:geburtsdatum', namespaces)
        geschlecht_code = person.find('.//tns:geschlecht/code', namespaces)
       
        if vorname is not None and nachname is not None and geburtsdatum is not None and geschlecht_code is not None:
            vorname = vorname.text
         
            nachname = nachname.text
            geburtsdatum = geburtsdatum.text
            geschlecht = 'Male' if geschlecht_code.text == '1' else 'Female' if geschlecht_code.text == '2' else 'Other'
            
            # Print the results
            df_temp = {'name':company_id,'aktenzeichen':aktenzeichen,'gegenstand':gegenstand,'total_MDs':total_MDs,'vorname': vorname, 'nachname': nachname, 'geburtsdatum': geburtsdatum, 'geschlecht': geschlecht}
            df_temp_df = pd.DataFrame([df_temp])
            #add df temp to df_shareholder_info
            df_shareholder_info = pd.concat([df_shareholder_info,df_temp_df])
            
            #Create a liust of all vorname, nachname
            name_json.append(vorname + ' ' + nachname)
          
    #jsonify the df shareholder info
    df_shareholder_info = df_shareholder_info.to_json()
    #write the json to the db
    documentManager = DocumentManager(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))
    documentManager._save_json_to_db(df_shareholder_info, company_id, column_name='list_mds')


    return df_shareholder_info
  
