#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 02:10:06 2019

@author: gurdit.chahal
"""

#get dictonairy of drug names +urls to individual pages
import urllib.request
medline_url="https://medlineplus.gov/druginfo/herb_All.html"
#access url page for drugs
page=urllib.request.urlopen(medline_url)
import re
import pandas as pd

from bs4 import BeautifulSoup
soup=BeautifulSoup(page)
#print(soup.prettify())

#extract everything between <a href= and >
web_pattern="(?<=<a href=)(.*?)>"
#grab everything between > and <
name_pattern="(?<=>)[^<]*"

#get all lines
lines=soup.find_all('li')
#initialize variables
drug_dict={}
url='unknown'
drug='unknown'
store_flag=False

#within lines look for website references
for line in lines:
    ref=str(line.find('a'))
    html=re.search(web_pattern,ref)
    if html:
        url=html.group(1).replace('"',"")
        #append https body to websites starting only with natural
        if url.startswith('natural'):
            url='https://medlineplus.gov/druginfo/'+url
            
    drug_name=re.search(name_pattern,ref)
  
    #only keep valid websites
    if url.startswith('https'):
        store_flag=True
    else:
        store_flag=False
    if bool(drug_name)&(store_flag):
        drug=drug_name.group()
    url=url.replace(' target=_blank','')
    drug_dict[drug]=url
#print(drug_dict)


#NaturalMedicines DB Scrape example from page
#case 1:directly medline
drug_url='https://medlineplus.gov/druginfo/natural/833.html'

drug_page=urllib.request.urlopen(drug_url)

drug_soup=BeautifulSoup(drug_page)

article=drug_soup.find('article')

article_text=str(article)



## NIH related herbs scrape
drug_info=[]
# Loop through drug dict looking for URL's with nccih
# Build list of drugs and page contents from the associated URL
for d in drug_dict.items():
    if d[1][8:13] == 'nccih':
        drug_url2=d[1]
        drug_page2=urllib.request.urlopen(drug_url2)
        drug_soup2=BeautifulSoup(drug_page2)
        main_content2=str(drug_soup2.find_all('li'))
        drug_info.append([d[0],main_content2])
        #print(d[0])




#convert to data frame and export to csv
df = pd.DataFrame(drug_info, columns =['Herb', 'Info']) 
df.to_csv ('./medline_nih_1.csv', index = None, header=True) 

