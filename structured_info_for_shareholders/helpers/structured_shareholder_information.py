from openai import OpenAI
import os
from .db_manager import DocumentManager

import pandas as pd
import json
from .db_manager import DocumentManager

# Load environment variables from .env file



# endpoint ="https://scraper.cognitiveservices.azure.com/"
# key ="8b2877ef2b52444886bb09e0c5be84e5"



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


  def _get_xml_for_company(self,shareholder_id:int,document_type:str,download:bool):
    documentManager = DocumentManager(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))
    documentManager._get_file_path(shareholder_id)

    gcs_file_path=documentManager._get_file_path(shareholder_id)
  
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




  def get_shareholder_details_from_si(self,shareholder_id:int):
  
    file_content = self._get_xml_for_company(shareholder_id,'si',True)

    root = ET.fromstring(file_content)

    df_shareholder_info = pd.DataFrame(columns=['name','aktenzeichen','total_MDs','gegenstand','vorname', 'nachname', 'geburtsdatum', 'geschlecht'])
    # Define the namespace
    namespaces = {'tns': 'http://www.xjustiz.de'}
    name_json = {}

    # get shareholder name
    documentManager = DocumentManager(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))
    shareholder_name = documentManager.get_search_attributes_from_db(shareholder_id, 'shareholder_name')
    shareholders = {"shareholders": []}
    # Find elements with the given namespace
    people = root.findall('.//tns:beteiligung', namespaces)
    aktenzeichen = root.find(".//{http://www.xjustiz.de}aktenzeichen.absender").text
    total_MDs = len(people)-2
    print(total_MDs)
    # Find and extract the gegenstand element
    gegenstand = root.find('.//tns:basisdatenRegister/tns:gegenstand', {'tns': 'http://www.xjustiz.de'}).text
    
    for beteiligung in root.findall('.//tns:beteiligung', namespaces):
        # Look for natural person within the beteiligung element
        natuerliche_person = beteiligung.find('.//tns:natuerlichePerson', namespaces)
        if natuerliche_person is not None:
            vorname_element = natuerliche_person.find('.//tns:vollerName/tns:vorname', namespaces)
            nachname_element = natuerliche_person.find('.//tns:vollerName/tns:nachname', namespaces)
            geburtsdatum_element = natuerliche_person.find('.//tns:geburt/tns:geburtsdatum', namespaces)
            geschlecht_element = natuerliche_person.find('.//tns:geschlecht', namespaces)

            # Only proceed if all elements are found
            if vorname_element is not None and nachname_element is not None and geburtsdatum_element is not None and geschlecht_element is not None:
                geschlecht_code = geschlecht_element.find('.//code', namespaces)
                gender = 'Male' if geschlecht_code.text == '1' else 'Female' if geschlecht_code.text == '2' else 'Other'
                
                # Construct the shareholder info dictionary
                person_info = {
                    'firstname': vorname_element.text,
                    'lastname': nachname_element.text,
                    'birthdate': geburtsdatum_element.text,
                    'gender': gender
                }
                shareholders["shareholders"].append(person_info)

    # for person in people:
    #     print(person)
    #     person_info = {}
    #     vorname = person.find('.//tns:vorname', namespaces)
    #     print(vorname.text)
    #     nachname = person.find('.//tns:nachname', namespaces)
    #     print(nachname.text)
    #     geburtsdatum = person.find('.//tns:geburtsdatum', namespaces)
    #     print(geburtsdatum.text)
    #     geschlecht_code = person.find('.//tns:geschlecht/code', namespaces)
    #     print(geschlecht_code.text)
        
    #     if all([vorname, nachname, geburtsdatum, geschlecht_code]):
    #         person_info['firstname'] = vorname.text
            
    #         person_info['lastname'] = nachname.text
    #         person_info['birthdate'] = geburtsdatum.text
    #         person_info['gender'] = 'Male' if geschlecht_code.text == '1' else 'Female' if geschlecht_code.text == '2' else 'Other'
    #         person_info['shareholder_name'] = shareholder_name
    #         person_info['list_mds'] = total_MDs
    #         # Add the person to the shareholders list
    #         shareholders["shareholders"].append(person_info)
    #         print(shareholders)
    
    # Serialize the shareholders dictionary to a JSON string
    shareholders_json = json.dumps(shareholders, ensure_ascii=False)

    # for person in people:
        
    #     vorname = person.find('.//tns:vorname', namespaces)
    #     nachname = person.find('.//tns:nachname', namespaces)
    #     geburtsdatum = person.find('.//tns:geburtsdatum', namespaces)
    #     geschlecht_code = person.find('.//tns:geschlecht/code', namespaces)
       
    #     if vorname is not None and nachname is not None and geburtsdatum is not None and geschlecht_code is not None:
    #         vorname = vorname.text
         
    #         nachname = nachname.text
    #         geburtsdatum = geburtsdatum.text
    #         geschlecht = 'Male' if geschlecht_code.text == '1' else 'Female' if geschlecht_code.text == '2' else 'Other'
            
    #         # Print the results
    #         df_temp = {'shareholder_name':shareholder_name,'gender':geschlecht,'shareholder_purpose':gegenstand,'total_MDs':total_MDs,'vorname': vorname, 'nachname': nachname, 'birthdate': geburtsdatum}
    #         df_temp_df = pd.DataFrame([df_temp])
    #         #add df temp to df_shareholder_info
    #         df_shareholder_info = pd.concat([df_shareholder_info,df_temp_df])
            
    #         #Create a liust of all vorname, nachname
    # df_shareholder_info = df_shareholder_info.dropna(axis=1, how='all')       
    # print(df_shareholder_info)
    # #jsonify the df shareholder info while making sure we have unique column names
    # # Check for duplicate column names and rename them if necessary
    # duplicates = df_shareholder_info.columns[df_shareholder_info.columns.duplicated()]
    # print(duplicates)
    # # Create a new DataFrame to avoid modifying the original one while iterating
    # df_unique_cols = df_shareholder_info.copy()
    # for col in duplicates:
    #     df_unique_cols.rename(columns={col: f"{col}_1"}, inplace=True)
    # # Convert the DataFrame to JSON
    # df_shareholder_info = df_shareholder_info.reset_index(drop=True)
    # json_str = df_shareholder_info.to_json(orient='columns')
    # # df_shareholder_info = df_unique_cols.to_json()
    # #drop empty columns
    # print(json_str)
    # #remove column names
    # #add each people df to the table shareholders as a new row
    # for shareholder in json_str:
    #     documentManager._save_json_to_db(shareholder, shareholder_id, column_name='shareholder_details')

    #write the json to the db
    documentManager = DocumentManager(os.environ.get('SUPABASE_URL'), os.environ.get('SUPABASE_KEY'))
    documentManager._update_shareholders_in_db(shareholders_json, shareholder_id)
    
    gegenstand = {'shareholder_purpose':gegenstand}
    
    #write gegenstand only to db
    documentManager._save_json_to_db(gegenstand, shareholder_id, column_name='shareholder_purpose')

    return "yes"
  
