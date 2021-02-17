import requests
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import re
import urllib.request, json 

def run(page_title,output_filename):
    sections_query = "https://en.wikipedia.org/w/api.php?action=parse&page=" + page_title + "&format=json&prop=sections"
    references_query = "https://en.wikipedia.org/w/api.php?action=parse&page=" + page_title + "&format=json&prop=externallinks"
    text_query = "https://en.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext&titles=" + page_title + "&format=json&exsectionformat=wiki"
    keys = ['Sections','Text','References','Text/Reference']
    result = {key: None for key in keys}

    with urllib.request.urlopen(sections_query) as url:
        sections_data = json.loads(url.read().decode())['parse']['sections']
        print(sections_data)
    
    with urllib.request.urlopen(references_query) as url:
        references_data = json.loads(url.read().decode())['parse']['externallinks']
        print(references_data)
    
    with urllib.request.urlopen(text_query) as url:
        text_data = json.loads(url.read().decode())['query']['pages']
        text_data = text_data[next(iter(text_data))]['extract']
        print(text_data)
    
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

    archived_references_data = []
    for data in references_data:
        if "https://web.archive.org/web/" in data:
            archived_references_data.append(data)
    
    references_data_text = []
    for archived_url in archived_references_data:
        http_request = requests.get(archived_url).text
        if BeautifulSoup(http_request, 'html.parser').findAll('article'):
            soup = BeautifulSoup(http_request, 'html.parser').findAll('article')[0].findChildren()
            ref_text = ""
            for tag in soup:
                if tag.getText():
                    ref_text = ref_text + tag.getText()
            references_data_text.append(ref_text)

    references_count = [ i for i in range(len(archived_references_data)) ]

    result['References'] = dict(zip(references_count, archived_references_data))
    result['Text/Reference'] = dict(zip(references_count, references_data_text))

    with open(output_filename, 'w') as fp:
        json.dump(result, fp)

if __name__ == '__main__':
    run()