import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import urllib.request
import json
import time


def get_page_json(page_title, domain, lang):
    start_time = time.perf_counter()
    sections_query = "https://{}.wikipedia.org/w/api.php?action=parse&page=".format(lang) + page_title.title() + "&format=json&prop=sections"
    references_query = "https://{}.wikipedia.org/w/api.php?action=parse&page=".format(lang) + page_title.title() + "&format=json&prop=externallinks"
    text_query = "https://{}.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&titles=".format(lang) + page_title.title() + "&format=json&exsectionformat=wiki"
    keys = ['Sections','Text','References']
    result = {key: None for key in keys}

    with urllib.request.urlopen(sections_query) as url:
        sections_data = json.loads(url.read().decode())['parse']['sections']
    
    with urllib.request.urlopen(references_query) as url:
        references_data = json.loads(url.read().decode())['parse']['externallinks']
    
    with urllib.request.urlopen(text_query) as url:
        text_data = json.loads(url.read().decode())['query']['pages']
        text_data = text_data[next(iter(text_data))]['extract']
    
    sections_title = ["main"]
    sections_values = []
    sections_value, text_data = text_data.split("== "+ sections_data[0]['line'] + " ==")
    sections_values.append(sections_value)
    for ind, value in enumerate(sections_data):
        if ind == len(sections_data) - 2:
            break
        header = int(sections_data[ind+1]['level'])*'='
        sections_value, text_data = text_data.split(header + " " + sections_data[ind+1]['line'] + " " + header)
        sections_title.append(sections_data[ind]['line'])
        sections_values.append(sections_value)

    sections_count = [ i for i in range(len(sections_title)) ]

    result['Sections'] = dict(zip(sections_count, sections_title))
    result['Text'] = dict(zip(sections_count, sections_values))
    result['No. of sections'] = len(sections_title)

    archived_references_data = []
    for data in references_data:
        if "https://web.archive.org/web/" in data:
            archived_references_data.append(data)
    
    references_data_text = []
    ref_count = 0
    mostly_paras = 0
    for archived_url in archived_references_data:
        http_request = requests.get(archived_url).text
        soup = BeautifulSoup(http_request, 'html.parser').findAll('p')
        if soup:
            ref_count += 1
            ref_text = ""
            if len(soup) >= 5:
                mostly_paras += 1
            for tag in soup:
                # Match only those paras with that contain the page title
                # Assumption here would be that every para about the page title
                # should ideally mention the page title atleast once. 
                if page_title.lower() in tag.getText().lower():
                    ref_text = ref_text + tag.getText()
            references_data_text.append(ref_text)

    result['References'] = references_data_text
    result['No. of references'] = ref_count
    result['Prop of references with gt 10 paras'] = mostly_paras/ref_count
    end_time = time.perf_counter() - start_time
    result['Scraping Time'] = end_time

    print(page_title)
    print(mostly_paras/ref_count)

    with open('data/domains/'+domain+'/'+page_title+'.json', 'w') as fp:
        json.dump(result, fp)


def get_qids(domain):
    domain_csv = pd.read_csv("data/qid/"+domain+".csv")
    qids = domain_csv.iloc[:,0].str.split("http://www.wikidata.org/entity/")
    qids = [i[1] for i in qids]
    return qids


def get_page_titles(qids,lang):
    page_titles = []
    query = "https://www.wikidata.org/w/api.php?"
    wiki = "{}wiki".format(lang)
    for qid in qids:
        params = {"action":"wbgetentities","props":"sitelinks","ids":qid,"sitefilter":wiki, "format":"json"}
        r = requests.get(url = query, params = params)
        response = r.json()
        if 'sitelinks' in response['entities'][qid]:
            if wiki in response['entities'][qid]['sitelinks']:
                page_titles.append(response['entities'][qid]['sitelinks'][wiki]['title'])
            else:
                print(response['entities'][qid]['sitelinks'])


if __name__ == '__main__':
    domain = 'animals'
    lang = 'en'
    qids = get_qids(domain)
    page_titles = get_page_titles(qids, lang)
    print(len(page_titles))
    print(page_titles[:10])
    #for page_title in page_titles:
        #get_page_json(page_title, domain, lang)