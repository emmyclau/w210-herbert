#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 13:43:34 2019

@author: gurdit.chahal
"""
exec(open('medline_scrape.py').read())

meds=list(drug_dict.keys())[6:181]

import wikipedia
import urllib.request
import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from collections import defaultdict
import json

def get_toc(html,name_find=False,name_pattern="(?<=>)[^<]*"):
    soup=bs(html)
    toc=soup.find_all(class_="toctext",text=True)
    names=[]
    if name_find:
        for content in toc:
            names.append(re.search(name_pattern,content))  
    else:
        for content in toc:
            names.append(content.text)  
    return names

def get_ref(wiki_page,filter_pattern=False):
    try:
        ref_list=wiki_page.references
    except KeyError:
        ref_list=[]
    sub_ref=[]
    if filter_pattern:
        for ref in ref_list:
                if re.search(filter_pattern,ref):
                    sub_ref.append(ref)
        return sub_ref
    return ref_list

def get_links(wiki_page,filter_pattern=False):
    try:
        link_list=wiki_page.links
    except KeyError:
        link_list=[]
    sub_link=[]
    if filter_pattern:
        for ref in link_list:
                if re.search(filter_pattern,link):
                    sub_link.append(link)
        return sub_link
    return link_list

res = requests.get("https://en.wikipedia.org/wiki/Category:Plants_used_in_traditional_Chinese_medicine")
soup = bs(res.text, "html.parser")
plants = {}
for link in soup.find_all("a"):
    url = link.get("href", "")
    if "/wiki/" in url:
        plants[link.text.strip()] = url
plants=list(plants.keys())[7:202]

superset=list(set(plants).union(set(meds)))

herb_dict=defaultdict(lambda:'not_captured')

for s in superset:
      valid_wiki=True
      try:
          wikipage=wikipedia.page(s)
      except wikipedia.DisambiguationError as e:
          known_page=e.options[0]
          wikipage=wikipedia.WikipediaPage(known_page)
      except wikipedia.PageError as p:
          search_result=wikipedia.search(s)
          if search_result:
              wikipage=wikipedia.page(search_result[0])
          else:
              valid_wiki=False
      if valid_wiki:
          info_captured=defaultdict(lambda:'not_captured')
          
          info_captured['table_of_contents']=get_toc(wikipage.html())
          info_captured['links']=get_links(wikipage)
          info_captured['references']=get_ref(wikipage,filter_pattern='pubmed')
          info_captured['summary']=wikipage.summary
          info_captured['content']=wikipage.content
          info_captured['related_pages']=wikipedia.search(s)
          print('captured ',s)
          herb_dict[s]=info_captured
    

with open('wiki_herbs.json', 'w') as fp:
    json.dump(herb_dict, fp)        
    
table_cols = [[] for i in range(3)]
fifty_fundamental=res = requests.get("https://en.wikipedia.org/wiki/Chinese_herbology")
soup = bs(res.text, "html.parser")

table=soup.find("table",class_="wikitable")
rows=table.find_all('tr')
for row in rows[1:]:
    cells=row.find_all('td')
    for i in range(len(table_cols)):
        table_cols[i].append(cells[i].find(text=True))
table_records=list(zip(table_cols[0],table_cols[1],table_cols[2])) 

ff_dict=defaultdict(lambda:'not_captured')
df_ff=pd.DataFrame.from_records(table_records,columns=rows[0].text.strip('\n').split('\n\n'))    
for name in df_ff['Binomial nomenclature']:
     valid_wiki=True
     try:
          wikipage=wikipedia.page(name)
     except wikipedia.DisambiguationError as e:
          known_page=e.options[0]
          wikipage=wikipedia.WikipediaPage(known_page)
     except wikipedia.PageError as p:
          search_result=wikipedia.search(name)
          if search_result:
              wikipage=wikipedia.page(search_result[0])
          else:
              valid_wiki=False
     if valid_wiki:
          info_captured=defaultdict(lambda:'not_captured')
          
          info_captured['table_of_contents']=get_toc(wikipage.html())
          info_captured['links']=get_links(wikipage)
          info_captured['references']=get_ref(wikipage)
          info_captured['summary']=wikipage.summary
          info_captured['content']=wikipage.content
          info_captured['related_pages']=wikipedia.search(name)
          print('captured ',name)
          ff_dict[name]=info_captured
    

'''plants=wikipedia.WikipediaPage("Category:Plants used in traditional Chinese medicine")
ginseng=wikipedia.WikipediaPage("ginseng")


dir(ginseng)
text=ginseng.content
refs=ginseng.references
relations=ginseng.links
ginseng.categories
ginseng.url

page=urllib.request.urlopen(ginseng.url)
soup=bs(page)
topics_covered=soup.find_all(class_='toctext',text=True)
name_pattern="(?<=>)[^<]*"'''





