

import os
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import pandas as pd

from .db_manager import DocumentManager

# Load environment variables from .env file
load_dotenv()

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



from google.cloud import storage
import io
import PyPDF2
import pandas as pd

class TableExtractor:
    
    def _rename_duplicate_columns(self,df):
        cols = pd.Series(df.columns)
        for dup in cols[cols.duplicated()].unique():
            cols[cols[cols == dup].index] = [f'{dup}_{i}' if i != 0 else dup for i in range(sum(cols == dup))]
        df.columns = cols
        return df

    def get_pdf_data(self, company_id):
        document_manager = DocumentManager(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
        #check in DB if we have a json extracted already -> azure_json = null
        #if not, extract the json and save it to DB
        #if yes, return the json
        result =document_manager.check_and_get_azure_json(company_id)
        print(result)
        if result is None:
            gcs_file_path=document_manager._get_file_path(company_id)


            storage_client = storage.Client(project="cr-extraction")
            bucket = storage_client.get_bucket('cr_documents')
            print(gcs_file_path)
            #try to download file from GCS, in case it fails change the path ending to .pdf
            try:
                blob = bucket.blob(gcs_file_path)
                print(gcs_file_path)
                pdf_bytes = io.BytesIO(blob.download_as_bytes())
                print(pdf_bytes)
            except:
                print(gcs_file_path)
                if gcs_file_path.endswith('.tif'):
                    gcs_file_path = gcs_file_path.replace('.tif',".pdf")
                    blob = bucket.blob(gcs_file_path)
                    pdf_bytes = io.BytesIO(blob.download_as_bytes())
                elif gcs_file_path.endswith('.tiff'):
                    gcs_file_path = gcs_file_path.replace('.tiff',".pdf")
                    blob = bucket.blob(gcs_file_path)
                    pdf_bytes = io.BytesIO(blob.download_as_bytes())
                
                print(gcs_file_path)
            
            print(pdf_bytes)
            writer = PyPDF2.PdfWriter()
            try:
                reader = PyPDF2.PdfReader(pdf_bytes)
                for i in range(len(reader.pages)):
                    try:
                        page = reader.pages[i]
                        writer.add_page(page)
                    except Exception as e:
                        print(f"Failed to read page {i}: {e}")
            except Exception as general_error:
                print(f"Failed to open PDF: {general_error}")
            # reader = PyPDF2.PdfReader(pdf_bytes)
            df_list = pd.DataFrame()
           
            # writer = PyPDF2.PdfWriter()

                # Add all pages to the writer
            # print(reader.pages)
            # for page in reader.pages:
            #     writer.add_page(page)

                # Create a file-like object to hold the PDF data
            pdf_chunk_bytes = io.BytesIO()
            writer.write(pdf_chunk_bytes)
            pdf_chunk_bytes.seek(0)

                # Now `pdf_chunk_bytes` is a file-like object containing the PDF data.
                # This can be sent to an API as follows:
            response = analyze_PDF(pdf_chunk_bytes)

            table = get_table_data(response)
                # Check the response
                # df_list = df_list.append(table)
            df_list = pd.concat([df_list, table], ignore_index=True)

            #check if two columna are the same
            #if yes, rename one of them to _1
            #if no, append the column to the df_list
           # Check for duplicate column names and rename them if necessary
            duplicates = df_list.columns[df_list.columns.duplicated()]
            # Create a new DataFrame to avoid modifying the original one while iterating
            df_unique_cols = self._rename_duplicate_columns(df_list)
            # Convert the DataFrame to JSON
            result = df_unique_cols.to_json()
            #write json to
            #Write result json to DB
            document_manager._save_json_to_db(result, startup_id=company_id)


        return result

# Usage
# Assuming you have already authenticated with GCS and have the necessary permissions


def analyze_PDF(buffer):
      poller = document_analysis_client.begin_analyze_document("prebuilt-layout", buffer)
      result = poller.result()
      return result


def get_table_data(result):
      rows = []

      # get header row
      header_row = {}
      try:
          for cell in result.tables[0].cells:
              if(cell.kind != "columnHeader"):
                  continue

              # if row index is 0, add cell content to header row
              if cell.row_index == 0:
                  for i in range(cell.column_index, cell.column_index + cell.column_span):
                      header_row[i] = cell.content
                  
              # if row index is larger than 0, append cell content to existing header row for the correct column
              elif cell.row_index > 0:
                  for i in range(cell.column_index, cell.column_index + cell.column_span):
                      header_row[i] += "\n" + cell.content
      except:
          pass

      # append header row to rows list
      rows.append(header_row)

      # get table content
      for table_idx, table in enumerate(result.tables):
          
          row = {}
          row_index = 0
      
          try:
              for cell in table.cells:
                  # skip the first header row of the first table
                  if table_idx == 0 and cell.kind == "columnHeader":
                      continue

                  # append constructed row if previous row is complete
                  if cell.row_index > row_index:
                      if row != {}:
                          rows.append(row)
                      row = {}
                      row_index = cell.row_index
              

                  # add cell to row - if cell spans multiple columns, add the cell content to every column
                  for i in range(cell.column_index, cell.column_index + cell.column_span):
                      # row[i] = { header_row[i]: cell.content }
                      row[i] = cell.content
          except:
              pass
          rows.append(row)

      # convert list of dicts to dataframe
      df = pd.DataFrame(rows[1:])
      df.columns = rows[0].values()
      return df
