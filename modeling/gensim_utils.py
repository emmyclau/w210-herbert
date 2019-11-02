#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 29 07:16:41 2019

@author: gurdit.chahal
"""
exec(open('wiki_scrape.py').read())

from gensim.models import KeyedVectors
from gensim.summarization.summarizer import summarize
from gensim import utils
from scipy.spatial.distance import cosine
wv_from_bin = KeyedVectors.load_word2vec_format("wikipedia-pubmed-and-PMC-w2v.bin", binary=True)

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
   
def  summarize_wiki_page(wikipage,ratio=.1,contents,word_count=None):
    subset_dict=grab_wiki_sections(wikipage,contents)
    summary=[]
    for key,val in subset_dict.items():
        summary.append(summarize(val,ratio=ratio,word_count=word_count))
    return ''.join(summary)