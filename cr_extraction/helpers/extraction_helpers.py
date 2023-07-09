
from bs4 import BeautifulSoup
import re
from typing import Tuple
from datetime import datetime
import urllib.parse

def get_view_state(raw_text: str) -> str:
    soup = BeautifulSoup(raw_text, 'html.parser')

    view_state_input = soup.find('input', {'name': 'javax.faces.ViewState'})
    view_state_value = view_state_input['value']
    return view_state_value


def get_session_id(raw_text: str) -> str:
    regex = r'jsessionid=([a-zA-Z0-9]+\.[a-zA-Z0-9]+-1)\b'

    match = re.search(regex, raw_text)
    if match:
        jsessionid = match.group(1)
        return jsessionid
    return


def get_company_name_id(raw_text: str) -> Tuple[str, str]:
    soup = BeautifulSoup(raw_text, "html.parser")

    # Extract company name
    company_name = soup.find("div", class_="company_result").find("b").get_text(strip=True)
    company_link = soup.find("a", string="Registerinformationen des Registergerichts")["href"]

    # Use regex to find company number
    company_number = re.search(r'company=(\d+)', company_link)
    company_id = company_number.group(1)  # Group 1 contains the first set of parentheses matches

    return company_name, company_id


def identify_dk_links(raw_text:str, level: int = 0):
    soup = BeautifulSoup(raw_text, 'html.parser')

    if level == 0:
        for a in soup.find_all('a'):
            i = a.find('i', title="Öffnet diesen Baum des Dokumentenbaums")
            link = a['href']
    elif level == 1:
        tag_a = soup.find('a', string="Liste der Gesellschafter")
        link = tag_a['href']
        
    return link

def create_payload_for_document_selection(raw_text: str) -> str:
    soup = BeautifulSoup(raw_text, 'html.parser')
    tag_td = soup.find('td', class_='submit-container')

    inputs = {}

    # Find all 'input' tags and store their 'id' and 'value' as key-value pairs in the dictionary
    for input_tag in soup.find_all('input'):
        inputs[input_tag.get('id')] = input_tag.get('value')

    # submitaction = inputs.get('submitaction')
    keys = ['ausdruckart', 'cname', 'docnames', 'format', 'gkz', 'gkzalt', 'hasChildren', 'iddok', 'location', 'rnr', 'rtype', 'searchIdx', 'state', 'submitaction']

    # create payload
    payload = {key: value for key, value in inputs.items() if value is not None and key in keys}
    payload = urllib.parse.urlencode(payload)
    
    return payload

def get_latest_document_link(raw_text: str) -> Tuple[str, str]:
    soup = BeautifulSoup(raw_text, 'html.parser')
    date_format = "%d.%m.%Y"

    # Initialize the latest_date and the href_value
    latest_date = datetime.min
    href_value = ""

    # Find all the 'a' tags with "Liste der Gesellschafter"
    tags_a = soup.find_all('a', string=lambda x: x and "Liste der Gesellschafter" in x)

    # Loop through all the tags
    for tag_a in tags_a:
        # find date in the format dd.mm.yyyy
        date_string = re.search(r'\d{2}\.\d{2}\.\d{4}', tag_a.text)
        if date_string:
            date = datetime.strptime(date_string.group(), date_format)
            if date > latest_date:
                latest_date = date
                link = tag_a['href']
                file_name = tag_a.text
    
    return link, file_name
            

def create_payload_for_document_download(raw_text:str) -> str:
    soup = BeautifulSoup(raw_text, 'html.parser')

    # Find the input element with name="javax.faces.ViewState"
    view_state_input = soup.find('input', {'name': 'javax.faces.ViewState'})

    # Extract the value attribute
    view_state_value = view_state_input['value']
    input_element = soup.find('input', {'name': lambda value: value and value.startswith('transactionref_')})
    transaction_ref = input_element['name']

    payload = {'doccartForm': 'doccartForm', 'doccartForm:j_idt351': 'Zur Freischaltung', 'javax.faces.ViewState': view_state_value, transaction_ref: ''}
    payload = urllib.parse.urlencode(payload)

    return payload


def get_download_link(raw_text:str):
    soup = BeautifulSoup(raw_text, 'html.parser')

    # Find the <div> element with the class "download-wrapper"
    div_element = soup.find('div', class_='download-wrapper')

    # Find the <a> element within the <div> element
    a_element = div_element.find('a')

    # Extract the value of the href attribute
    href_value = a_element['href']
    if 'format=null' in href_value:
        href_value = href_value.replace('format=null', 'format=pdf')
    else:
        href_value += '&format=pdf'

    return href_value