import os
import sys
import re
import pandas as pd
from data_source import DataSource 
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.index import open_dir  # for opening index directory
from whoosh import scoring  # used in Search section
from whoosh.query import *  # used in Search section
from whoosh.qparser import *
from whoosh.spelling import *
from spellchecker import SpellChecker

class SearchEngine:

    index_path = 'index'
    ix = None
    ds = None
    schema = None
    spell = None
    spell_list = []

    def __init__(self, ds):

        #Build Spelling Dictionary
        ##Build Spell list off Herbs and Conditions
        for key, value in ds.herb_dict.items():
            self.spell_list.extend([i for word in value['english_name'] for i in word.split(' ')])
            self.spell_list.extend([i for word in value['new_conditions'] for i in re.split(' |\\|',word)])
        
        self.spell = SpellChecker()   #add parameter languages = None to not pre-load a default dictionary
        self.spell.word_frequency.load_words(self.spell_list*100)

        
        self.ds = ds

        # create schema
        self.schema = Schema(herb_id = ID(stored = True), 
                        name = TEXT, 
                        pinyin = TEXT, 
                        other_name = TEXT,
                        conditions = TEXT, 
                        interactions = TEXT, 
                        likely_safe = TEXT, 
                        likely_unsafe = TEXT, 
                        possibly_safe = TEXT, 
                        possibly_unsafe = TEXT, 
                        safe = TEXT
                       )

        if os.path.exists(self.index_path):  
            self.ix = open_dir(self.index_path)
            return 
        
        os.mkdir(self.index_path)
        self.ix = create_in(self.index_path, self.schema)

        # Open Directory
        self.ix = open_dir(self.index_path)

        # Write all the data from the csv file to the index
        writer = self.ix.writer()

        for key, value in ds.herb_dict.items():
            writer.add_document(herb_id=value['herb_id'], 
                                name=','.join(value['english_name']),
                                pinyin=value['pinyin_name'],
                                other_name=','.join(value['other_name']),
                                conditions=','.join(value['new_conditions'] if value['new_conditions'] is not None else ''), 
                                interactions=','.join(value['interactions'] if value['interactions'] is not None else ''), 
                                likely_safe=','.join(value['likely_safe'] if value['likely_safe'] is not None else ''), 
                                likely_unsafe=','.join(value['likely_unsafe'] if value['likely_unsafe'] is not None else ''), 
                                possibly_safe=','.join(value['possibly_safe'] if value['possibly_safe'] is not None else ''), 
                                possibly_unsafe=','.join(value['possibly_unsafe'] if value['possibly_unsafe'] is not None else ''), 
                                safe=','.join(value['safe'] if value['safe'] is not None else '')
                               )


            '''
            writer.add_document(herb_id=value['herb_id'], 
                                name=','.join(value['english_name']),
                                pinyin=value['pinyin_name'],
                                conditions=','.join(value['new_conditions'] if value['new_conditions'] is not None else ''), 
                                interactions=','.join(value['interactions'] if value['interactions'] is not None else ''), 
                                likely_safe=','.join(value['likely_safe'] if value['likely_safe'] is not None else ''), 
                                likely_unsafe=','.join(value['likely_unsafe'] if value['likely_unsafe'] is not None else ''), 
                                possibly_safe=','.join(value['possibly_safe'] if value['possibly_safe'] is not None else ''), 
                                possibly_unsafe=','.join(value['possibly_unsafe'] if value['possibly_unsafe'] is not None else ''), 
                                safe=','.join(value['safe'] if value['safe'] is not None else '')
                               )
                
           '''
        writer.commit()

    
    def search(self, query):

        #find words in query that may be misspelled
        split_query = query.split(' ')
        correct_query = []

        for word in split_query:
            # Get the one `most likely` answer
            correct = self.spell.correction(word)
            if correct != word:
                correct_query.append(correct)
            else:
                correct_query.append(word)

            newq=" ".join(correct_query)
            print("NEW QUERY", newq)

        # Whoosh code to run search off corrected query
        parser = QueryParser(None, self.schema,termclass=terms.Variations,group=OrGroup)  #Ian Added Variations for searching on variations of the word, adeed OR group so it's either
        parser.add_plugin(MultifieldPlugin(["name", "other_name", "conditions"]))
        search_result = []
        qp = parser.parse(newq)
        

        with self.ix.searcher() as s:
            results = s.search(qp, limit=100, terms=True)
            print(len(results))

            for r in results:
                #print(r, r.score)
                search_result.append(self.ds.get_herb(int(r.get('herb_id'))))

              
##ATTEMPT for Highlighting Conditions in Query
                #cond = (self.ds.herb_dict[int(r.get('herb_id'))].get('conditions'))
                #print(cond)
                #print("RESULT TERMS:",r.matched_terms())
                #print("RESULT CONDITIONS",r.matched_terms()[0])
                #print("QUERY:",query)
                #print("QP",qp)
                #if str(query) in cond:
                #    print ("YEP COND in QUERY",query)

            
        return search_result

