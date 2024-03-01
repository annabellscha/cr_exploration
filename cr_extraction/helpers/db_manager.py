from supabase import create_client, Client

class DocumentManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def _save_document_link_to_db(self, full_path: str, company_id: int, document_type:str, search_type:str):
        # Define the table name where you want to save the document link
        print("we are in the function now")
        

        # Create a new record or update existing with the company_id and the full_path
        if document_type == "si" & search_type == "startups":
            table_name = 'startups'
            data = {'link_structured_content_file_current': full_path}
            id_column = 'startup_id'
        elif document_type == "si" & search_type == "shareholders":
            table_name = 'shareholders'
            data = {'link_structured_content_file_current': full_path}
            id_column = 'shareholder_id'
        else:
            data = {'link_shareholder_file_2021': full_path}
            table_name = 'startups'
            id_column = 'startup_id'
        print("we now atttemot the update")
        # Insert or update the data into the table
        response = self.supabase.table(table_name).update(data).eq(id_column, company_id).execute()
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
    
    def _get_search_attributes_from_db(self, company_id: int, search_type:str):
        if search_type == "startups":
            table_name = 'startups'
            id_column = 'startup_id'
            columns_to_select = 'register_identification_number, register_mapping, startup_name'
        elif search_type == "shareholders":
            table_name = 'shareholders'
            id_column = 'shareholder_id'
            columns_to_select = 'register_id, register_mapping, shareholder_name'


        # Fetch the required records with the given company_id
        response = self.supabase.table(table_name).select(columns_to_select).eq(id_column, company_id).execute()
        print(response.data[0])
        print("response content above")
        return response.data[0]
    
    def _write_error_to_db(self, error: str, company_id: int, search_type:str):
        if search_type == "startups":
            table_name = 'startups'
            id_column = 'startup_id'
        elif search_type == "shareholders":
            table_name = 'shareholders'
            id_column = 'shareholder_id'
        data = {'error': error}
        
        response = self.supabase.table(table_name).update(data).eq(id_column, company_id).execute()

# Usage example:
# You need to replace 'your_supabase_url' and 'your_supabase_key' with the actual values
# document_manager = DocumentManager('your_supabase_url', 'your_supabase_key')
# document_manager._save_document_link_to_db('/path/to/document.pdf', 123)