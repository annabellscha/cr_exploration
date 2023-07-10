import re
from typing import List, Dict
import xml.etree.ElementTree as ET

def retrieve_si_data(self, xml_string) -> Dict:
    try:
    # Define the namespace dictionary
        namespace = {"x": "http://www.xjustiz.de", "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

        # Parse the XML content
        root = ET.fromstring(xml_string)

        # Retrieve the desired attributes
        company_name = root.find(".//x:Bezeichnung_Aktuell", namespace).text
        location = root.find(".//x:Sitz/x:Ort", namespace).text
        id = root.find(".//x:Aktenzeichen", namespace).text
        court = root.find(".//x:Gericht/x:content", namespace).text
        

        # Create a dictionary with the retrieved attributes
        basic_information = { 
            "name": company_name,
            "location": location,
            "id": id,
            "court": court  
        }
    except:
        basic_information = {
            "name": "unknown",
            "location": "unknown",
            "id": "unknown",
            "court": "unknown"
        }

    return basic_information