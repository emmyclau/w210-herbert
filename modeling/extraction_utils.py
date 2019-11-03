#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 07:16:41 2019

@author: gurdit.chahal
"""
exec(open('wiki_scrape.py').read())
from spacy.matcher import Matcher 
from spacy.tokens import Span 
import numpy as np
import pandas as pd
import scispacy
import spacy
from gensim.models import KeyedVectors
from gensim.summarization.summarizer import summarize
from gensim import utils
import re
from scipy.spatial.distance import cosine
import wikipedia
import urllib.request
import requests
from bs4 import BeautifulSoup as bs
from collections import defaultdict
import json
import os

wv_from_bin = KeyedVectors.load_word2vec_format("wikipedia-pubmed-and-PMC-w2v.bin", binary=True)
nlp = spacy.load("scilg")
merge_nps = nlp.create_pipe("merge_noun_chunks")
nlp.add_pipe(merge_nps)

verb_clause_pattern = r'<VERB>*<ADV>*<PART>*<VERB>+<PART>*'


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
    

def has_vector_representation(word2vec_model, doc):
    """check if at least one word of the document is in the
    word2vec dictionary"""
    return not all(word not in word2vec_model.vocab for word in doc)


def filter_docs(corpus, texts, labels, condition_on_doc):
    """
    Filter corpus, texts and labels given the function condition_on_doc which takes
    a doc.
    The document doc is kept if condition_on_doc(doc) is true.
    """
    number_of_docs = len(corpus)

    if texts is not None:
        texts = [text for (text, doc) in zip(texts, corpus)
                 if condition_on_doc(doc)]

    labels = [i for (i, doc) in zip(labels, corpus) if condition_on_doc(doc)]
    corpus = [doc for doc in corpus if condition_on_doc(doc)]

    print("{} docs removed".format(number_of_docs - len(corpus)))

    return (corpus, texts, labels)


def relavent_contents(wikipage,keywords,word2vec_model):
    table_of_contents=get_toc(wikipage)
    table=[content.lower() for content in table_of_contents]
    doc=','.join(table).split(',')
    vecs=[]
    for content in table:
        filtered_content=[word_vectors.word2vec_model.word_vec(c, use_norm=True) for c in content if c in word2vec_model.vocab]
        avg_vec=np.mean(filtered_content,axis=0)
        vecs.append(avg_vec)
        kept=[]
    for word in keywords:
        key_vec=word2vec_model.word_vec(word, use_norm=True)
        
        kept.append(np.argmax(cosine(key_vec,vecs)))
    return table_of_contents[kept]

top_words=np.asarray(['adverse','interact','warn','effect','side effect','react','toxic','regulate','death','poison','allergy','risk','overdose','safe','unsafe'])
   
def  summarize_wiki_page(wikipage,contents,ratio=.1,word_count=None):
    subset_dict=grab_wiki_sections(wikipage,contents)
    summary=[]
    for key,val in subset_dict.items():
        summary.append(summarize(val,ratio=ratio,word_count=word_count))
    return ''.join(summary)


def subtree_matcher(doc,find_rel=False):
  subjpass = 0

  for i,tok in enumerate(doc):
    # find dependency tag that contains the text "subjpass"    
    if tok.dep_.find("subjpass") == True:
      subjpass = 1

  x = ''
  y = ''

  # if subjpass == 1 then sentence is passive
  if subjpass == 1:
    for i,tok in enumerate(doc):
      if tok.dep_.find("subjpass") == True:
        y = tok.text

      if tok.dep_.endswith("obj") == True:
        x = tok.text
      if (tok.dep_.startswith('conj') == True) and x:
          y+=' '+tok.text
  # if subjpass == 0 then sentence is not passive
  else:
    for i,tok in enumerate(doc):
      if tok.dep_.endswith("subj") == True:
        x = tok.text
        x_pos=i
      if tok.dep_.endswith("obj") == True:
        y = tok.text
        y_pos=i
      if (tok.dep_.startswith('conj') == True) and x:
          y+=', '+tok.text
          y_pos=i
  if find_rel:
      rel=get_relation(doc[:np.max([x_pos,y_pos])].text)
      
      return x,rel,y
  else:
      return x,y

def get_relation(sent):

  doc = nlp(sent)

  # Matcher class object 
  matcher = Matcher(nlp.vocab)

  #define the pattern 
  pattern = [{'DEP':'ROOT'}, 
            {'DEP':'prep','OP':"?"},
            {'DEP':'agent','OP':"?"},  
            {'POS':'ADJ','OP':"?"}] 

  matcher.add("matching_1", None, pattern) 

  matches = matcher(doc)
  k = len(matches) - 1

  span = doc[matches[k][1]:matches[k][2]] 

  return(span.text)
  
'''
example usage:
    doc=nlp("Ginger may treat inflammation and mild motion sickness.")
    subtree_matcher(doc): ('Ginger', 'inflammation, mild motion sickness')
    subtree_matcher(doc,find_rel=True): ('Ginger', 'treat', 'inflammation, mild motion sickness')
'''
    