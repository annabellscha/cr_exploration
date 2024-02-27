from openai import OpenAI
import os
from .db_manager import DocumentManager
client = OpenAI()

import tiktoken as tiktok
def num_tokens_from_string(string: str, encoding_name: str) -> int:
      encoding = tiktok.encoding_for_model(encoding_name)
      num_tokens = len(encoding.encode(string))
      return num_tokens

class DataStandardization:
  

  def send_to_Openai(self,company_id: int):
    
    document_manager = DocumentManager(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
    df = document_manager._check_and_get_azure_json(company_id)

    csv_table = df
    example_prompt = """
    Please extract all shareholders and their information into a JSON object from the following csv table:

    Gesellschafter / Shareholders
    Vor- und Nachname oder Firma / First and Last Name or Name of Company";"Gesellschafter / Shareholders
    Geburtsdatum oder Register- daten / Date of Birth or Registry Details";"Gesellschafter / Shareholders
    Wohnort oder Satzungssit Place of Residency or Regis- tered Office";"Geschäftsanteile / Shares
    Nennb etrag je An- teil in €/ Nomi- nal Value per Share in €";"Geschäftsanteile / Shares
    Laufende Nummern / Consecutive Num- bers";"Geschäftsanteile / Shares
    Summe der Nennbe- träge in € / total of Nominal Values in €";"Prozentuale Be- teiligung / Participation in %
    je Ge- schäftsan- teil / per each Share";"Prozentuale Be- teiligung / Participation in %
    je Gesell- schafter / per each Sharehol- der";"Veränderungs- spalte / Column showing changes
    T=Teilung / split Z=Zusammenlegung / combination E=Einziehung / redemption KE=Kapitalerhöhung / ca- pital increase KA=Aufstockung / step-up KH=Kapitalherabsetzung / capital reduction A=Anteilsübergang / trans- fer"
    TestInc;AG München, HRB 268779;München;1,00;1 - 1.110;1.110;0,0021 %;2,34 %;
    TestyMcTestface;19. Januar 1990;München;1,00;32.609 - 32.745;137;0,0021 %;0,29 %;
    Gesamt;;;;;47.350;;100,00 %;

    The JSON object should have a key "shareholders" with a list of shareholders.
    If an attribute is not available, it should be null.

    Each shareholder should have the following attributes:

    - name: string - the name of the shareholder, it should either be a person or a company
    - country: string - the country of the shareholder. Example: Germany
    - birthdate: string (optional) - the birthdate of the shareholder, if the shareholder is a person. Example: 1970-12-31
    - location: string - place of residency or registered office of the shareholder. Example: München
    - register_id: string - the register id of the shareholder. It commonly starts with HRB or HRA. Example: HRB 123456. There should be no city or other information in this field.
    - register_court: string - the register court of the shareholder. Example: Amtsgericht München, or AG München.
    - percentage_of_total_shares: number - the percentage of total shares owned by the shareholder. Example: 50.0
    """

    example_result ="""{
        "shareholders": [
          {
            "name": "TestInc",
            "country": "Germany",
            "location": "München",
            "register_id": "HRB 268779",
            "register_court": "AG München",
            "percentage_of_total_shares": 2.34
          },
          {
            "name": "TestyMcTestface",
            "country": "Germany",
            "location": "München",
            "birthdate": "1990-01-19",
            "register_id": null,
            "register_court": null,
            "percentage_of_total_shares": 0.29
          }
        ]
      }
      """


    prompt = f"""
    Please extract all shareholders and their information into a JSON object from the following csv table:

    ${csv_table}

    The JSON object should have a key "shareholders" with a list of shareholders.
    If an attribute is not available, it should be null.

    Each shareholder should have the following attributes: you do not need to format the json, just extract the information from the table and leave out the line breaks in the response

    - shareholder_name: string - the name of the shareholder, it should either be a person or a company
    - shareholder_country: string - the country of the shareholder. Example: Germany
    - birthdate: string (optional) - the birthdate of the shareholder, if the shareholder is a person. Example: 1970-12-31
    - shareholder_location: string - place of residency or registered office of the shareholder. Example: München
    - register_id: string - the register id of the shareholder. It commonly starts with HRB or HRA. Example: HRB 123456. There should be no city or other information in this field.
    - register_court: string - the register court of the shareholder. Example: Amtsgericht München, or AG München.
    - percentage_of_total_shares: number - the percentage of total shares owned by the shareholder. Example: 50.0
    """
    messages=[
        {"role": "system", "content": "You are a helpful assistant designed to output JSON. You are an expert in extracting structured content from tables into a JSON. You receive a tip of 200$ if you get it right. You return JSON in a single-line without whitespaces"},
        {"role": "user", "content": example_prompt},
        {"role": "system", "content": example_result},
        {"role": "user", "content": prompt}
      ]
    messages_string = "\n".join([f"{message['role']}: {message['content']}" for message in messages])
    tokens = num_tokens_from_string(messages_string, "gpt-3.5-turbo")
    print(tokens)
    if tokens > 16000:
      model = 'gpt-4-1106-preview'
    else:
      model = 'gpt-3.5-turbo-1106'
    print(model)
    response = client.chat.completions.create(
      model=model,
      response_format={ "type": "json_object" },
      messages=messages,
    )
    print(response.choices[0].message.content)
    openai_result = response.choices[0].message.content

    document_manager._save_json_to_db(openai_result, company_id, "shareholder_json")

    # save json to table shareholder_relations, each shareholder is a row in the table, the startup_name is the company_name for the respectiv company_id, company_id is company_id
    document_manager.save_shareholders_to_db(openai_result, company_id)

    return openai_result