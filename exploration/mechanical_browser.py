import json
import re
import mechanicalsoup
import requests
import os
import xml.etree.ElementTree as ET
from PIL import Image, ImageSequence


def search_companies(name):
    browser = mechanicalsoup.StatefulBrowser(user_agent='Chrome')
    browser.open("https://www.unternehmensregister.de/ureg/index.html")

    url = browser.page.select("ul.service__list li a")[0].attrs["href"]
    session_id = url.split(";")[1].split("?")[0]

    # Fill-in the search form
    browser.select_form('#globalSearchForm')
    browser["globalSearchForm:extendedResearchCompanyName"] = name
    browser["submitaction"] = "searchRegisterData"
    browser.submit_selected(btnName="globalSearchForm:btnExecuteSearchOld")

    browser.open_relative(browser.page.select("div.right a")[0].attrs["href"])

    # Display the results
    companies = []
    i = 0
    si = browser.page.select(".reglink[id*='SI']")
    for result in browser.page.select('td.RegPortErg_FirmaKopf'):
        company = result.text
        companies += [(company, i,
                       "https://www.unternehmensregister.de/ureg/registerPortal.html;{}{}".format(session_id,
                                                                                                  si[i].attrs["href"]))]
        i += 1
    return companies, session_id


def add_si_to_cart(browser, si_link):
    # Pull Overview
    browser.open(si_link)


def add_gs_to_cart(browser, session_id, index):
    # Open document tree
    browser.open(
        "https://www.unternehmensregister.de/ureg/registerPortal.html;{}?submitaction=showDkTree&searchIdx={}".format(
            session_id, index))

    # Expand
    level = 2

    while True:
        elements = browser.page.select("div.dktree-container.level-{} span a".format(level))
        if len(elements) == 0:
            raise Exception("no gs list found")
        if level == 3:
            element = list(filter(lambda x: x.text == "Liste der Gesellschafter", elements))
            if len(element) == 0:
                raise Exception("no gs list found")
            browser.open_relative(element[0].attrs["href"])
            level += 1
            continue
        if "Liste der" not in elements[0].text:
            browser.open_relative(elements[0].attrs["href"])
            level += 1
        else:
            browser.open_relative(elements[0].attrs["href"])
            level += 1
            break

    file_format = [x.attrs["value"] for x in browser.page.select("input#format_orig")][0]

    date = browser.page.select("div>table.file-info-table tbody tr:nth-of-type(2) td:nth-of-type(2)")[
        0].text.strip().replace("\n", "")
    date_2 = browser.page.select("div>table.file-info-table tbody tr:nth-of-type(4) td:nth-of-type(2)")[
        0].text.strip().replace("\n", "")
    if date == "unbekannt":
        date = date_2

    browser.select_form("#dkform")
    browser["format"] = file_format
    browser.submit_selected("add2cart")

    return date


async def pull_gs(name, index, si_link, session_id, db):
    # Connect to UReg
    browser = mechanicalsoup.StatefulBrowser(user_agent='Chrome')

    has_si = True
    try:
        add_si_to_cart(browser, si_link)
    except Exception as e:
        print(e)
        has_si = False

    has_gs = True
    date = ""
    try:
        date = add_gs_to_cart(browser, session_id, index)
    except Exception as e:
        print(e)
        has_gs = False

    if not (has_gs or has_si):
        raise Exception("no data found")

    # Go to cart
    browser.open_relative("doccart.html;{}".format(session_id))
    browser.select_form("#doccartForm")

    submit_name = browser.page.select("div.right input")[0].attrs["name"]
    browser.submit_selected(submit_name)

    browser.select_form("#paymentFormOverview")
    browser.submit_selected("paymentFormOverview:btnNext")

    browser.open_relative("doccart.html;{}".format(session_id))

    downloads = [x.attrs["href"] for x in browser.page.select("div.download-wrapper div a:not(.disabled)")]

    if len(downloads) == 0:
        raise Exception("no downloads found")

    gs_list = ""
    si = ""
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
            fname = "GS-Liste-{}-{}.{}".format(name, date, file_format)
            filename = "out/{}/{}".format(name, fname)
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
            filename = "out/{}/{}".format(name, fname)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(r.content)
            si = filename
        else:
            fname = "GS-Liste-{}-{}.{}".format(name, date, file_format)
            filename = "out/{}/{}".format(name, fname)
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            with open(filename, 'wb') as f:
                f.write(r.content)
            gs_list = filename

    if not si == "" and not has_gs:
        # Parse SI
        e = ET.parse(si)
        bet = e.findall("./{http://www.xjustiz.de}Grunddaten//{http://www.xjustiz.de}Beteiligung")

        rechtsform = ""
        for beteiligung in bet:
            t = beteiligung.find(".//{http://www.xjustiz.de}Rollenbezeichnung/{http://www.xjustiz.de}content").text
            if t == "Rechtsträger":
                rechtsform = beteiligung.find(
                    ".//{http://www.xjustiz.de}Rechtsform/{http://www.xjustiz.de}content").text

        if rechtsform == "":
            raise Exception("unknown rechtsform")

        if rechtsform == "Kommanditgesellschaft":
            kommanditisten = []
            haftender = []
            for beteiligung in bet:
                t = beteiligung.find(".//{http://www.xjustiz.de}Rollenbezeichnung/{http://www.xjustiz.de}content").text
                if "kommanditist" in t.lower():
                    kommanditist = {}
                    if beteiligung.find(
                            ".//{http://www.xjustiz.de}Beteiligter/{http://www.xjustiz.de}Natuerliche_Person"):
                        kommanditist["name"] = beteiligung.find(".//{http://www.xjustiz.de}Vorname").text.strip()
                        kommanditist["surname"] = beteiligung.find(".//{http://www.xjustiz.de}Nachname").text.strip()
                        kommanditist["place"] = (
                                beteiligung.find(".//{http://www.xjustiz.de}Ort").text or "unbekannt").strip()
                    elif beteiligung.find(".//{http://www.xjustiz.de}Beteiligter/{http://www.xjustiz.de}Organisation"):
                        kommanditist["company"] = beteiligung.find(
                            ".//{http://www.xjustiz.de}Bezeichnung_Aktuell").text.strip()
                        kommanditist["place"] = beteiligung.find(".//{http://www.xjustiz.de}Ort").text.strip()
                    kommanditisten.append(kommanditist)

                elif "persönlich haftende" in t.lower():
                    haftender_gesellschafter = {}
                    if beteiligung.find(
                            ".//{http://www.xjustiz.de}Beteiligter/{http://www.xjustiz.de}Natuerliche_Person"):
                        haftender_gesellschafter["name"] = beteiligung.find(
                            ".//{http://www.xjustiz.de}Vorname").text.strip()
                        haftender_gesellschafter["surname"] = beteiligung.find(
                            ".//{http://www.xjustiz.de}Nachname").text.strip()
                        haftender_gesellschafter["ort"] = (
                                beteiligung.find(".//{http://www.xjustiz.de}Ort").text or "unbekannt").strip()
                    elif beteiligung.find(".//{http://www.xjustiz.de}Beteiligter/{http://www.xjustiz.de}Organisation"):
                        haftender_gesellschafter["bezeichnung"] = beteiligung.find(
                            ".//{http://www.xjustiz.de}Bezeichnung_Aktuell").text.strip()
                        haftender_gesellschafter["ort"] = beteiligung.find(".//{http://www.xjustiz.de}Ort").text.strip()
                    haftender.append(haftender_gesellschafter)
            return {"type": "partnership", "value": {
                "partners": kommanditisten,
                "liable_parties": haftender
            }}

        elif "Aktien" in rechtsform:
            return {"type": "ag"}
        else:
            raise Exception("not found")
    elif gs_list != "":
        dl_id = uuid.uuid4()
        db["dl-{}".format(dl_id)] = gs_list
        return {"type": "corporation", "value": {
            "shareholder_list": dl_id
        }
                }
    else:
        raise Exception("not found")

    return gs_list


from flask import Flask, request, jsonify, g, abort, send_file
import dbm
import uuid
from functools import wraps

app = Flask(__name__)
DATABASE = 'kvstore.db'

# Define your authentication token
AUTH_TOKEN = 'boah_mann_ist_diese_api_gut_abgesichert'


def require_auth_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Check if the Authorization header is present
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            abort(401, 'Authentication required')

        # Extract the token from the header
        token = auth_header.replace('Bearer ', '')

        # Check if the token is valid
        if token != AUTH_TOKEN:
            abort(401, 'Invalid authentication token')

        # Token is valid, proceed with the request
        return f(*args, **kwargs)

    return decorated


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = dbm.open(DATABASE, 'c')
    return db


@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()


@app.route('/api/search', methods=['GET'])
@require_auth_token
def search_endpoint():
    db = get_db()
    search_query = request.args.get('search')
    results, session_id = search_companies(search_query)

    response = {'query': search_query, 'results': []}
    for r in results:
        id = uuid.uuid4()
        v = {
            "id": id.hex,
            "name": r[0],
            "index": r[1],
            "link": r[2],
            "session_id": session_id
        }
        db[str(id)] = json.dumps(v)
        response["results"].append({
            "id": id,
            "name": r[0]
        })

    return jsonify(response)


@app.route('/api/fetch/<path:id>', methods=['GET'])
@require_auth_token
async def fetch_endpoint(id):
    db = get_db()
    if id not in db:
        abort(404, "unknown company id")
    context = json.loads(db.get(id))
    content = await pull_gs(context["name"], context["index"], context["link"], context["session_id"], db)
    return jsonify({'id': id, 'content': content})

@app.route('/api/download/<path:id>', methods=['GET'])
@require_auth_token
def file_endpoint(id):
    db = get_db()
    key = "dl-{}".format(id)
    if key not in db:
        abort(404, "unknown download id")
    return send_file(db[key].decode(), as_attachment=True)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)