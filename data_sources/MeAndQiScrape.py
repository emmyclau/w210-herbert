#!/usr/bin/env python
# coding: utf-8

# In[1]:


import urllib.request
# url="https://www.meandqi.com/herb-database?page=14"
#access url page for drugs
# page=urllib.request.urlopen(url)
import re
import pandas as pd

from bs4 import BeautifulSoup
#soup=BeautifulSoup(page)


# In[2]:


# Build dicitonary of Herb Names and URL's
drug_dict={}

base_url="https://www.meandqi.com/herb-database?page="
y=1
while y < 15:
    page=urllib.request.urlopen(base_url+str(y))
    soup=BeautifulSoup(page)
    for link in soup.find_all('a'): 
        if link.get('title') is not None:
            url_end = (link.get('href'))
            url='https://www.meandqi.com/'+url_end
            drug = link.get('title')
            drug_dict[drug]=url
            print(drug)
    y+=1
   
        
print(drug_dict)


# In[37]:


# Split Herb name into Wester name and Chinese name
drug_info=[]
for key,value in drug_dict.items():
    # Get herb name and its chinese name
    two_names =(key.split('('))
    herb = two_names[0].rstrip()
    chinese_name = two_names[1].rstrip().replace(")", "")
    url=value

    #get each herb's URL to soupify    
    page=urllib.request.urlopen(url)
    soup=BeautifulSoup(page)
       
    #get all conditions by looking through the links and put in a list
    drug_conditions=[]
    for link in soup.find_all(class_="category-tag small-tag"):
        if (link.get('href')[15:24]) == 'condition':
            condition = link.text
            drug_conditions.append(condition)
        
    # Create list of herb name, chinese name and list of drug conditions
    drug_info.append([herb,chinese_name,drug_conditions])
    print(herb)


# In[39]:


df = pd.DataFrame(drug_info, columns =['herb', 'chinese_name','conditions']) 
df
df.to_csv ('./meAndQi.csv', index =None, header=True) 
print(df)

