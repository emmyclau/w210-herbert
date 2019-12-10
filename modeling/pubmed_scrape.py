#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 00:27:00 2019

@author: gurdit.chahal
"""
#https://pypi.org/project/metapub/
#https://github.com/biocommons/eutils
import os
from collections import defaultdict
import pandas as pd
os.environ['NCBI_API_KEY']='f30fa4fea4985edcc02616c4755d5d62a608'
import metapub

fetch = metapub.PubMedFetcher()
''' e.g.
example=fetch.pmids_for_query("ginseng[Title] AND fatigue [Title]")
article=fetch.article_by_pmid(example[3])
article.to_dict()

article.url
article.title

example2=fetch.pmids_for_clinical_query("ginseng",category='therapy',optimization='broad')
article2=fetch.article_by_pmid(example2[0])
article.title

'''

master_list=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/extracted_wiki.csv')
herb=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/herb.csv')
herb_ref=dict(zip(herb['herb'],herb['herb_id']))
master_list['HerbId']=master_list['Herb'].apply(lambda h: herb_ref.get(h.strip(),999))
pubmed_dict=defaultdict(lambda:'')
accepted_tags=['[bpoc]','[dsyn]','[fndg]','[sosy]','[mobd]','[virs]','[hops]','[inpo]']
for row in master_list.itertuples(index=True, name='Pandas'):
    herbid=str(getattr(row,'HerbId'))
    herb=getattr(row,'Herb')
    harmflag=str(getattr(row,'HarmFlag')==['NO_MATCH'])
    umls=getattr(row,'UMLS')
    #|term*cuid*category|
    condition_tuples=umls.split('|')
    for tup in condition_tuples:
        triple=tup.split('*')
        if (len(triple)==3) and (triple[2] in accepted_tags):
            query=herb+'[Title] AND '+triple[0]+'[Title]'
           # print(query)
            pmids=fetch.pmids_for_query(query,retmax=5)
           # print(len(pmids))
            if len(pmids):
                for pmid in pmids:
                    article=fetch.article_by_pmid(pmid)
                    try:
                        pubmed_dict[herbid]+='*'.join([herbid,herb,triple[0],harmflag,article.title,article.url])+'|'
                    except TypeError:
                        pass
    if not bool(pubmed_dict[herbid]):
        query=herb+'[Title]'
        pmids=fetch.pmids_for_clinical_query(query,category='therapy',optimization='broad',retmax=5)
        if len(pmids):
            # print(query)
             #print(len(pmids))
             for pmid in pmids:
                    article=fetch.article_by_pmid(pmid)
                    try:
                        pubmed_dict[herbid]+='*'.join([herbid,herb,'REASEARCH','False',article.title,article.url])+'|'
                    except TypeError:
                        pass
    print(herb)
    
pubmed_wiki=pd.DataFrame.from_dict(pubmed_dict,orient='index')  
pubmed_wiki.columns=["Info_String"]  
pubmed_wiki.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/pubmed_conditions.csv')

master_list=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/valid_herb_conditions.csv')
pubmed_dict=defaultdict(lambda:'')

for row in master_list.itertuples(index=True, name='Pandas'):
    herbid=str(getattr(row,'herb_id'))
    herb=getattr(row,'name')
    umls=getattr(row,'conditions')
    #|term|
    conditions=umls.split('|')
    for condition in conditions:
            query=herb+'[Title] AND '+condition+'[Title]'
           # print(query)
            pmids=fetch.pmids_for_query(query,retmax=5)
           # print(len(pmids))
            if len(pmids):
                for pmid in pmids:
                    article=fetch.article_by_pmid(pmid)
                    try:
                        pubmed_dict[herbid]+='*'.join([herbid,herb,condition,'NO_FLAG',article.title,article.url])+'|'
                    except TypeError:
                        pass
    '''if not bool(pubmed_dict[herbid]):
        query=herb+'[Title]'
        pmids=fetch.pmids_for_clinical_query(query,category='therapy',optimization='broad',retmax=5)
        if len(pmids):
            # print(query)
             #print(len(pmids))
             for pmid in pmids:
                    article=fetch.article_by_pmid(pmid)
                    try:
                        pubmed_dict[herbid]+='*'.join([herbid,herb,'REASEARCH','False',article.title,article.url])+'|'
                    except TypeError:
                        pass'''
    print(herb)
    
pubmed_wiki=pd.DataFrame.from_dict(pubmed_dict,orient='index')  
pubmed_wiki.columns=["Info_String"]  
pubmed_wiki.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/pubmed_conditions_valid.csv')

name='ginger'
herbid=678
pubmed='https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2792472/,https://www.ncbi.nlm.nih.gov/pubmed/12576305'
conditions='stomach ache, diarrhea,vomiting,nausea,motion sickness,Rheumatoid Arthritis' 
condition=''
safety='abdominal discomfort, heartburn, diarrhea,gas,Cholelithiasis'
safe=''
interactions='anticoagulants (blood thinners)|Warfarin'
from pyMeSHSim.metamapWrap.MetamapInterface import MetaMap
from pyMeSHSim.Sim.similarity import metamapFilter
mm_path='/Users/gurdit.chahal/public_mm/bin/metamap18'
mm_filter = metamapFilter(path=mm_path)
metamap = MetaMap(path=mm_path)
conditions= metamap.runMetaMap(semantic_types=metamap.semanticTypes , conjunction=False, term_processing=False, text=conditions)
for c in conditions:
    condition+=c['preferred_name']+'|'
s=metamap.runMetaMap(semantic_types=metamap.semanticTypes , conjunction=False, term_processing=False, text=safety)
for c in s:
    safe+=c['preferred_name']+'|'
interactions=metamap.runMetaMap(semantic_types=metamap.semanticTypes , conjunction=False, term_processing=False, text=interactions)
for c in interactions:
    print(c['preferred_name'])