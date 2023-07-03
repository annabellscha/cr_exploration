import requests
import fake_useragent
import re

class CommercialRegisterRetriever:

    def __init__(self, view_state:str = None) -> None:
        self.view_state = view_state
        self.user_agent = fake_useragent.UserAgent().chrome
        self.jsession_id = self._retrieve_jsession_id()
    
    def _retrieve_jsession_id(self) -> None:
        response = self._retrieve_data()
        regex = r'jsessionid=([a-zA-Z0-9]+\.[a-zA-Z0-9]+-1)\b'

        match = re.search(regex, response.text)
        jsessionid = match.group(1)
        return jsessionid
        

    def _retrieve_data(self, payload: dict = {}, method:str = "GET") -> requests.Response:
        base_url = "https://www.unternehmensregister.de/ureg/"
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
        response = requests.request(method=method, url=base_url, headers=headers, data=payload)

        return response

    def get_jsession_id(self) -> str:
        return self.jsession_id