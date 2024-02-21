from supabase import create_client, Client

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

# Usage example:
# You need to replace 'your_supabase_url' and 'your_supabase_key' with the actual values
# document_manager = DocumentManager('your_supabase_url', 'your_supabase_key')
# document_manager._save_document_link_to_db('/path/to/document.pdf', 123)