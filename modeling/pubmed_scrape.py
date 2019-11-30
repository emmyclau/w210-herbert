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