#!/usr/bin/python

import os
import json
import pandas as pd
import numpy as np
import argparse
import matplotlib.pyplot as plt
from tqdm import tqdm

parser = argparse.ArgumentParser()
parser.add_argument('--domain', type=str, default='animals')
parser.add_argument('--top', type=int, default=20)
args = parser.parse_args()


domain = args.domain
with open('data/domains/'+domain+'_page_titles.json', 'r') as load:
	pages_name = json.load(load)

top_num = args.top  # Number of retrieved top frequent sections
count = 0
count_miss = 0
sections_content = {}
sections_num = []
reference_num = []
reference_5prop_num = []
scraping_time = []
info = pd.DataFrame(columns=['data', 'value'])
for page in tqdm(pages_name):
	try:
		load = open('data/domains/'+domain+'/'+page+'.json')
	except:
		count_miss += 1
	else:
		entry = json.load(load)
		count += 1
		
	sections_num.append(entry['No. of sections'])
	reference_num.append(entry['No. of references'])
	reference_5prop_num.append(entry['Prop of references with gt 5 paras'])
	scraping_time.append(entry['Scraping Time'])
	
	sections = list(entry['Sections'].values())
	for sec in sections:
		if sec not in sections_content.keys():
			sections_content[sec] = 1
		else:
			sections_content[sec] += 1
	temp = pd.DataFrame(sections_content.items(), columns = ['section', 'number'])
	temp = temp.sort_values(by = ['number'], ascending = False)[:top_num]
	temp.to_csv(domain+'_top'+str(top_num)+'_sections.csv')
	
info.loc[0] = {'data':'avg_secton_num', 'value':int(np.mean(sections_num))}
info.loc[1] = {'data':'avg_reference_num', 'value':int(np.mean(reference_num))}
info.loc[2] = {'data':'avg_reference_5prop_num', 'value':np.mean(reference_5prop_num)}
info.loc[4] = {'data':'mid_secton_num', 'value':int(np.median(sections_num))}
info.loc[5] = {'data':'mid_reference_num', 'value':int(np.median(reference_num))}
info.loc[6] = {'data':'mid_reference_5prop_num', 'value':np.median(reference_5prop_num)}
info.loc[3] = {'data':'scraping_time', 'value':np.mean(scraping_time)}
info.to_csv(domain+'_info.csv')

print('{} pages can not be found!'.format(count_miss))