from supabase import create_client, Client
import json
class DocumentManager:
    def __init__(self, supabase_url: str, supabase_key: str):
        self.supabase: Client = create_client(supabase_url, supabase_key)

    def _save_document_link_to_db(self, full_path: str, shareholder_id: int):
        # Define the table name where you want to save the document link
        print("we are in the function now")
        table_name = 'shareholders'

        # Create a new record or update existing with the shareholder_id and the full_path
        data = {'link_structured_content_file_current': full_path}
        print("we now atttemot the update")
        # Insert or update the data into the table
        response = self.supabase.table(table_name).update(data).eq('shareholder_id', shareholder_id).execute()
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
    def _get_file_path(self,shareholder_id: int):
        # Define the table name from where you want to retrieve the document link
        table_name = 'shareholders'

        # Select the link_SI_file_current column where shareholder_id matches the shareholder_id
        response = self.supabase.table(table_name).select('link_structured_content_file_current').eq('shareholder_id', shareholder_id).execute()
        link = response.data[0].get('link_structured_content_file_current')
        return link 
    
    def _save_json_to_db(self, json_data: dict, shareholder_id: int, column_name: str):
        # Define the table name where you want to save the JSON data
        table_name = 'shareholders'

        # Convert the JSON data to a string if it's not already
        json_string = json.dumps(json_data) if isinstance(json_data, dict) else json_data

        # Create a record or update an existing one with the shareholder_id and the JSON data
        data = {column_name: json_string}

        # Insert or update the data into the table
        response = self.supabase.table(table_name).update(data).eq('shareholder_id', shareholder_id).execute()

        # Check if the operation was successful
        # if response.status_code in range(200, 300):
        #     print("JSON saved successfully.")
        #     return response.data
        # else:
        #     # Handle any errors that occur during the insert
        #     print(f"Failed to save JSON: {response.error.message if response.error else 'Unknown error'}")
        return 
    
    def _check_and_get_azure_json(self, shareholder_id: int):
        table_name = 'shareholders'
        
        # Fetch the record with the given shareholder_id
        response = self.supabase.table(table_name).select('azure_json_2021').eq('shareholder_id', shareholder_id).execute()
        return response.data[0]['azure_json_2021']
    
    from supabase import create_client, Client


    def get_search_attributes_from_db(self, shareholder_id: int, column_name:str) -> str:
        response = self.supabase.table('shareholders').select('shareholder_name').eq('shareholder_id', shareholder_id).execute()
        return response.data[0].get('shareholder_name')
       

    def save_shareholders_to_db(self, shareholders_json: str, shareholder_id: int):
        company_name = self.get_company_name_by_id(shareholder_id)
        if company_name is None:
            print(f"No company found with shareholder_id {shareholder_id}.")
            return

        # Parse the JSON data
        try:
            shareholders_data = json.loads(shareholders_json)
            shareholders = shareholders_data.get('shareholders', [])
        except json.JSONDecodeError as e:
            print(f"Invalid JSON data provided: {str(e)}")
            return
        # Assuming shareholders is a list of dictionaries
        for shareholder in shareholders:
            shareholder['shareholder_name'] = company_name
            shareholder['shareholder_id'] = shareholder_id
            # Insert the shareholder data into the shareholder_relations table
            response = self.supabase.table('shareholder_relations_2021').insert(shareholder).execute()
    
    def _update_shareholders_in_db(self,shareholders_json: str, shareholder_id: int):
        # Deserialize the JSON string to a dictionary
        shareholders_data = json.loads(shareholders_json)
        print(shareholders_data)
        # Loop through each shareholder
        for shareholder in shareholders_data["shareholders"]:
            print(shareholder)
            # Update the shareholder's information in the 'shareholders' table
            # You would need to have a unique identifier for each shareholder to update the correct row.
            # I'm assuming here that `shareholder_id` is a field in your JSON and in the table.
            
            response = self.supabase.table('shareholders').update(shareholder).eq('shareholder_id', shareholder['shareholder_id']).execute()

            # Check for errors in the response
            # if response.get('error'):
            #     print(f"An error occurred while updating shareholder {shareholder['shareholder_id']}: {response['error']}")

        return "Update completed"        
        

    # Usage example:
    # You need to replace 'your_supabase_url' and 'your_supabase_key' with the actual values
    # document_manager = DocumentManager('your_supabase_url', 'your_supabase_key')
    # document_manager._save_document_link_to_db('/path/to/document.pdf', 123)