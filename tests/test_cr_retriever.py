from dotenv import load_dotenv
from datetime import timedelta
import datetime
from typing import List
from cr_extraction.helpers.cr_retriever import CommercialRegisterRetriever
from cr_extraction.main import search_companies, download_files
from google.cloud import storage
import os
import logging
import pytest
from flask import Flask, request

# load env
load_dotenv()

# set logging
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

def test_cr_search_companies():
    retriever = CommercialRegisterRetriever()
    companies = retriever.search("BCN Food Tech GmbH")
    assert len(companies) > 0   

def test_cr_download_files():
    session_id: str = None
    documents: List[str] = ["gs", "si"] 
    company_name: str = 'Tacto'

    # initialize retriever
    retriever = CommercialRegisterRetriever(session_id=session_id)

    # load company data
    try:
        company = retriever.search(company_name=company_name)[0]
    except Exception as e:
        print(e)
    
    # add documents to cart
    retriever.add_documents_to_cart(company=company, documents=documents)

    # download documents
    company_name, result = retriever.download_documents_from_basket(bypass_storage=True)

    assert len(result) > 0


def test_cr_find_company_by_hrb():
    retriever = CommercialRegisterRetriever()
    company = retriever.extended_search(company_id="HRB 269123")
    assert company is not None


def test_cr_download_files_by_hrb():
    session_id: str = None
    documents: List[str] = ["gs"] 
    # company_id: str = "HRB 269123"
    company_id: str = "HRB 235083"

    # initialize retriever
    retriever = CommercialRegisterRetriever(session_id=session_id)

    # load company data
    company = retriever.extended_search(company_id=company_id)

    # add documents to cart
    retriever.add_documents_to_cart(company=company, documents=documents)

    # download documents
    company_name, result = retriever.download_documents_from_basket(bypass_storage=True)

    assert len(result) > 0
    


# <form id="searchRegisterForm" name="searchRegisterForm" method="post" action="/ureg/search1.1.html;jsessionid=EF645278890089C83D7D7DEACD3FABBF.web04-1" class="search-form" enctype="application/x-www-form-urlencoded">
# <input type="hidden" name="searchRegisterForm" value="searchRegisterForm">


#                                     <!-- Firmendaten -->
#                                     <div class="search-row headline first">
#                                         <div class="col">
#                                             <h2>Firmendaten</h2>
#                                             <p class="forms-validation-message"></p>
#                                         </div>
#                                     </div>
                                       
#                                     <!-- Firmenname -->
#                                     <div class="search-row">
#                                         <div class="col">
#                                             <label class="sr-only input-label" for="searchRegisterForm:extendedResearchCompanyName">Firmenname</label><input id="searchRegisterForm:extendedResearchCompanyName" type="text" name="searchRegisterForm:extendedResearchCompanyName" value="" class="form-control" placeholder="Firmenname">
#                                         </div>
#                                     </div>

#                                     <!-- Niederlassung / Sitz -->
#                                     <div class="search-row">
#                                         <div class="col">
#                                             <label class="sr-only input-label" for="searchRegisterForm:extendedResearchCompanyLocation">Niederlassung / Sitz</label><input id="searchRegisterForm:extendedResearchCompanyLocation" type="text" name="searchRegisterForm:extendedResearchCompanyLocation" value="" class="form-control" placeholder="Niederlassung / Sitz">
#                                         </div>
#                                     </div>

#                                     <!-- Rechtsform -->
#                                     <div class="search-row">
#                                         <div class="col">
#                                             <div class="select-wrapper"><select id="searchRegisterForm:extendedResearchLegalForm" name="searchRegisterForm:extendedResearchLegalForm" class="select select2-hidden-accessible" size="1" aria-label="Rechtsform" data-select2-id="searchRegisterForm:extendedResearchLegalForm" tabindex="-1" aria-hidden="true">	<option value="0" data-select2-id="2">Rechtsform</option>
# 	<option value="21">Aktiengesellschaft</option>
# 	<option value="25">Bergrechtliche Gewerkschaft</option>
# 	<option value="5">eingetragene Genossenschaft</option>
# 	<option value="28">eingetragene Gesellschaft bürgerlichen Rechts</option>
# 	<option value="19">eingetragener Verein</option>
# 	<option value="26">Einzelkaufmann / Einzelkauffrau</option>
# 	<option value="15">Europäische Aktien­gesellschaft (SE)</option>
# 	<option value="23">Europäische Ge­nossen­schaft (SCE)</option>
# 	<option value="8">Europäische wirtschaftliche Interessen­vereinigung</option>
# 	<option value="9">Gesellschaft mit beschränkter Haftung</option>
# 	<option value="11">Kommandit­gesellschaft</option>
# 	<option value="12">Kommandit­gesellschaft auf Aktien</option>
# 	<option value="13">Offene Handels­gesellschaft</option>
# 	<option value="27">Partner­schafts­gesellschaft</option>
# 	<option value="1">Rechtsform ausländischen Rechts GnR</option>
# 	<option value="29">Rechtsform ausländischen Rechts GsR</option>
# 	<option value="2">Rechtsform ausländischen Rechts HRA</option>
# 	<option value="3">Rechtsform ausländischen Rechts HRB</option>
# 	<option value="4">Rechtsform ausländischen Rechts PR</option>
# 	<option value="24">Sonstige juristische Person</option>
# 	<option value="20">Versicherungs­verein auf Gegen­seitigkeit</option>
# </select><span class="select2 select2-container select2-container--default" dir="ltr" data-select2-id="1" style="width: 351.5px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-disabled="false" aria-labelledby="select2-searchRegisterFormextendedResearchLegalForm-container"><span class="select2-selection__rendered" id="select2-searchRegisterFormextendedResearchLegalForm-container" role="textbox" aria-readonly="true" title="Rechtsform">Rechtsform</span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span>
#                                             </div>
#                                         </div>
#                                     </div>

#                                     <!-- Registergericht / Registerart -->
#                                     <div class="search-row">
#                                         <div class="row">
#                                             <div class="col-lg-6">
#                                                 <div class="select-wrapper"><select id="searchRegisterForm:extendedResearchCircuitId" name="searchRegisterForm:extendedResearchCircuitId" class="select select2-hidden-accessible" size="1" aria-label="Registergericht" data-select2-id="searchRegisterForm:extendedResearchCircuitId" tabindex="-1" aria-hidden="true">	<option value="0" data-select2-id="4">Registergericht</option>
# 	<option value="549">Aachen</option>
# 	<option value="157">Amberg</option>
# 	<option value="162">Ansbach</option>
# 	<option value="470">Arnsberg</option>
# 	<option value="187">Aschaffenburg</option>
# 	<option value="111">Augsburg</option>
# 	<option value="418">Aurich</option>
# 	<option value="290">Bad Hersfeld</option>
# 	<option value="282">Bad Homburg v.d.H.</option>
# 	<option value="572">Bad Kreuznach</option>
# 	<option value="487">Bad Oeynhausen</option>
# 	<option value="190">Bamberg</option>
# 	<option value="194">Bayreuth</option>
# 	<option value="217">Berlin (Charlottenburg)</option>
# 	<option value="480">Bielefeld</option>
# 	<option value="490">Bochum</option>
# 	<option value="557">Bonn</option>
# 	<option value="360">Braunschweig</option>
# 	<option value="258">Bremen</option>
# 	<option value="634">Chemnitz</option>
# 	<option value="197">Coburg</option>
# 	<option value="530">Coesfeld</option>
# 	<option value="228">Cottbus</option>
# 	<option value="270">Darmstadt</option>
# 	<option value="117">Deggendorf</option>
# 	<option value="499">Dortmund</option>
# 	<option value="621">Dresden</option>
# 	<option value="446">Duisburg</option>
# 	<option value="550">Düren</option>
# 	<option value="441">Düsseldorf</option>
# 	<option value="305">Eschwege</option>
# 	<option value="507">Essen</option>
# 	<option value="695">Flensburg</option>
# 	<option value="281">Frankfurt am Main</option>
# 	<option value="237">Frankfurt/Oder</option>
# 	<option value="8">Freiburg</option>
# 	<option value="296">Friedberg</option>
# 	<option value="306">Fritzlar</option>
# 	<option value="286">Fulda</option>
# 	<option value="167">Fürth</option>
# 	<option value="510">Gelsenkirchen</option>
# 	<option value="297">Gießen</option>
# 	<option value="372">Göttingen</option>
# 	<option value="482">Gütersloh</option>
# 	<option value="516">Hagen</option>
# 	<option value="261">Hamburg</option>
# 	<option value="500">Hamm</option>
# 	<option value="300">Hanau</option>
# 	<option value="379">Hannover</option>
# 	<option value="387">Hildesheim</option>
# 	<option value="200">Hof</option>
# 	<option value="654">Homburg</option>
# 	<option value="212">Ingolstadt</option>
# 	<option value="517">Iserlohn</option>
# 	<option value="739">Jena</option>
# 	<option value="609">Kaiserslautern</option>
# 	<option value="308">Kassel</option>
# 	<option value="121">Kempten (Allgäu)</option>
# 	<option value="567">Kerpen</option>
# 	<option value="706">Kiel</option>
# 	<option value="454">Kleve</option>
# 	<option value="582">Koblenz</option>
# 	<option value="568">Köln</option>
# 	<option value="283">Königstein</option>
# 	<option value="309">Korbach</option>
# 	<option value="458">Krefeld</option>
# 	<option value="615">Landau</option>
# 	<option value="127">Landshut</option>
# 	<option value="444">Langenfeld</option>
# 	<option value="655">Lebach</option>
# 	<option value="649">Leipzig</option>
# 	<option value="497">Lemgo</option>
# 	<option value="320">Limburg</option>
# 	<option value="716">Lübeck</option>
# 	<option value="606">Ludwigshafen a.Rhein (Ludwigshafen)</option>
# 	<option value="394">Lüneburg</option>
# 	<option value="593">Mainz</option>
# 	<option value="33">Mannheim</option>
# 	<option value="328">Marburg</option>
# 	<option value="134">Memmingen</option>
# 	<option value="656">Merzig</option>
# 	<option value="462">Mönchengladbach</option>
# 	<option value="586">Montabaur</option>
# 	<option value="136">München</option>
# 	<option value="535">Münster</option>
# 	<option value="339">Neubrandenburg</option>
# 	<option value="657">Neunkirchen</option>
# 	<option value="249">Neuruppin</option>
# 	<option value="442">Neuss</option>
# 	<option value="172">Nürnberg</option>
# 	<option value="279">Offenbach am Main</option>
# 	<option value="428">Oldenburg (Oldenburg)</option>
# 	<option value="439">Osnabrück</option>
# 	<option value="658">Ottweiler</option>
# 	<option value="543">Paderborn</option>
# 	<option value="146">Passau</option>
# 	<option value="703">Pinneberg</option>
# 	<option value="252">Potsdam</option>
# 	<option value="492">Recklinghausen</option>
# 	<option value="177">Regensburg</option>
# 	<option value="349">Rostock</option>
# 	<option value="659">Saarbrücken</option>
# 	<option value="660">Saarlouis</option>
# 	<option value="553">Schleiden</option>
# 	<option value="207">Schweinfurt</option>
# 	<option value="358">Schwerin</option>
# 	<option value="561">Siegburg</option>
# 	<option value="548">Siegen</option>
# 	<option value="661">St. Ingbert (St Ingbert)</option>
# 	<option value="662">St. Wendel (St Wendel)</option>
# 	<option value="368">Stadthagen</option>
# 	<option value="529">Steinfurt</option>
# 	<option value="691">Stendal</option>
# 	<option value="351">Stralsund</option>
# 	<option value="179">Straubing</option>
# 	<option value="95">Stuttgart</option>
# 	<option value="404">Tostedt</option>
# 	<option value="155">Traunstein</option>
# 	<option value="109">Ulm</option>
# 	<option value="664">Völklingen</option>
# 	<option value="417">Walsrode</option>
# 	<option value="185">Weiden i. d. OPf.</option>
# 	<option value="322">Wetzlar</option>
# 	<option value="335">Wiesbaden</option>
# 	<option value="602">Wittlich</option>
# 	<option value="469">Wuppertal</option>
# 	<option value="211">Würzburg</option>
# 	<option value="618">Zweibrücken</option>
# </select><span class="select2 select2-container select2-container--default" dir="ltr" data-select2-id="3" style="width: 271.5px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-disabled="false" aria-labelledby="select2-searchRegisterFormextendedResearchCircuitId-container"><span class="select2-selection__rendered" id="select2-searchRegisterFormextendedResearchCircuitId-container" role="textbox" aria-readonly="true" title="Registergericht">Registergericht</span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span>
#                                                 </div>
#                                             </div>
#                                             <div class="col-lg-6">
#                                                 <div class="select-wrapper"><select id="searchRegisterForm:extendedResearchRegisterType" name="searchRegisterForm:extendedResearchRegisterType" class="select select2-hidden-accessible" size="1" data-select2-id="searchRegisterForm:extendedResearchRegisterType" tabindex="-1" aria-hidden="true">	<option value="0" data-select2-id="6">Registerart</option>
# 	<option value="4">Genossenschafts­register</option>
# 	<option value="7">Gesellschaftsregister</option>
# 	<option value="1">HRA</option>
# 	<option value="2">HRB</option>
# 	<option value="5">Partnerschafts­register</option>
# </select><span class="select2 select2-container select2-container--default" dir="ltr" data-select2-id="5" style="width: 186.5px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-disabled="false" aria-labelledby="select2-searchRegisterFormextendedResearchRegisterType-container"><span class="select2-selection__rendered" id="select2-searchRegisterFormextendedResearchRegisterType-container" role="textbox" aria-readonly="true" title="Registerart">Registerart</span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span>
#                                                 </div>
#                                             </div>
#                                         </div>
#                                     </div>

#                                     <!-- Registernummer -->
#                                     <div class="search-row">
#                                         <div class="col">
#                                             <label class="sr-only input-label" for="searchRegisterForm:extendedResearchRegisterNumber">Registernummer</label><input id="searchRegisterForm:extendedResearchRegisterNumber" type="text" name="searchRegisterForm:extendedResearchRegisterNumber" value="" class="form-control" placeholder="Registernummer">
#                                         </div>
#                                     </div>

#                                     <!-- Bundesl&amp;#228;nder -->
#                                     <div class="search-row">
#                                         <div class="col col-info">
#                                             <div class="accordion" id="federalState" data-toggle="false">
#                                                 <div class="card">
#                                                     <div class="card-header" id="federalState-heading">
#                                                         <h4>
#                                                             <button class="btn btn-link collapsed" type="button" data-toggle="collapse" data-target="#federalState-collapse" aria-expanded="false" aria-controls="federalState-collapse">Bundesländer</button>
#                                                         </h4>
#                                                     </div>
#                                                     <fieldset>
#                                                         <legend class="sr-only">Bundesländer</legend>
#                                                     <div id="federalState-collapse" class="collapse" aria-labelledby="federalState-heading" data-parent="#federalState" style="">
#                                                         <div class="card-body">
#                                                             <div class="row">
#                                                                 <div class="col-lg-6">
#                                                                     <div class="row checkbox-wrapper">
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState1" type="checkbox" name="searchRegisterForm:searchFederalState1" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState1">Baden-Württemberg</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState2" type="checkbox" name="searchRegisterForm:searchFederalState2" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState2">Bayern</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState3" type="checkbox" name="searchRegisterForm:searchFederalState3" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState3">Berlin</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState4" type="checkbox" name="searchRegisterForm:searchFederalState4" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState4">Brandenburg</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState5" type="checkbox" name="searchRegisterForm:searchFederalState5" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState5">Bremen</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState6" type="checkbox" name="searchRegisterForm:searchFederalState6" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState6">Hamburg</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState7" type="checkbox" name="searchRegisterForm:searchFederalState7" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState7">Hessen</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState8" type="checkbox" name="searchRegisterForm:searchFederalState8" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState8">Mecklenburg-Vorpommern</label>
#                                                                             </div>
#                                                                         </div>
#                                                                     </div>
#                                                                 </div>
#                                                                 <div class="col-lg-6">
#                                                                     <div class="row checkbox-wrapper">
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState9" type="checkbox" name="searchRegisterForm:searchFederalState9" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState9">Nieder­sachsen</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState10" type="checkbox" name="searchRegisterForm:searchFederalState10" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState10">Nordrhein-Westfalen</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState11" type="checkbox" name="searchRegisterForm:searchFederalState11" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState11">Rheinland-Pfalz</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState12" type="checkbox" name="searchRegisterForm:searchFederalState12" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState12">Saarland</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState13" type="checkbox" name="searchRegisterForm:searchFederalState13" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState13">Sachsen</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState14" type="checkbox" name="searchRegisterForm:searchFederalState14" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState14">Sachsen-Anhalt</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState15" type="checkbox" name="searchRegisterForm:searchFederalState15" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState15">Schleswig-Holstein</label>
#                                                                             </div>
#                                                                         </div>
#                                                                         <div class="col-12">
#                                                                             <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchFederalState16" type="checkbox" name="searchRegisterForm:searchFederalState16" class="custom-control-input">                                                                                
#                                                                                 <label class="custom-control-label" for="searchRegisterForm:searchFederalState16">Thüringen</label>
#                                                                             </div>
#                                                                         </div>
#                                                                     </div>
#                                                                 </div>
#                                                             </div>
#                                                         </div>
#                                                     </div>
#                                                     </fieldset>
#                                                 </div>
#                                             </div>
#                                             <!-- Input Info: BEGIN --><a href="njs_help/search1.1.html;jsessionid=EF645278890089C83D7D7DEACD3FABBF.web04-1" target="_blank" class="btn btn-tooltip" data-target="#modalBundeslaender" data-toggle="modal" aria-label="mehr über Firmenname"><span class="icon-info-circle-solid"></span></a>
#                                             <div class="modal fade" id="modalBundeslaender" tabindex="-1" role="dialog" aria-hidden="true">
#                                                 <div class="modal-dialog" role="document">
#                                                     <div class="modal-content">
#                                                         <div class="modal-header">
#                                                             <h5 class="modal-title">Bundesländer</h5>
#                                                             <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">×</span></button>
#                                                         </div>
#                                                         <div class="modal-body">
#                                                             <p>Thema Zweigniederlassungen: Bei der Firmen-Suche können Zweigniederlassungen nur eingeschränkt über das Bundesland, in dem die Zweigniederlassung ihren Sitz hat, gefunden werden. Führen Sie deshalb die Suche nach Zweigniederlassungen ohne Einschränkung auf das Bundesland der Zweigniederlassung durch. Weitere Hinweise zur Suche nach Zweigniederlassungen finden sie unter&nbsp;<a href="howto1.2.html;jsessionid=EF645278890089C83D7D7DEACD3FABBF.web04-1" role="menuitem">"So geht's / Suchen"</a>.</p>
#                                                         </div>
#                                                     </div>
#                                                 </div>
#                                             </div>
#                                             <!-- Input Info: END -->
#                                         </div>
#                                     </div>

#                                     <!-- Checkbox filter -->
#                                     <div class="search-row">
#                                         <div class="row checkbox-wrapper">
#                                             <div class="col-lg-6">
#                                                 <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchDeleted" type="checkbox" name="searchRegisterForm:searchDeleted" class="custom-control-input">                                                                 
#                                                     <label class="custom-control-label" for="searchRegisterForm:searchDeleted">Auch gelöschte Firmen finden</label>
#                                                 </div>
#                                             </div>
#                                             <div class="col-lg-6">
#                                                 <div class="custom-control custom-checkbox"><input id="searchRegisterForm:searchWithoutBranches" type="checkbox" name="searchRegisterForm:searchWithoutBranches" class="custom-control-input">                                                                 
#                                                     <label class="custom-control-label" for="searchRegisterForm:searchWithoutBranches">Zweigniederlassungen ausblenden</label>
#                                                 </div>
#                                             </div>
#                                         </div>
#                                     </div>

#                                     <!-- Ver&amp;#246;ffentlichungsdaten -->
#                                     <div class="search-row headline">
#                                         <div class="col">
#                                             <h2>Veröffentlichungsdaten</h2>
#                                         </div>
#                                     </div>

#                                     <!-- Sprache -->
#                                     <div class="search-row">
#                                         <div class="col">
#                                             <div class="select-wrapper"><select id="searchRegisterForm:extendedResearchLanguage" name="searchRegisterForm:extendedResearchLanguage" class="select select2-hidden-accessible" size="1" aria-label="Sprache" data-select2-id="searchRegisterForm:extendedResearchLanguage" tabindex="-1" aria-hidden="true">	<option value="0" data-select2-id="8">Sprache</option>
# 	<option value="bg">Bulgarisch</option>
# 	<option value="de">Deutsch</option>
# 	<option value="da">Dänisch</option>
# 	<option value="et">Estnisch</option>
# 	<option value="en">Englisch</option>
# 	<option value="fi">Finnisch</option>
# 	<option value="fr">Französisch</option>
# 	<option value="el">Griechisch</option>
# 	<option value="ga">Irisch</option>
# 	<option value="is">Isländisch</option>
# 	<option value="it">Italienisch</option>
# 	<option value="hr">Kroatisch</option>
# 	<option value="lv">Lettisch</option>
# 	<option value="lt">Litauisch</option>
# 	<option value="mt">Maltesisch</option>
# 	<option value="nl">Niederländisch</option>
# 	<option value="no">Norwegisch</option>
# 	<option value="pl">Polnisch</option>
# 	<option value="pt">Portugiesisch</option>
# 	<option value="ro">Rumänisch</option>
# 	<option value="sv">Schwedisch</option>
# 	<option value="sk">Slowakisch</option>
# 	<option value="sl">Slowenisch</option>
# 	<option value="es">Spanisch</option>
# 	<option value="cs">Tschechisch</option>
# 	<option value="hu">Ungarisch</option>
# </select><span class="select2 select2-container select2-container--default" dir="ltr" data-select2-id="7" style="width: 120px;"><span class="selection"><span class="select2-selection select2-selection--single" role="combobox" aria-haspopup="true" aria-expanded="false" tabindex="0" aria-disabled="false" aria-labelledby="select2-searchRegisterFormextendedResearchLanguage-container"><span class="select2-selection__rendered" id="select2-searchRegisterFormextendedResearchLanguage-container" role="textbox" aria-readonly="true" title="Sprache">Sprache</span><span class="select2-selection__arrow" role="presentation"><b role="presentation"></b></span></span></span><span class="dropdown-wrapper" aria-hidden="true"></span></span>
#                                             </div>
#                                         </div>
#                                     </div>

#                                     <!-- Datepicker -->
#                                     <div class="search-row datepicker">
#                                         <div class="row">
#                                             <div class="col-lg-4">
#                                                 <p class="label">Veröffentlichungszeitraum</p>
#                                             </div>
#                                             <div class="col-md-6 col-lg-4">
#                                                 <div class="form-group">
#                                                     <div class="input-group date" id="date-from">
#                                                         <label class="sr-only input-label" for="searchRegisterForm:extendedResearchStartDate">von</label>
#                                                         <div class="input-group-prepend">
#                                                             <span class="input-group-text">von</span>
#                                                         </div><input id="searchRegisterForm:extendedResearchStartDate" type="text" name="searchRegisterForm:extendedResearchStartDate" value="30.11.0002" class="form-control" placeholder="tt.mm.jjjj">
#                                                         <span class="input-group-addon">
#                                                             <span class="fa fa-calendar-alt"></span>
#                                                         </span>
#                                                     </div>
#                                                 </div>
#                                             </div>
#                                             <div class="col-md-6 col-lg-4">
#                                                 <div class="form-group">
#                                                     <div class="input-group date" id="date-to">
#                                                         <label class="sr-only input-label" for="searchRegisterForm:extendedResearchEndDate">bis</label>
#                                                         <div class="input-group-prepend">
#                                                             <span class="input-group-text">bis</span>
#                                                         </div><input id="searchRegisterForm:extendedResearchEndDate" type="text" name="searchRegisterForm:extendedResearchEndDate" value="30.11.0002" class="form-control" placeholder="tt.mm.jjjj">
#                                                         <span class="input-group-addon">
#                                                             <span class="fa fa-calendar-alt"></span>
#                                                         </span>
#                                                     </div>
#                                                 </div>
#                                             </div>
#                                         </div>
#                                     </div><input id="searchRegisterForm:justADummyForValidation" type="checkbox" name="searchRegisterForm:justADummyForValidation" style="display: none">                                                                 

#                                     <!-- Submit -->
#                                     <div class="search-row submit">
#                                         <input type="hidden" name="submitaction" value="searchExtendedResearch"><input type="submit" name="searchRegisterForm:j_idt329" value="Suchen" class="btn btn-green">
#                                     </div><input type="hidden" name="javax.faces.ViewState" id="j_id1:javax.faces.ViewState:1" value="-1000911380972201158:5933084940885845771" autocomplete="off">
# </form>