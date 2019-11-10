#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Oct  2 13:43:34 2019

@author: gurdit.chahal
"""
#exec(open('medline_scrape.py').read())

#meds=list(drug_dict.keys())[6:181]

import wikipedia
import urllib.request
import requests
from bs4 import BeautifulSoup as bs
import re
import pandas as pd
from collections import defaultdict
import json
import os
from flatten_dict import flatten

def get_toc(html,name_find=False,name_pattern="(?<=>)[^<]*",find_subsection=True):
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

#mediawiki version for tables with subsections
def get_toc_mw(wmpage):
    toc=flatten(wmpage.table_of_contents,keep_empty_types=(dict,))
    toc=list(toc.keys()) #list of tuples where order is key,subsection1,subsection of sub1
    return toc

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

def wiki_compile(search_terms,filter_pattern=False,nan_pattern='NAN',filename='file.txt'):
    herb_dict=defaultdict(lambda:'not_captured')
    if filename:
        file=open(filename,"a")
    for s in search_terms:
          valid_wiki=True
          #if search term is NAN then just pass
          if (nan_pattern) and (s==nan_pattern):
                  valid_wiki=False 
          else:
              try:
                  wikipage=wikipedia.page(s)
              except wikipedia.DisambiguationError as e:
                  known_page=e.options[0]
                  try:
                      wikipage=wikipedia.WikipediaPage(known_page)
                  except wikipedia.PageError:
                      valid_wiki=False
              except wikipedia.PageError:
                  search_result=wikipedia.search(s)
                  if search_result:
                      try:
                          wikipage=wikipedia.page(search_result[0])
                      except wikipedia.DisambiguationError as e:
                          known_page=e.options[0]
                          wikipage=wikipedia.WikipediaPage(known_page)
                      except wikipedia.PageError:
                          valid_wiki=False
                  else:
                      valid_wiki=False
          if valid_wiki:
              info_captured=defaultdict(lambda:'not_captured')
              
              info_captured['table_of_contents']=get_toc(wikipage.html())
              info_captured['links']=get_links(wikipage)
              info_captured['references']=get_ref(wikipage,filter_pattern=filter_pattern)
              info_captured['summary']=wikipage.summary
              info_captured['content']=wikipage.content
              info_captured['related_pages']=wikipedia.search(s)
              info_captured['page_url']=wikipage.url
              print('captured ',s) 
              herb_dict[s]=info_captured
              if filename:
                  for key in info_captured.keys():
                      file.write(str(key)+':'+str(info_captured[key])+'|')
                  file.write('\n')
    if filename:
        file.close()              
    return herb_dict

'''res = requests.get('https://en.wikibooks.org/wiki/Traditional_Chinese_Medicine/Usage_Of_Single_Herbs')
soup = bs(res.text, "html.parser")
table=soup.find('table')
ths = table.find_all('th')
headings = [th.text.strip() for th in ths]
with open('traditional_chinese_wikitable.txt', 'w') as fo:
    print('| '.join(headings), file=fo)
    for tr in table.find_all('tr'):
        tds = tr.find_all('td')
        if not tds:
            continue
        print('| '.join([td.text.strip() for td in tds]), file=fo)

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
          info_captured['page_url']=wikipage.url
          print('captured ',s)
          herb_dict[s]=info_captured

df=pd.DataFrame.from_records(herb_dict).transpose() 
df['nlmANDwiki']=  df.index.map(lambda x: x in meds)
df.to_excel('herb_wiki.xlsx')

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
          info_captured['page_url']=wikipage.url
          print('captured ',name)
          ff_dict[name]=info_captured
df_ff2=pd.DataFrame.from_records(ff_dict).transpose()   

df_ffinal=pd.concat([df_ff,df_ff2.reset_index()],axis=1,ignore_index=True)
df_ffinal.columns=['Scientific_Name','Chinese_Name','American_Name','Wiki_Search_Match','Full_Content','InText_Links','Reference_Links','Related_Pages','Summary','Table_Contents']
df_ffinal.to_csv('fifty_fundamental_herbs.csv')

#/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert
sym_herb=pd.read_excel('SymMapHerb.xlsx')
sym_medical=pd.read_excel('SymMapMedicalSymptom.xlsx')
sym_ingredient=pd.read_excel('SymMapIngredient.xlsx')
sym_tcmsymptom=pd.read_excel('SymMapTcmSymptom.xlsx')
sym_target=pd.read_excel('SymMapTarget.xlsx')
sym_disease=pd.read_excel('SymMapDisease.xlsx')

herb_TCMID=pd.read_csv('herb-TCMID.v2.01.txt',sep='\t')
#prescription_TCMID=pd.read_csv('prescription-TCMID.v2.01.txt',sep='\t')
herb_TCMID['English Name']=herb_TCMID['English Name'].fillna('NAN')
herb_TCMID['Latin Name']=herb_TCMID['Latin Name'].fillna('NAN')

english_names=list(herb_TCMID['English Name'].unique())
latin_names=list(herb_TCMID['Latin Name'].unique())
sym_lat=sym_herb['Latin_name'].fillna('NAN').unique()
sym_eng=sym_herb['English_name'].fillna('NAN').unique()
super_duper=list(set(superset).union(set(english_names)).union(set(latin_names)).union(set(sym_lat)).union(set(sym_eng)))

english_dict=wiki_compile(english_names,filename='english_namefile.txt')
latin_dict=wiki_compile(latin_names)



##Block Layout##
content_list=list(set(df['table_of_contents'].sum()))

with open('content.txt', 'w') as filehandle:
    for listitem in content_list:
        filehandle.write('%s\n' % listitem)

filtered_content=[]       
with open('content_filtered.txt','r') as filehandle:
    for line in filehandle:
       filtered_content.append(line) 

filtered_content=[str.lower(herb.strip('\n')) for herb in filtered_content]

top_words=np.asarray(['adverse','interact','warn','effect','side effect','react','toxi','regula','death','pois','allerg','risk','overdose','safe'])'''

def substr_found(full_string,substring):
    if full_string.find(substring)!=-1:
        return True
    else:
        return False
    
def match_subset(array_words,array_substr):
    matched=[]
    for substr in array_substr:
        match_bool=np.asarray(list(map(lambda word: substr_found(word,substr),array_words)))
        try:
            matched.extend(list(array_words[np.where(match_bool)[0]]))
        except TypeError:
            try:
                matched.extend(list(array_words[np.where(match_bool)[0][0]]))
            except IndexError:
                 pass
    if matched:
        return matched
    else:
        return ['NO_MATCH']

def lower_all(array):
    if len(array)>0:
        return np.vectorize(str.lower)(array)
    else:
        return np.asarray(array)

'''df['filtered_toc']=df['table_of_contents'].apply(lambda toc_list:(match_subset(lower_all(toc_list),top_words))) 

df['filtered_toc'].value_counts().head()

       
df['para_blocks']=df.content.apply(lambda page: page.replace('\n\n\n== ','<p>').split('<p>'))
        
para_blocks=df.content.apply(lambda page: page.replace('\n\n\n== ','<p>').split('<p>'))'''

def para_startswith(para,start_list):
    return any([para.startswith(start) for start in start_list])

def match_parastart(array_para,array_starts):
    matched=[]
    match_bool=np.asarray(list(map(lambda para: para_startswith(para,array_starts),array_para)))
    matched.extend(list(array_para[np.where(match_bool)[0]]))
    if matched:
        return matched
    else:
        return ['NO_MATCH']
    
'''df['filtered_para']=df.apply(lambda row:(match_parastart(lower_all(row['para_blocks']),row['filtered_toc'])),axis=1)       
    
#para_blocks.apply(lambda p: [keeper if para_startswith(keeper,['Metabolism']) else 'NM' for keeper in p])
df['filtered_para'].value_counts().head()
df['herb_name']=df.index.values
df['indexed_para']=df.apply(lambda row: ['**'+row['herb_name']+'**'+ para for para in row['filtered_para']],axis=1)

df_trimmed=df[df['filtered_para'].apply(lambda p_list:'NO_MATCH' not in p_list)]

paragraphs=df_trimmed['indexed_para'].sum()

para_dict={}

for para in paragraphs:
    para_dict[para]=para.split('.')
para_dict[list(para_dict.keys())[0]]
df_block=pd.DataFrame.from_dict(para_dict,orient='index').transpose()
df_block=pd.DataFrame.from_dict(para_dict,orient='index')
df_block=df_block.fillna('NO_SENTENCE')

df_block2=df_block.reset_index()
melted_df=pd.melt(df_block2,id_vars='index')
melted_df=melted_df.sort_values(by='index')
melted_df.to_excel('block_text.xlsx')'''



###herb names#####
def wiki_search(search_term,filter_pattern=False,nan_pattern='NAN'):
          valid_wiki=True
          #if search term is NAN then just pass
          if (nan_pattern) and (search_term==nan_pattern):
                  valid_wiki=False 
          else:
              try:
                  wikipage=wikipedia.page(search_term)
              except wikipedia.DisambiguationError as e:
                  known_page=e.options[0]
                  try:
                      wikipage=wikipedia.WikipediaPage(known_page)
                  except wikipedia.PageError:
                      valid_wiki=False
              except wikipedia.PageError:
                  search_result=wikipedia.search(search_term)
                  if search_result:
                      try:
                          wikipage=wikipedia.page(search_result[0])
                      except wikipedia.DisambiguationError as e:
                          known_page=e.options[0]
                          wikipage=wikipedia.WikipediaPage(known_page)
                      except wikipedia.PageError:
                          valid_wiki=False
                  else:
                      valid_wiki=False
          if valid_wiki:
                  return wikipage
#ginseng=wiki_search('ginseng')

#desired_words=['name','synonym','taxonomy','genus','species','common name','other name','also called']

def grab_wiki_sections(wikipage,desired_words,identifier=None):
    section_dict=defaultdict(lambda:'not_captured')
    if wikipage:
        table_of_contents=get_toc(wikipage.html())
        toc_list=match_subset(lower_all(table_of_contents),desired_words)
        if not(identifier):
            identifier=wikipage.title
        for topic in toc_list:
               if wikipage.section(topic.capitalize()):
                   topic_text=wikipage.section(topic.capitalize())
               elif wikipage.section(topic.title()):
                   topic_text=wikipage.section(topic.title())
               else:
                   topic_text=False
               if topic_text:
                   section_dict[(identifier,topic)]={topic:topic_text,'toc':table_of_contents}
               elif (not topic_text) and (table_of_contents):
                   section_dict[(identifier,"no topic")]={topic:"no topic",'toc':table_of_contents}
               else:
                   continue
    return section_dict

def wiki_topic_text(wikipage,topic):
    if isinstance(topic,str):
        try:
            return wikipage.section(topic)
        except Exception:
            return 'No topic text.'
    elif isinstance(topic,tuple):
        content=''
        for section in topic:
            content+=wikipage.section(section)
        return content
    else:
        return 'Invalid topic.'
            

#grab_wiki_sections(ginseng,desired_words)   

###clean up list##
'''super_string='|'.join(super_duper)
super_string=super_string.replace('*','')
super_string=super_string.replace('Equivalent plant:','|')
super_string=super_string.replace('[Syn.','|')
super_string=super_string.replace(']','')
super_string=super_string.replace(',','|')
super_string=super_string.replace('(',' ')
super_string=super_string.replace(')',' ')
super_string=super_string.replace(';','|')
super_string=super_string.replace('.','')
super_string=super_string.replace(':','')
super_string=super_string.strip()
super_string=re.sub(' +', ' ',super_string)
super_cleaned=super_string.split('|')

with open('ListHerbNames.txt', 'w') as filehandle:
    for listitem in super_cleaned:
        filehandle.write('%s\n' % listitem)
i=0
names=[]
for name in super_cleaned:
    try:
        wikipage=wiki_search(name)
        names.append(grab_wiki_sections(wikipage,desired_words))
    except wikipedia.DisambiguationError:
        pass
    i+=1
    print(name)

sections=[]
for wikipage in names:
    if wikipage:
      sections.append(grab_wiki_sections(wikipage,desired_words))          

has_something=[section if bool(section) else "NA" for section in names]

full_dict=defaultdict(set)
for d in names:
    for k, v in d.items():  
        full_dict[k]=v
        
names_df=pd.DataFrame.from_dict(full_dict).transpose()

names_df.to_csv('wiki_scraped_names.csv')'''
        
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





