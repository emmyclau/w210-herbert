#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 07:16:41 2019

@author: gurdit.chahal
"""
exec(open('wiki_scrape.py').read())
import ast 
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
import clausiepy as clausie
from itertools import chain
#import textacy has to be in separate environment
import phrasemachine
import time

print("loading word vecs...")
wv_from_bin = KeyedVectors.load_word2vec_format("wikipedia-pubmed-and-PMC-w2v.bin", binary=True)
print('loading spacy')
nlp = spacy.load("scilg")
merge_nps = nlp.create_pipe("merge_noun_chunks")
nlp.add_pipe(merge_nps)

verb_clause_pattern = r'<VERB>*<ADV>*<PART>*<VERB>+<PART>*'

def ascii_only(string):
    return re.sub(r'[^\x00-\x7f]',r' ', string).strip()
    #return ' '.join(char for char in string if ord(char) < 128)
    #return string.encode("ascii", errors="ignore").decode()

def extract_verbs(text,pattern=verb_clause_pattern):
    v_phrase=textacy.extract.pos_regex_matches
    return list(v_phrase)

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

#word2vec_model.n_similarity
#https://radimrehurek.com/gensim/models/keyedvectors.html
def relavent_contents(wikipage,keywords,word2vec_model,toc_mode=False,threshold=False):
    #expect list of table of contents or wikipage to extract contents from
    if toc_mode:
        if type(wikipage)==list:
            table_of_contents=wikipage
        elif type(wikipage)==str:
            table_of_contents=ast.literal_eval(wikipage)
        else:
            table_of_contents=[]
    else:
        table_of_contents=get_toc(wikipage)
    table=[content.lower() for content in table_of_contents]
    f_content=[]
    for content in table:
        filtered_content=[c for c in content.split() if c in word2vec_model.vocab]
        f_content.append(filtered_content) #expect list of lists
    kept=[]
    for key in keywords:    
        #take similarity between words or groups of words
        sims=np.asarray([word2vec_model.n_similarity(key.split(),fc) for fc in f_content])
        if threshold:
            kept.extend(np.where(sims>threshold))
        else:
            kept.append(np.argmax(sims))
            
    kept=np.unique(kept)
    return [table_of_contents[k] for k in kept]

top_words=np.asarray(['medicine','adverse','interact','warn','effect','side effect','react','toxic','regulate','death','poison','allergy','risk','overdose','safe','unsafe'])
   
def  summarize_wiki_page(wikipage,contents,wikisec=False,ratio=.1,word_count=None):
    if wikisec:
        subset_dict=grab_wikisec_toc(wikipage,contents)
    else:   
        subset_dict=grab_wiki_sections(wikipage,contents)
    summary=[]
    for key,val in subset_dict.items():
        try:
            summarized=summarize(val,ratio=ratio,word_count=word_count)
            summary.append(summarized)
        except ValueError:
            continue  
    return ''.join(summary)


def group_np(doc):
      spans = list(doc.ents) + list(doc.noun_chunks)
      spans = spacy.util.filter_spans(spans)
      with doc.retokenize() as retokenizer:
            for span in spans:
                retokenizer.merge(span)
      return doc

def collocate_np(doc):
    doctext=doc.text
    spans = list(doc.ents) + list(doc.noun_chunks)
    spans = spacy.util.filter_spans(spans)
    #print(spans)
    for span in spans:
        collocation='_'.join(span.text.split())
       # print(collocation)
        doctext=doctext.replace(span.text,collocation)
    return doctext

def break_clauses(doc):
    #todo: break for each subject
    pass
    
def subtree_matcher(doc,find_rel=False):
  subjpass = 0
  
  for i,tok in enumerate(doc):
    # find dependency tag that contains the text "subjpass"    
    if tok.dep_.find("subjpass") == True:
      subjpass = 1

  x = ''
  y = ''
  x_pos=0
  y_pos=0
  # if subjpass == 1 then sentence is passive
  if subjpass == 1:
    for i,tok in enumerate(doc):
      if tok.dep_.find("subjpass") == True:
        y = tok.text
        y_pos=max(i,y_pos)
      if tok.dep_.endswith("obj") == True:
        x = tok.text
        x_pos=max(i,x_pos)
      if (tok.dep_.startswith('conj') == True) and y:
          y+=' '+tok.text
          y_pos=max(i,y_pos)
      if (tok.dep_.startswith('case') == True) and y:
          y+=' '+tok.text
          y_pos=max(i,y_pos)
  # if subjpass == 0 then sentence is not passive
  else:
    for i,tok in enumerate(doc):
      if tok.dep_.endswith("subj") == True:
        x = tok.text
        x_pos=max(i,x_pos)
      if tok.dep_.endswith("obj") == True:
        y = tok.text
        y_pos=max(i,y_pos)
      if (tok.dep_.startswith('nmod') == True) and y:
          y+=', '+tok.text
          y_pos=max(i,y_pos)
  if find_rel and x and y:
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

def rule_get_relation(sent):

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
  
verb = "<ADV>*<AUX>*<VERB><PART>*<ADV>*"
word = "<NOUN|ADJ|ADV|DET|ADP>"
preposition = "<ADP|ADJ>"

rel_pattern = "( %s (%s* (%s)+ )? )+ " % (verb, word, preposition)
grammar_long = '''REL_PHRASE: {\\%s}''' % rel_pattern


def filter_spans(spans):
    # Filter a sequence of spans so they don't contain overlaps
    # For spaCy 2.1.4+: this function is available as spacy.util.filter_spans()
    get_sort_key = lambda span: (span.end - span.start, -span.start)
    sorted_spans = sorted(spans, key=get_sort_key, reverse=True)
    result = []
    seen_tokens = set()
    for span in sorted_spans:
        # Check for end - 1 here because boundaries are inclusive
        if span.start not in seen_tokens and span.end - 1 not in seen_tokens:
            result.append(span)
        seen_tokens.update(range(span.start, span.end))
    result = sorted(result, key=lambda span: span.start)
    return result

def extract_entity_relations(doc):
    # Merge entities and noun chunks into one token
    spans = list(doc.ents) + list(doc.noun_chunks)
    spans = filter_spans(spans)
    with doc.retokenize() as retokenizer:
        for span in spans:
            retokenizer.merge(span)
    

    relations = []
    for enty in filter(lambda w: w.ent_type_ == "ENTITY", doc):
        if enty.dep_ in ("attr", "dobj"):
            subject = [w for w in enty.head.lefts if w.dep_=="nsubj"]
            if subject:
                subject = subject[0]
                relations.append((subject, enty))
        elif enty.dep_ == "pobj" and enty.head.dep_ == "prep":
            relations.append((enty.head.head, enty))
    return relations

def extract_relations(doc):

    spans = list(doc.ents) + list(doc.noun_chunks)
    for span in spans:
        span.merge()
    
    triples = []
        
    for ent in doc.ents:
        preps = [prep for prep in ent.root.head.children if prep.dep_ == "prep"]
        for prep in preps:
            for child in prep.children:
                triples.append((ent.text, "{} {}".format(ent.root.head, prep), child.text))
            
    
    return triples

def extract_clausieSVO(text):
    clauses=clausie.clausie(text)
    svo=[]
    for clause in clauses:
        if clause['type']=='SVO':
            svo.append(clause)
    return svo


#https://github.com/mmxgn/spacy-clausie
def extract_clausieProp(text,clause_type=None):
    try:
        clauses=clausie.clausie(text)
        clause_list=[]
        if clause_type:
            for clause in clauses:
                if clause['type']in clause_type :
                 clause_list.append(clause)   
                else: 
                    pass
        propositions = clausie.extract_propositions(clauses)
    except IndexError:
        propositions=[]
    return propositions

def keep_relevant_verbs(entity_triple,verb_keywords):
    #todo only keep triples that are relevant
    pass

def flatten_list(l):
    return list(chain.from_iterable(l))

def grab_wikisec_toc(wikipage,toc):
    section_dict=defaultdict(lambda:'not_captured')
    for topic in toc:
        section_dict[topic]=wikipage.section(topic)
    return section_dict

def wiki_summary(wikipage,toc,relevant_toc,mode='multi',wikisec=True,word_count=150):
    wikisum=wikipage.summary
    wikisum_len=len(wikisum.split())
    if toc:#if non-empty table of contents
        sum_fields=list(set(toc).difference(set(relevant_toc)))
        if mode=='multi':
            sum_sum=summarize_wiki_page(wikipage,sum_fields,wikisec=wikisec)
            sum_total=wikisum+sum_sum
        elif mode=='single':
            text=[]
            subset_dict=grab_wikisec_toc(wikipage,sum_fields)
            for key,content in subset_dict.items():
                text.append(content)
            try:
                sum_sum=wikisum+''.join(text)
            except TypeError:
                sum_sum=wikisum
            sum_sum_len=len(sum_sum.split())
            if sum_sum_len<word_count:
                sum_total=sum_sum
            else:
                sum_total=summarize(sum_sum,word_count=word_count)    
    else:
        if  wikisum_len<word_count:
            sum_total=wikisum
        else:    
            sum_total=summarize(wikisum,word_count=word_count)
    return sum_total   


'''
example usage:
    doc=nlp("Ginger may treat inflammation and mild motion sickness.")
    #just entities
    subtree_matcher(doc): ('Ginger', 'inflammation, mild motion sickness')
    #entity 1 relation to entity 2
    subtree_matcher(doc,find_rel=True): ('Ginger', 'treat', 'inflammation, mild motion sickness')
import clausiepy as clausie
clauses = clausie.clausie('A preliminary study suggested that eating acai fruit pulp might reduce blood sugar and cholesterol levels in overweight people.')
propositions = clausie.extract_propositions(clauses)
clausie.print_propositions(propositions)
'''
