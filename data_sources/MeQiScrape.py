#!/usr/bin/env python
# coding: utf-8

# In[1]:

import urllib
import urlparse
import urllib.request
import urllib.parse
from PIL import Image
# url="https://www.meandqi.com/herb-database?page=14"
#access url page for drugs
# page=urllib.request.urlopen(url)
import re
import pandas as pd

from bs4 import BeautifulSoup
#soup=BeautifulSoup(page)

def urlEncodeNonAscii(b):
    return re.sub('[\x80-\xFF]', lambda c: '%%%02x' % ord(c.group(0)), b)

def iriToUri(iri):
    parts= urlparse.urlparse(iri)
    return urlparse.urlunparse(
        part.encode('idna') if parti==1 else urlEncodeNonAscii(part.encode('utf-8'))
        for parti, part in enumerate(parts)
    )

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


# Split Herb name into Western name and Chinese name
drug_info=[]
url_dict={}
for key,value in drug_dict.items():
    # Get herb name and its chinese name
    two_names =(key.split('('))
    herb = two_names[0].rstrip()
    chinese_name = two_names[1].rstrip().replace(")", "")
    url=value
    url_dict[herb]=url

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
    drug_info.append([herb,chinese_name,drug_conditions,url])
    print(herb)


# In[39]:


df = pd.DataFrame(drug_info, columns =['herb', 'chinese_name','conditions','url']) 
df
df.to_csv ('./meAndQi.csv', index =None, header=True) 
print(df)

# In[40]:

#images
meqi=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/meAndQi.csv')

images = {}
for row in meqi.itertuples(index=True, name='Pandas'):
    
    herb=getattr(row,'herb')
    url=getattr(row,'Url')

    html_page = urllib.request.urlopen(url)
    soup = BeautifulSoup(html_page)
    
    for img in soup.findAll('img'):
        caption=img.get('alt')
        caption_words=[s.lower() for s in caption.split()]
        if herb.split()[0].lower() in caption_words:
        #images.append(img.get('src'))
            images[caption]='https://www.meandqi.com/'+img.get('src')
# In[41]:
qi_images=pd.DataFrame.from_dict(images,orient='index') 
qi_images['caption']=qi_images.index
qi_images.columns=['Url','Caption']   
qi_images.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/qi_images.csv')   

for row in qi_images.itertuples(index=True, name='Pandas'):
    title='_'.join(getattr(row,'Caption').split())
    url=getattr(row,'Url')
    url = urllib.parse.urlsplit(url)
    url = list(url)
    url[2] = urllib.parse.quote(url[2])
    url = urllib.parse.urlunsplit(url)
    path="/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/images/"+title
    urllib.request.urlretrieve(url,path+".webp")
    print(url)
    im = Image.open(path+".webp").convert("RGB")
    im.save(path+".jpg","jpeg")
    print(path+".jpg")
    