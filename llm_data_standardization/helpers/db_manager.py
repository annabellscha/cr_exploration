from datetime import datetime
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
        data = {'link_shareholder_file_2021': full_path}
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
        response = self.supabase.table(table_name).select('link_shareholder_file_2021').eq('startup_id', company_id).execute()
        link = response.data[0].get('link_shareholder_file_2021')
        return link 
    
    def _save_json_to_db(self, json_data: dict, startup_id: int, column_name: str):
        # Define the table name where you want to save the JSON data
        table_name = 'startups'

        # Convert the JSON data to a string if it's not already
        json_string = json.dumps(json_data) if isinstance(json_data, dict) else json_data

        # Create a record or update an existing one with the startup_id and the JSON data
        data = {column_name: json_string}

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
    
    def _check_and_get_azure_json(self, company_id: int):
        table_name = 'startups'
        
        # Fetch the record with the given company_id
        response = self.supabase.table(table_name).select('azure_json_2021').eq('startup_id', company_id).execute()
        return response.data[0]['azure_json_2021']
    
    from supabase import create_client, Client


    def get_company_name_by_id(self, company_id: int) -> str:
        response = self.supabase.table('startups').select('startup_name').eq('startup_id', company_id).execute()
        return response.data[0].get('startup_name')
       

    def save_shareholders_to_db(self, shareholders_json: str, company_id: int):
        company_name = self.get_company_name_by_id(company_id)
        if company_name is None:
            print(f"No company found with company_id {company_id}.")
            return

        # Parse the JSON data
        try:
            # shareholders_data = json.loads(shareholders_json)
            # shareholders = shareholders_data.get('shareholders', [])
            shareholders = shareholders_json
            print(shareholders)
        except json.JSONDecodeError as e:
            print(f"Invalid JSON data provided: {str(e)}")
            return
        # Assuming shareholders is a list of dictionaries
        for shareholder in shareholders:
            shareholder['startup_name'] = company_name
            shareholder['startup_id'] = company_id
            #make sure  that birthdate is in the right format date YYYY-MM-DD
            date_format = "%Y-%m-%d"
            try:
                birthdate = shareholder.get('birthdate')
                print(birthdate)
                if birthdate != None:
                    valid_birthdate = datetime.strptime(birthdate, date_format)
                    print(valid_birthdate)
                    shareholder['birthdate'] = valid_birthdate.strftime(date_format)
            except ValueError:
                print("The birthdate was in the right format")
            #Check format of percentage_of_total_shares
            percentage_of_total_shares = shareholder.get('percentage_of_total_shares')
            try:
                valid_percentage_of_total_shares = float(percentage_of_total_shares)
            except ValueError:
                print("The percentage_of_total_shares is not a number")
                valid_percentage_of_total_shares = 0.0
            print(valid_percentage_of_total_shares)
            shareholder['percentage_of_total_shares'] = valid_percentage_of_total_shares
            # Insert the shareholder data into the shareholder_relations table
            print(shareholder)
            response = self.supabase.table('shareholder_relations_2021').insert(shareholder).execute()
            # Check if the operation was successful
            
            # if response.status_code in range(200, 300):   
        return shareholders
    
    def _write_error_to_db(self, error: str, company_id: int):

        data = {'error': error}
        table_name = 'startups'
        response = self.supabase.table(table_name).update(data).eq('startup_id', company_id).execute()

# Usage example:
# You need to replace 'your_supabase_url' and 'your_supabase_key' with the actual values
# document_manager = DocumentManager('your_supabase_url', 'your_supabase_key')
# document_manager._save_document_link_to_db('/path/to/document.pdf', 123)