import os
import sys
import pandas as pd
from data_source import DataSource_Herb, DataSource_Condition, DataSource_Interaction
from whoosh.index import create_in
from whoosh.fields import Schema, TEXT, ID, KEYWORD
from whoosh.index import open_dir  # for opening index directory
from whoosh import scoring  # used in Search section
from whoosh.query import *  # used in Search section
from whoosh.qparser import *
from spellchecker import SpellChecker

# search engine for herbs
class SearchEngine_Herb:

    index_path = 'index_herb'
    ix = None
    ds = None
    schema = None
    
    def __init__(self, ds):
        
        self.ds = ds
        
        # create schema
        self.schema = Schema(herb_id = ID(stored = True), 
                        name = TEXT(field_boost=2.0), 
                        pinyin = TEXT, 
                        other_name = TEXT,
                        summary=TEXT,
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
           
          
            writer.add_document(herb_id=str(value['herb_id']), 
                                name=','.join(value['english_name']),
                                pinyin=value['pinyin_name'],
                                other_name=','.join(value['other_name']),
                                summary=value['summary'],
                                conditions=','.join([x.split('|')[1] for x in value['valid_conditions']] if value['valid_conditions'] is not None else ''), 
                                interactions=','.join([x.split('|')[0] for x in value['interactions']]  if value['interactions'] is not None else ''), 
                                likely_safe=','.join([x.split('|')[0] for x in value['likely_safe']] if value['likely_safe'] is not None else ''), 
                                likely_unsafe=','.join([x.split('|')[0] for x in value['likely_unsafe']] if value['likely_unsafe'] is not None else ''), 
                                possibly_safe=','.join([x.split('|')[0] for x in value['possibly_safe']] if value['possibly_safe'] is not None else ''), 
                                possibly_unsafe=','.join([x.split('|')[0] for x in value['possibly_unsafe']] if value['possibly_unsafe'] is not None else ''), 
                                safe=','.join([x.split('|')[0] for x in value['safe']] if value['safe'] is not None else '')
                               )
            
        writer.commit()
        
    
    
    def search(self, query):
        
        #Ian Added Variations for searching on variations of the word, adeed OR group so it's either
        parser = QueryParser(None, self.schema,termclass=terms.Variations,group=OrGroup)  
        parser.add_plugin(MultifieldPlugin(["name", "pinyin", "other_name", "conditions", "interactions"]))
    
        search_result = []
        query = parser.parse(query)
        with self.ix.searcher() as s:
            results = s.search(query, limit=100)
            print(len(results))

            for r in results:
                search_result.append(self.ds.get_herb(int(r.get('herb_id'))))

        return search_result


# search engine for conditions
class SearchEngine_Condition:

    index_path = 'index_condition'
    ix = None
    ds = None
    schema = None
    
    def __init__(self, ds):
        
        self.ds = ds
        
        # create schema
        self.schema = Schema(condition_id = ID(stored = True), 
                        condition = TEXT(field_boost=2.0), 
                        summary=TEXT,
                        herbs=TEXT
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

        for key, value in ds.cond_dict.items():
          
            writer.add_document(condition_id=str(value['condition_id']), 
                                condition=value['condition'],
                                summary=value['summary'],
                                herbs=','.join([x.split('|')[1].split('*')[0] for x in value['all_herbs']] if value[''] is not None else '')
                               )
            
        writer.commit()
        
    
    
    def search(self, query):
        
        parser = QueryParser(None, self.schema,termclass=terms.Variations,group=OrGroup)  
        parser.add_plugin(MultifieldPlugin(["condition", "herbs"]))
    
        search_result = []
        query = parser.parse(query)
        with self.ix.searcher() as s:
            results = s.search(query, limit=100)
            print(len(results))

            for r in results:
                search_result.append(self.ds.get_condition(int(r.get('condition_id'))))

        return search_result


# search engine for interactions
class SearchEngine_Interaction:

    index_path = 'index_interaction'
    ix = None
    ds = None
    schema = None
    
    def __init__(self, ds):
        
        self.ds = ds

        # create schema
        self.schema = Schema(interaction_id = ID(stored = True), 
                        interaction = TEXT(field_boost=2.0), 
                        summary=TEXT,
                        herbs=TEXT
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

        for key, value in ds.interaction_dict.items():
          
            writer.add_document(interaction_id=str(value['interaction_id']), 
                                interaction=value['interaction'],
                                summary=value['summary'],
                                herbs=','.join([x.split('|')[1].split('*')[0] for x in value['all_herbs']] if value[''] is not None else '')
                               )
            
        writer.commit()
        
    
    
    def search(self, query):
        
        parser = QueryParser(None, self.schema,termclass=terms.Variations,group=OrGroup)  
        parser.add_plugin(MultifieldPlugin(["interaction", "herbs"]))
    
        search_result = []
        query = parser.parse(query)
        with self.ix.searcher() as s:
            results = s.search(query, limit=100)
            print(len(results))

            for r in results:
                search_result.append(self.ds.get_interaction(int(r.get('interaction_id'))))

        return search_result


# herbert spell checker
class Herbert_SpellChecker():

    spell = None
    spell_list = []
    
    def __init__(self, ds):
    
        #Build Spelling Dictionary
        ##Build Spell list off Herbs and Conditions
        for key, value in ds.herb_dict.items():
            self.spell_list.extend([i for word in value['english_name'] for i in word.split(' ')])
            self.spell_list.extend([re.split(' |\\|', word)[1] for word in value['valid_conditions']])
        
        self.spell = SpellChecker()   #add parameter languages = None to not pre-load a default dictionary
        self.spell.word_frequency.load_words(self.spell_list*100)

    def check(self, query):
    
        split_query = query.split(' ')
        correct_query = []

        for word in split_query:
            # Get the one `most likely` answer
            correct = self.spell.correction(word)
            if correct != word:
                correct_query.append(correct)
            else:
                correct_query.append(word)

            new_query=" ".join(correct_query)
            print("NEW QUERY", new_query)
        
        return new_query
        
        
        
        
