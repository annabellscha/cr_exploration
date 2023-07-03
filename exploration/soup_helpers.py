
from bs4 import BeautifulSoup
import re


def get_view_state(soup: BeautifulSoup) -> str:
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


def check_if_basket_has_content(soup: BeautifulSoup) -> bool:
    # Find the <span> element with the class "basket-iem-counter"
    span_element = soup.find('span', class_='basket-item-counter')

    # Check if the text content of the <span> element is "1"
    has_content = int(span_element.get_text(strip=True)) > 0

    return has_content