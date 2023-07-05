import requests
import fake_useragent
import re
from .extraction_helpers import *
import urllib.parse

class CommercialRegisterRetriever:

    def __init__(self) -> None:
        self.user_agent = fake_useragent.UserAgent().chrome
        self.jsession_id: str = None
        self.view_state: str = None

        self._get_session_id_view_state()
    
    def _get_session_id_view_state(self) -> None:
        response = self._retrieve_data(use_session=False)

        # set jsession id
        regex = r'jsessionid=([a-zA-Z0-9]+\.[a-zA-Z0-9]+-1)\b'
        match = re.search(regex, response.text)
        self.jsession_id = match.group(1)

        # set viewstate
        self.view_state = get_view_state(response.text)
        

    def _retrieve_data(self, payload: dict = {}, method:str = "GET", path:str = "", use_session:bool = True) -> requests.Response:
        base_url = "https://www.unternehmensregister.de/ureg/"
        jsession_url = f";jsessionid={self.jsession_id}"
        params = ""

        url = f"{base_url}{path}{jsession_url}{params}"

        headers = {
                'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"macOS"',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': self.user_agent,
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
                'Sec-Fetch-Site': 'same-origin',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-User': '?1',
                'Sec-Fetch-Dest': 'document',
                'Cookie': 'checkCookieSession=true'
            }
        response = requests.request(method=method, url=url, headers=headers, data=payload)

        return response
    

    
    def retrieve_document(self, search_term: str):
        payload = f'globalSearchForm=globalSearchForm&globalSearchForm%3AextendedResearchCompanyName={search_term}&globalSearchForm%3Ahidden_element_used_for_validation_only=aaa&submitaction=globalsearch&globalsearch=true&globalSearchForm%3AbtnExecuteSearchOld=Suchen&javax.faces.ViewState={self.view_state}'
        params = f"?submitaction=regnav&company={search_term}"

        # submit search
        result = self._retrieve_data(payload=payload, method="POST", path="registerPortalAdvice.html", params=params)

        # get search result
        result = self._retrieve_data(path="result.html")
        company_name, company_id = get_company_name_id(result.text)

        # go to registerportaladvice
        result = self._retrieve_data(path="registerPortalAdvice.html", params=f"?submitaction=regnav&company={company_id}")

        # loop through document tree
        result = self._retrieve_data(path="registerPortal.html", params=f"?submitaction=showDkTree&searchIdx=0")
        submit_action = identify_dk_links(result.text, level=0)

        result = self._retrieve_data(path="registerPortal.html", params=submit_action)
        submit_action = identify_dk_links(result.text, level=1)

        result = self._retrieve_data(path="registerPortal.html", params=submit_action)  
        submit_action, file_name = get_latest_document_link(result.text)

        result = self._retrieve_data(path="registerPortal.html", params=submit_action)
        payload = create_payload_for_document_selection(result.text)

        # put document in basket
        result = self._retrieve_data(payload=payload, method="POST", path="registerPortal.html")
        result = self._retrieve_data(path="doccart.html")

        payload = create_payload_for_document_download(result.text)
        result = self._retrieve_data(payload=payload, method="POST", path="doccart.html")

        # click through payment
        result = self._retrieve_data(path="payment_overview.html")
        view_state = get_view_state(result.text)
        payload = {
            'javax.faces.ViewState': view_state,
            'paymentFormOverview': 'paymentFormOverview',
            'paymentFormOverview:acceptAGB': 'true',
            'paymentFormOverview:btnNext': 'Jetzt freischalten',
            'submitAmount': '0',
            'submitaction': 'paymentSubmit'
        }
        payload = urllib.parse.urlencode(payload)

        self._retrieve_data(payload=payload, method="POST", path="payment_overview.html")

        self._retrieve_data(path="payment_confirm2.html")
        self._retrieve_data(path="doccart.html")

        # download document
        download_link = get_download_link(result.text)
        result = self._retrieve_data(path=download_link, use_session=False)
        current_datetime = datetime.now()


        file_store_name = company_id + "_" + company_name + "_" + file_name + '_' + current_datetime.isoformat() + '.pdf'

        # Check if the request was successful (status code 200)
        if result.status_code == 200:
            # Save the response content to a file
            with open(file_store_name, 'wb') as file:
                file.write(result.content)
            print('File successfully retrieved and saved.')
        else:
            print('Error occurred while retrieving the file.')