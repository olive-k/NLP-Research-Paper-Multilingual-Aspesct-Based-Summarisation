import requests
from bs4 import BeautifulSoup
import urllib.request
import time

def start():
    url = 'http://www.oxforddnb.com/view/article/29738'
    page_title = 'Drona'
    http_request = requests.get(url, timeout = 5.0).text
    print('here')
    soup = BeautifulSoup(http_request, 'html.parser').findAll('p')
    if soup:
        ref_text = ""
        for tag in soup:
            print(tag)
            # Match only those paras with that contain the page title
            # Assumption here would be that every para about the page title
            # should ideally mention the page title atleast once. 
            if page_title.lower() in tag.getText().lower():
                ref_text = ref_text + tag.getText()
        


if __name__ == '__main__':
    start()