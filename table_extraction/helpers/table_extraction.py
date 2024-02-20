

import os
from dotenv import load_dotenv

from azure.core.credentials import AzureKeyCredential
from azure.ai.formrecognizer import DocumentAnalysisClient
import pandas as pd

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
chunk_size = 2


from google.cloud import storage
import io
import PyPDF2
import pandas as pd

class TableExtractor:
    

    def get_pdf_data(self, gcs_file_path):
        storage_client = storage.Client(project="cr-extraction")
        bucket = storage_client.get_bucket('cr_documents')
        blob = bucket.blob(gcs_file_path)
        pdf_bytes = io.BytesIO(blob.download_as_bytes())

        reader = PyPDF2.PdfReader(pdf_bytes)
        df_list = pd.DataFrame()
        for i in range(0, len(reader.pages), chunk_size):
            writer = PyPDF2.PdfWriter()

            for j in range(i, min(i + chunk_size, len(reader.pages))):
                writer.add_page(reader.pages[j])

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
            print(df_list)
            # Clear the writer for the next chunk of pages
            writer = PyPDF2.PdfWriter()

        return df_list

# Usage
# Assuming you have already authenticated with GCS and have the necessary permissions


def analyze_PDF(buffer):
      poller = document_analysis_client.begin_analyze_document("prebuilt-layout",buffer)
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
