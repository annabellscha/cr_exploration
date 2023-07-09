import requests
import re
from .extraction_helpers import *
import mechanicalsoup
from PIL import Image, ImageSequence
import os
from typing import Tuple, List, Dict
import uuid

class CommercialRegisterRetriever:
    def __init__(self, session_id: str = None):
        self.browser = mechanicalsoup.StatefulBrowser(user_agent='Chrome')

        if session_id is None:
            self._init_session()
       
        self.company_name = ""
        self.date = ""

    def _init_session(self):
        self.browser.open("https://www.unternehmensregister.de/ureg/index.html")
        url = self.browser.page.select("ul.service__list li a")[0].attrs["href"]
        self.session_id = url.split(";")[1].split("?")[0]

    def _add_si_to_cart(self, si_link):
        # Pull Overview
        self.browser.open(si_link)

    def _add_gs_to_cart(self, index):
        # Open document tree
        self.browser.open(
            "https://www.unternehmensregister.de/ureg/registerPortal.html;{}?submitaction=showDkTree&searchIdx={}".format(
                self.session_id, index))

        # Expand
        level = 2

        while True:
            elements = self.browser.page.select("div.dktree-container.level-{} span a".format(level))
            if len(elements) == 0:
                raise Exception("no gs list found")
            if level == 3:
                element = list(filter(lambda x: x.text == "Liste der Gesellschafter", elements))
                if len(element) == 0:
                    raise Exception("no gs list found")
                self.browser.open_relative(element[0].attrs["href"])
                level += 1
                continue
            if "Liste der" not in elements[0].text:
                self.browser.open_relative(elements[0].attrs["href"])
                level += 1
            else:
                self.browser.open_relative(elements[0].attrs["href"])
                level += 1
                break

        file_format = [x.attrs["value"] for x in self.browser.page.select("input#format_orig")][0]

        self.date = self.browser.page.select("div>table.file-info-table tbody tr:nth-of-type(2) td:nth-of-type(2)")[
            0].text.strip().replace("\n", "")
        date_2 = self.browser.page.select("div>table.file-info-table tbody tr:nth-of-type(4) td:nth-of-type(2)")[
            0].text.strip().replace("\n", "")
        if self.date == "unbekannt":
            self.date = date_2

        self.browser.select_form("#dkform")
        self.browser["format"] = file_format
        self.browser.submit_selected("add2cart")
        return

    def search(self, company_name: str) -> Tuple[List[Tuple[str, int, str]], str]:
        # Fill-in the search form
        self.browser.select_form('#globalSearchForm')
        self.browser["globalSearchForm:extendedResearchCompanyName"] = company_name
        self.browser["submitaction"] = "searchRegisterData"
        self.browser.submit_selected(btnName="globalSearchForm:btnExecuteSearchOld")

        # open the search results
        self.browser.open_relative(self.browser.page.select("div.right a")[0].attrs["href"])

        # retrieve all companies in a list
        companies = []
        i = 0
        si = self.browser.page.select(".reglink[id*='SI']")
        for result in self.browser.page.select('td.RegPortErg_FirmaKopf'):
            company = {}
            company["id"] = uuid.uuid4().hex
            company["name"] = result.text
            company["index"] = i
            company["link"] = "https://www.unternehmensregister.de/ureg/registerPortal.html;{}{}".format(self.session_id, si[i].attrs["href"])
            companies.append(company)
            i += 1
        
        return companies
    
    def add_documents_to_cart(self, company: Dict, documents: List[str]) -> None:
        # add all documents to the cart
        if "gs" in documents:
            self._add_gs_to_cart(index = company["index"])

        if "si" in documents:
            self._add_si_to_cart(si_link = company["link"])

        return
    
    def download_documents_from_basket(self):
        # open the cart & skip payment overview
        self.browser.open_relative("doccart.html;{}".format(self.session_id))
        self.browser.select_form("#doccartForm")
        submit_name = self.browser.page.select("div.right input")[0].attrs["name"]
        self.browser.submit_selected(submit_name)
        self.browser.select_form("#paymentFormOverview")
        self.browser.submit_selected("paymentFormOverview:btnNext")
        self.browser.open_relative("doccart.html;{}".format(self.session_id))

        # retrieve all download links
        downloads = [x.attrs["href"] for x in self.browser.page.select("div.download-wrapper div a:not(.disabled)")]
        if len(downloads) == 0:
            raise Exception("no downloads found")

        # download all files in the basket
        for download in downloads:
            url = 'https://www.unternehmensregister.de/ureg/{}'.format(download)
            r = requests.get(url, allow_redirects=True, stream=True)  # to get content after redirection

            if 'content-disposition' not in r.headers:
                # Most likely failed to fetch because HR is down
                continue
            d = r.headers['content-disposition']
            file_format = re.findall("filename=(.+)", d)[0].split(".")[1]

            filename = ""
            if file_format.lower() == "tif" or file_format.lower() == "tiff":
                file_format = "pdf"
                fname = "GS-Liste-{}-{}.{}".format(self.name, self.date, file_format)
                filename = "out/{}/{}".format(self.name, fname)
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                r.raw.decode_content = True
                image = Image.open(r.raw)

                images = []
                for i, page in enumerate(ImageSequence.Iterator(image)):
                    page = page.convert("RGB")
                    images.append(page)
                if len(images) == 1:
                    images[0].save(filename)
                else:
                    images[0].save(filename, save_all=True, append_images=images[1:])
                gs_list = filename
            elif file_format.lower() == "xml":
                fname = "SI.xml"
                filename = "out/{}/{}".format(self.company_name, fname)
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(r.content)
                si = filename
            else:
                fname = "GS-Liste-{}-{}.{}".format(self.company_name, self.date, file_format)
                filename = "out/{}/{}".format(self.company_name, fname)
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                with open(filename, 'wb') as f:
                    f.write(r.content)
                gs_list = filename
            
            return gs_list
        
    

        

                
            
