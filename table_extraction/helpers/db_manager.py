from supabase import create_client, Client
import json
class DocumentManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def _save_document_link_to_db(self, full_path: str, company_id: int):
        # Define the table name where you want to save the document link
        print("we are in the function now")
        table_name = 'startups'

        # Create a new record or update existing with the company_id and the full_path
        data = {'link_SI_file_current': full_path}
        print("we now atttemot the update")
        # Insert or update the data into the table
        response = self.supabase.table(table_name).update(data).eq('startup_id', company_id).execute()
        return
        # # Check if the operation was successful
        # if response.get('status_code') in range(200, 300):
        #     print("Document link saved successfully.")
        #     return response.data
        # else:
        #     # Handle any errors that occur during the insert
        #     error_message = response.get('error', {}).get('message', 'Unknown error')
        #     print(f"Failed to save document link: {error_message}")
        #     return None
    def _get_file_path(self,company_id: int):
        # Define the table name from where you want to retrieve the document link
        table_name = 'startups'

        # Select the link_SI_file_current column where startup_id matches the company_id
        response = self.supabase.table(table_name).select('link_SI_file_current').eq('startup_id', company_id).execute()
        link = response.data[0].get('link_SI_file_current')
        return link 
    
    def _save_json_to_db(self, json_data: dict, startup_id: int):
        # Define the table name where you want to save the JSON data
        table_name = 'startups'

        # Convert the JSON data to a string if it's not already
        json_string = json.dumps(json_data) if isinstance(json_data, dict) else json_data

        # Create a record or update an existing one with the startup_id and the JSON data
        data = {'azure_json': json_string}

        # Insert or update the data into the table
        response = self.supabase.table(table_name).update(data).eq('startup_id', startup_id).execute()

        # Check if the operation was successful
        # if response.status_code in range(200, 300):
        #     print("JSON saved successfully.")
        #     return response.data
        # else:
        #     # Handle any errors that occur during the insert
        #     print(f"Failed to save JSON: {response.error.message if response.error else 'Unknown error'}")
        return None
    
    def check_and_get_azure_json(self, company_id: int):
        table_name = 'startups'
        
        # Fetch the record with the given company_id
        response = self.supabase.table(table_name).select('azure_json').eq('startup_id', company_id).execute()
        return response.data

# Usage example:
# You need to replace 'your_supabase_url' and 'your_supabase_key' with the actual values
# document_manager = DocumentManager('your_supabase_url', 'your_supabase_key')
# document_manager._save_document_link_to_db('/path/to/document.pdf', 123)