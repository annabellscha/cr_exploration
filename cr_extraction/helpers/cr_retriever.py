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
import re
import os
# from supabase import create_client, Client
from dotenv import load_dotenv

class CommercialRegisterRetriever:
    def __init__(self, session_id: str = None, company_name: str = None):
        self.browser = mechanicalsoup.StatefulBrowser(user_agent='Chrome')

        if session_id is None:
            self.browser.open("https://www.unternehmensregister.de/ureg/index.html")
            url = self.browser.page.select("ul.service__list li a")[0].attrs["href"]
            self.session_id = url.split(";")[1].split("?")[0]
       
        self.company = {}
        self.file_date = ""
        self.file_name = ""
        self.file_type = ""

    def _clean_text(self, text: str) -> str:
        clean_text = re.sub(r"[^a-zA-Z0-9 ]", "", text)
        return clean_text
        

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
                self.file_name = elements[0].text
                self.file_type = "gs"
                self.browser.open_relative(elements[0].attrs["href"])
                level += 1
                break

        file_format = [x.attrs["value"] for x in self.browser.page.select("input#format_orig")][0]

        self.file_date = self.browser.page.select("div>table.file-info-table tbody tr:nth-of-type(2) td:nth-of-type(2)")[
            0].text.strip().replace("\n", "")
        date_2 = self.browser.page.select("div>table.file-info-table tbody tr:nth-of-type(4) td:nth-of-type(2)")[
            0].text.strip().replace("\n", "")
        

        if self.file_date == "unbekannt":
            self.file_date = date_2

        self.browser.select_form("#dkform")
        self.browser["format"] = file_format
        self.browser.submit_selected("add2cart")
        return

    def _add_registration_to_cart(self, index):
        # Open document tree
        self.browser.open(
            "https://www.unternehmensregister.de/ureg/registerPortal.html;{}?submitaction=showDkTree&searchIdx={}".format(
                self.session_id, index))

        # initial level = 2, expand from there
        level = 2

        while True:
            elements = self.browser.page.select("div.dktree-container.level-{} span a".format(level))

            if len(elements) == 0:
                raise Exception("no registration found")
            if any("Dokumente zur Registernummer" in element.string for element in elements):
                element = list(filter(lambda x: x.text == "Dokumente zur Registernummer", elements))
                self.browser.open_relative(element[0].attrs["href"])
                level += 1
                continue
            if any("Weitere Urkunden / Unterlagen" in element.string for element in elements):
                element = list(filter(lambda x: x.text == "Weitere Urkunden / Unterlagen", elements))
                self.browser.open_relative(element[0].attrs["href"])
                level += 1
                continue
            if any("Anmeldung vom" in element.string for element in elements):
                # Extract dates and convert them to datetime objects
                dates_elements = [(datetime.strptime(e.string.split('vom ')[1], '%d.%m.%Y'), e) for e in elements if 'Anmeldung vom ' in e.string]

                # Find the element with the most recent date
                element = max(dates_elements, key=lambda x: x[0])[1] if dates_elements else None

                self.file_name = element.string
                self.file_type = "rg"
                self.browser.open_relative(element.attrs["href"])
                level += 1
                break
            if any("Anmeldung" in element.string for element in elements):
                element = list(filter(lambda x: x.text == "Anmeldung", elements))
                self.browser.open_relative(element[0].attrs["href"])
                level += 1
                continue


        # download the file
        file_format = [x.attrs["value"] for x in self.browser.page.select("input#format_orig")][0]

        self.file_date = self.browser.page.select("div>table.file-info-table tbody tr:nth-of-type(2) td:nth-of-type(2)")[
            0].text.strip().replace("\n", "")
        date_2 = self.browser.page.select("div>table.file-info-table tbody tr:nth-of-type(4) td:nth-of-type(2)")[
            0].text.strip().replace("\n", "")
        

        if self.file_date == "unbekannt":
            self.file_date = date_2

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
        print(f"This is the blob : {blob}")
        print(f"This is the full path : {full_path}")
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
    
    # def _upload_file_to_supabase(response: requests.Response, full_path: str) -> None:
    #     # change target file name to pdf
    #     filename, file_extension = os.path.splitext(full_path)
    #     if file_extension.lower() in ['.tif', '.tiff']:
    #         full_path = "{}.pdf".format(filename)

    #     # init supabase client
    #     url: str = os.environ.get("SUPABASE_URL")
    #     key: str = os.environ.get("SUPABASE_KEY")
    #     supabase: Client = create_client(url, key)

    #     # prepare file content
    #     if file_extension.lower() in ['.tif', '.tiff']:
    #         response.raw.decode_content = True
    #         # Convert the TIFF content to a PDF byte array
    #         with io.BytesIO() as pdf_buffer:
    #             pdf_bytes = img2pdf.convert(response.raw)

    #         content_type = 'application/pdf'
    #         file_content = pdf_bytes

    #     else:
    #         content_type = 'application/xml'  # or whatever the content type of your other files is
    #         file_content = response.content

    #     # upload file to supabase
    #     response = supabase.storage.upload_file(
    #         path=full_path,
    #         file_or_path=file_content,
    #         content_type=content_type,
    #     )

    #     if response.error:
    #         print(f"Failed to upload {full_path}: {response.error.message}")
    #     else:
    #         print(f"File {full_path} uploaded to Supabase.")
    #         return full_path

    def _parse_company_results_page(self, results: List[Dict]) -> List[Dict]:
        results_page = self.browser.page
        results = results_page.find("tbody").find_all("tr", attrs={"class": None})
        companies = []
        for i in range(0, len(results), 2):
            company = {}
            try:
                company["court_city"] = results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\n")[0]
            except:
                company["court_city"] = None

            try:
                company["court"] = results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\xa0")[2].strip()
            except:
                company["court"] = None

            try:
                company["id"] = results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\xa0")[3].strip() + " " + results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\xa0")[4].strip() 
            except:
                company["id"] = None

            try:
                company["name"] = results[i+1].find("td", attrs={"class": "RegPortErg_FirmaKopf"}).text.strip()
            except:
                company["name"] = None

            try:
                company["city"] = results[i+1].find("td", attrs={"class": "RegPortErg_SitzStatusKopf"}).text.strip()
            except:
                company["city"] = None

            try:
                company["status"] = results[i+1].findAll("td", attrs={"class": "RegPortErg_SitzStatusKopf"})[1].text.strip()
            except:
                company["status"] = None

            company["search_index"] = int(i/2)

            company["document_urls"] = {}
            try:
                si = results[i+1].find("td", attrs={"class": "RegPortErg_RandRechts"}).find("a", string="SI").attrs["href"]
                company["document_urls"]["si"] = "https://www.unternehmensregister.de/ureg/registerPortal.html;{}{}".format(self.session_id, si)
            except:
                si = None

            try:
                dk = results[i+1].find("td", attrs={"class": "RegPortErg_RandRechts"}).find("a", string="DK").attrs["href"]
                company["document_urls"]["dk"] = "https://www.unternehmensregister.de/ureg/registerPortal.html;{}{}".format(self.session_id, dk)
            except:
                dk = None

            companies.append(company)
            i+=1
        return companies
    
    
    def extended_search(self, company_id:str = "", company_name:str = "", company_location:str = "", legal_form:str = "0", circuit_id:str = "0", register_type:str = "0", language:str = "0", start_date:str = "", end_date:str = "", return_one: bool = True) -> Dict:
        extended_search_url = "https://www.unternehmensregister.de/ureg/search1.1.html;{}".format(self.session_id)
        self.browser.open(extended_search_url)
        self.browser.select_form("#searchRegisterForm")

        # Fill in the form fields
        self.browser["searchRegisterForm:extendedResearchCompanyName"] = company_name
        self.browser["searchRegisterForm:extendedResearchRegisterNumber"] = company_id
        self.browser["searchRegisterForm:extendedResearchCompanyLocation"] = company_location
        self.browser["searchRegisterForm:extendedResearchLegalForm"] = legal_form
        self.browser["searchRegisterForm:extendedResearchCircuitId"] = circuit_id
        self.browser["searchRegisterForm:extendedResearchRegisterType"] = register_type
        self.browser["searchRegisterForm:extendedResearchLanguage"] = language
        self.browser["searchRegisterForm:extendedResearchStartDate"] = start_date
        self.browser["searchRegisterForm:extendedResearchEndDate"] = end_date
        self.browser["submitaction"] = "searchExtendedResearch"
        self.browser["javax.faces.ViewState"] = self.browser.page.find('input', {'id': 'j_id1:javax.faces.ViewState:1'})['value']

        self.browser.submit_selected()

         # Find the container div
        container_div = self.browser.page.select_one('.container.result_container.global-search')

        # Find all divs with class 'row back' within the container
        row_back_divs = container_div.select('.row.back')

        # If there are no results or multiple results, raise an exception
        if len(row_back_divs) == 0:
            raise Exception("no results found")
        elif len(row_back_divs) > 1:
            raise Exception("multiple results found")

        # open search results
        self.browser.open_relative("https://www.unternehmensregister.de/ureg/registerPortal.html;{}".format(self.session_id))
        companies = self._parse_company_results_page(self.browser.page)

        # we expect only one result for the company id
        if return_one:
            if len(companies) != 1:
                raise Exception("no results found/ multiple companies found")
                
            return companies[0]
        else:
            return companies
        
    def search(self, company_name: str) -> Tuple[List[Tuple[str, int, str]], str]:
        # Fill-in the search form
        self.browser.select_form('#globalSearchForm')
        self.browser["globalSearchForm:extendedResearchCompanyName"] = company_name
        self.browser["submitaction"] = "searchRegisterData"
        self.browser.submit_selected(btnName="globalSearchForm:btnExecuteSearchOld")

        # self.browser.open(
        #     "https://www.unternehmensregister.de/ureg/search1.1.html;{}".format(
        #         self.session_id))
        # self.browser.select_form("#searchRegisterForm")
        # self.browser["searchRegisterForm:extendedResearchCompanyName"] = company_name
        # self.browser["searchRegisterForm:extendedResearchRegisterNumber"] = company_id
        # # self.browser["searchRegisterForm:extendedResearchStartDate"] = "01.01.2014"

        # self.browser["submitaction"] = "searchExtendedResearch"
        # self.browser.submit_selected()

        # page = self.browser.page
        # # select first company in the list
        # links = self.browser.page.find_all('a', href=lambda href: href and 'registerPortalAdvice.html' in href)
        # self.browser.open_relative(links[0].attrs["href"])
        

        # open the search results
        self.browser.open_relative(self.browser.page.select("div.right a")[0].attrs["href"])

        # retrieve all companies in a list
        companies = []

        # get si links
        # si = self.browser.page.select(".reglink[id*='SI']")

        # get company information
        results_page = self.browser.page
        results = results_page.find("tbody").find_all("tr", attrs={"class": None})

        for i in range(0, len(results), 2):

            company = {}
            try:
                company["court_city"] = results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\n")[0]
            except:
                company["court_city"] = None

            try:
                company["court"] = results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\xa0")[2].strip()
            except:
                company["court"] = None

            try:
                company["id"] = results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\xa0")[3].strip() + " " + results[i].find("td", attrs={"class": "RegPortErg_AZ"}).text.split("\xa0")[4].strip() 
            except:
                company["id"] = None

            try:
                company["name"] = results[i+1].find("td", attrs={"class": "RegPortErg_FirmaKopf"}).text.strip()
            except:
                company["name"] = None

            try:
                company["city"] = results[i+1].find("td", attrs={"class": "RegPortErg_SitzStatusKopf"}).text.strip()
            except:
                company["city"] = None

            try:
                company["status"] = results[i+1].findAll("td", attrs={"class": "RegPortErg_SitzStatusKopf"})[1].text.strip()
            except:
                company["status"] = None

            company["search_index"] = int(i/2)

            company["document_urls"] = {}
            try:
                si = results[i+1].find("td", attrs={"class": "RegPortErg_RandRechts"}).find("a", string="SI").attrs["href"]
                company["document_urls"]["si"] = "https://www.unternehmensregister.de/ureg/registerPortal.html;{}{}".format(self.session_id, si)
            except:
                si = None

            try:
                dk = results[i+1].find("td", attrs={"class": "RegPortErg_RandRechts"}).find("a", string="DK").attrs["href"]
                company["document_urls"]["dk"] = "https://www.unternehmensregister.de/ureg/registerPortal.html;{}{}".format(self.session_id, dk)
            except:
                dk = None

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
            self._add_si_to_cart(si_link = self.company["document_urls"]["si"])

        if "rg" in documents:
            self._add_registration_to_cart(index = self.company["search_index"])

        return
    
    def download_documents_from_basket(self, bypass_storage: bool = False) -> Tuple[Dict, List[Dict]]:
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
                document_type = "si"
                # basic_information = self._retrieve_basic_information(result.content)
            else:
                document_name = self.file_name if self.file_name != "" else "unknown filename"
                document_type = self.file_type if self.file_type != "" else "unknown file type"
        
            document_name_cl = self._clean_text(document_name)
            company_name_cl = self._clean_text(self.company["name"])
            court_cl = self._clean_text(self.company["court"])
            company_id_cl = self._clean_text(self.company["id"])
            

            # set filename and path
            file_name = "{}-{}.{}".format(document_name_cl, company_name_cl, file_format)
            full_path = "{}_{}_{}/{}".format(company_name_cl, court_cl, company_id_cl, file_name)

            # save file
              # init cloud storage
            if not bypass_storage:
                storage_client = storage.Client(project="cr-extraction")
                upload_result = {"type": document_type, "document_name":file_name, "url": self._upload_file_to_gcp(storage_client, result, full_path)}
                uploaded_file_paths.append(upload_result)
            else: 
                uploaded_file_paths.append({"type": document_type, "document_binary": result.content, "document_name": file_name})

        return self.company, uploaded_file_paths
            
        
    

        

                
            

