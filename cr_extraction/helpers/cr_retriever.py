import requests
import io
import re
from datetime import datetime
import mechanicalsoup
from PIL import Image, ImageSequence
import os
from typing import Tuple, List, Dict
from google.cloud import storage
import xml.etree.ElementTree as ET
import img2pdf

class CommercialRegisterRetriever:
    def __init__(self, session_id: str = None, company_name: str = None):
        self.browser = mechanicalsoup.StatefulBrowser(user_agent='Chrome')

        if session_id is None:
            self.browser.open("https://www.unternehmensregister.de/ureg/index.html")
            url = self.browser.page.select("ul.service__list li a")[0].attrs["href"]
            self.session_id = url.split(";")[1].split("?")[0]
       
        self.company = {}
        self.gs_date = ""
        self.gs_file_name = ""
        

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
                self.gs_file_name = elements[0].text
                self.browser.open_relative(elements[0].attrs["href"])
                level += 1
                break

        file_format = [x.attrs["value"] for x in self.browser.page.select("input#format_orig")][0]

        self.gs_date = self.browser.page.select("div>table.file-info-table tbody tr:nth-of-type(2) td:nth-of-type(2)")[
            0].text.strip().replace("\n", "")
        date_2 = self.browser.page.select("div>table.file-info-table tbody tr:nth-of-type(4) td:nth-of-type(2)")[
            0].text.strip().replace("\n", "")
        

        if self.gs_date == "unbekannt":
            self.gs_date = date_2

        self.browser.select_form("#dkform")
        self.browser["format"] = file_format
        self.browser.submit_selected("add2cart")
        return

    def _upload_file_to_gcp(self, storage_client: storage.Client, response: requests.Response, full_path: str) -> None:
        # change target file name to pdf
        filename, file_extension = os.path.splitext(full_path)
        if file_extension.lower() in ['.tif', '.tiff']:
            full_path = "{}.pdf".format(filename)

        # init bucket and blob
        bucket_name = "cr_documents"
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(full_path)
        
        if file_extension.lower() in ['.tif', '.tiff']:
            response.raw.decode_content = True
            # Convert the TIFF content to a PDF byte array
            with io.BytesIO() as pdf_buffer:
                pdf_bytes = img2pdf.convert(response.raw)

            blob.content_type = 'application/pdf'
            
            with blob.open("wb") as f:
                f.write(pdf_bytes)
        
        else:
            with blob.open("wb") as f:
                f.write(response.content)
        
        print("File {} uploaded to {}.".format(full_path, bucket_name))
        return full_path

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

        # get si links
        si = self.browser.page.select(".reglink[id*='SI']")

        # get company information
        results_page = self.browser.page
        results = results_page.find("tbody").find_all("tr", attrs={"class": None})

        for i in range(0, len(results), 2):
            company = {}
            company["court_city"] = results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\n")[0]
            company["court"] = results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\xa0")[2].strip()
            company["id"] = results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\xa0")[3].strip() + " " + results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\xa0")[4].strip() 
            company["name"] = results[i+1].find("td", attrs={"class": "RegPortErg_FirmaKopf"}).text.strip()
            company["city"] = results[i+1].find("td", attrs={"class": "RegPortErg_SitzStatusKopf"}).text.strip()
            company["status"] = results[i+1].findAll("td", attrs={"class": "RegPortErg_SitzStatusKopf"})[1].text.strip()
            company["search_index"] = int(i/2)
            company["document_links"] = {"si": "https://www.unternehmensregister.de/ureg/registerPortal.html;{}{}".format(self.session_id, si[int(i/2)].attrs["href"]),}

            companies.append(company)
            i+=1
            
        return companies
    
    def add_documents_to_cart(self, company: Dict, documents: List[str]) -> None:
        # set company name
        self.company = company
        
        # add all documents to the cart
        if "gs" in documents:
            self._add_gs_to_cart(index = self.company["search_index"])

        if "si" in documents:
            self._add_si_to_cart(si_link = self.company["document_links"]["si"])

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
        
        # init cloud storage
        storage_client = storage.Client(project="cr-extraction")
        
        # download all files in the basket onto cloud storage
        uploaded_file_paths = []
        for download in downloads:
            url = 'https://www.unternehmensregister.de/ureg/{}'.format(download)
            result = requests.get(url, allow_redirects=True, stream=True)  # to get content after redirection

            if 'content-disposition' not in result.headers:
                # Most likely failed to fetch because HR is down
                continue
            d = result.headers['content-disposition']
            file_format = re.findall("filename=(.+)", d)[0].split(".")[1].lower()

            if file_format == "xml":
                document_name = "SI"
                # basic_information = self._retrieve_basic_information(result.content)
            else:
                document_name = self.gs_file_name if self.gs_file_name != "" else "GS"
               

            # set filename and path
            file_name = "{}-{}.{}".format(document_name, self.company["name"], file_format)
            full_path = "{}_{}_{}/{}".format(self.company["name"], self.company["court"], self.company["id"], file_name)

            # save file
            upload_result = self._upload_file_to_gcp(storage_client, result, full_path)
            uploaded_file_paths.append(upload_result)

        return self.company, uploaded_file_paths
            
        
    

        

                
            
