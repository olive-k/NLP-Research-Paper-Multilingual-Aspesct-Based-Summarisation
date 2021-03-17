import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import urllib.request
import json
import time


def remove_tags(raw_html):
    pattern = re.compile('<.*?>')
    removed_text = re.sub(pattern, '', raw_html)
    return removed_text


def remove_parentheses(text):
    return re.sub('[()]', '', text)


def get_page_json(page_title, domain, lang):
    start_time = time.perf_counter()
    sections_query = "https://{}.wikipedia.org/w/api.php?action=parse&page=".format(lang) + page_title + "&format=json&prop=sections"
    sections_query = sections_query.replace(' ', '%20')
    references_query = "https://{}.wikipedia.org/w/api.php?action=parse&page=".format(lang) + page_title + "&format=json&prop=externallinks"
    references_query = references_query.replace(' ', '%20')
    text_query = "https://{}.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&titles=".format(lang) + page_title + "&format=json&exsectionformat=wiki"
    text_query = text_query.replace(' ', '%20')
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
    sections_value, text_data = text_data.split("== "+ remove_tags(sections_data[0]['line']) + " ==")
    sections_values.append(sections_value)
    for ind, value in enumerate(sections_data):
        if ind == len(sections_data) - 2:
            break
        header = int(sections_data[ind+1]['level'])*'='
        sections_value, text_data = text_data.split(header + " " + remove_tags(sections_data[ind+1]['line']) + " " + header)
        sections_title.append(sections_data[ind]['line'])
        sections_values.append(sections_value)

    sections_count = [ i for i in range(len(sections_title)) ]

    result['Sections'] = dict(zip(sections_count, sections_title))
    result['Text'] = dict(zip(sections_count, sections_values))
    result['No. of sections'] = len(sections_title)
    
    '''
    non_archived_references_data = []
    for data in references_data:
        if not ("https://web.archive.org/web/" in data):
            non_archived_references_data.append(data)
    '''

    page_title_tokens = page_title.split()
    
    references_data_text = []
    ref_count = 0
    mostly_paras = 0
    for all_url in references_data:
        try:
            http_request = requests.get(all_url).text
        except Exception:
            continue
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
                if any(remove_parentheses(token.lower()) in tag.getText().lower() for token in page_title_tokens):
                    ref_text = ref_text + tag.getText()
            references_data_text.append(ref_text)

    result['References'] = references_data_text
    result['No. of references'] = ref_count
    try:
        result['Prop of references with gt 5 paras'] = mostly_paras/ref_count
    except ZeroDivisionError:
        result['Prop of references with gt 5 paras'] = -1
    end_time = time.perf_counter() - start_time
    result['Scraping Time'] = end_time

    print('Page:',page_title)
    print('Pages with gt 5 paras', result['Prop of references with gt 5 paras'])
    print('Scraping Time:', end_time)

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
    count = 0
    for qid in qids:
        params = {"action":"wbgetentities","props":"sitelinks","ids":qid,"sitefilter":wiki, "format":"json"}
        r = requests.get(url = query, params = params)
        response = r.json()
        if 'sitelinks' in response['entities'][qid]:
            if wiki in response['entities'][qid]['sitelinks']:
                page_titles.append(response['entities'][qid]['sitelinks'][wiki]['title'])
                print(count)
        count += 1
    return page_titles


def dump_json(filename, data):
    with open(filename, 'w') as fp:
        json.dump(data, fp)


def read_json(filename):
    with open(filename, 'r') as fp:
        data = json.load(fp)
    return data


if __name__ == '__main__':
    domain = 'animals'
    lang = 'en'

    qids = get_qids(domain)
    titles_extraction_start_time = time.perf_counter()
    page_titles = get_page_titles(qids, lang)
    titles_extraction_time = time.perf_counter() - titles_extraction_start_time
    print('Titles extraction Time', titles_extraction_time)
    dump_json('data/domains/animals_page_titles.json', page_titles)
    
    #page_titles = read_json('data/domains/animals_page_titles.json')
    total_pages = len(page_titles)
    page_count = 0
    domain_scraping_start_time = time.perf_counter()
    for page_title in page_titles:
        print('Working on page: ', page_count, '/', total_pages)
        get_page_json(page_title, domain, lang)
        page_count += 1
    print(domain, ' domain successfully scraped!')
    domain_scraping_time = time.perf_counter() - domain_scraping_start_time
    print('Domain Scraping Time', domain_scraping_time)