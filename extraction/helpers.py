
from bs4 import BeautifulSoup


def get_view_state(soup: BeautifulSoup) -> str:
    view_state_input = soup.find('input', {'name': 'javax.faces.ViewState'})
    view_state_value = view_state_input['value']
    return view_state_value


def check_if_basket_has_content(soup: BeautifulSoup) -> bool:
    # Find the <span> element with the class "basket-iem-counter"
    span_element = soup.find('span', class_='basket-item-counter')

    # Check if the text content of the <span> element is "1"
    has_content = int(span_element.get_text(strip=True)) > 0

    return has_content