import re

def parse_filename(filename):
    result = {}
    
    # Extracting company name
    company_name_match = re.search(r'/D\d+_HRB \d+_(.+?)/SI-', filename)
    if company_name_match:
        result['company_name'] = company_name_match.group(1)
    
    # Extracting city and registration number
    city_registration_match = re.search(r'(.+)/D\d+_(\w+)\.xml', filename)
    if city_registration_match:
        result['city'] = city_registration_match.group(1)
        result['registration_number'] = city_registration_match.group(2)
    
    # Extracting filename
    filename_match = re.search(r'/(.+\.xml)', filename)
    if filename_match:
        result['filename'] = filename_match.group(1)
    
    # Extracting document type
    document_type_match = re.search(r'/(\w+)-', filename)
    if document_type_match:
        result['document_type'] = document_type_match.group(1)
    
    return result
