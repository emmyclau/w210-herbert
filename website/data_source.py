import pandas as pd
import re

         
class DataSource:
    
    herb_dict = None
    
    def __init__(self):
        
        
        self.herb_dict = pd.read_csv('data/herbert_herbs_v2.csv', encoding='utf-8').fillna('').transpose().to_dict()

        for key in self.herb_dict.keys():
            
            self.herb_dict[key]['herb_id'] = str(key)

            self.herb_dict[key]['english_name'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                   re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                       self.herb_dict[key].get('english_name'))]

            self.herb_dict[key]['pinyin_name'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                  re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                      self.herb_dict[key].get('pinyin_name'))]

            self.herb_dict[key]['chinese_name'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                   re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                       self.herb_dict[key].get('chinese_name'))]
            
           
            self.herb_dict[key]['other_name'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                   re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                       self.herb_dict[key].get('other_name'))]
            

            self.herb_dict[key]['new_conditions'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                     re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                         self.herb_dict[key].get('new_conditions'))]

            self.herb_dict[key]['interactions'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                   re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                       self.herb_dict[key].get('interactions'))]

            self.herb_dict[key]['likely_safe'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                  re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                      self.herb_dict[key].get('likely_safe'))]

            self.herb_dict[key]['likely_unsafe'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                    re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                        self.herb_dict[key].get('likely_unsafe'))]

            self.herb_dict[key]['possibly_safe'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                    re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                        self.herb_dict[key].get('possibly_safe'))]

            self.herb_dict[key]['possibly_unsafe'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                                      re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                                          self.herb_dict[key].get('possibly_unsafe'))]

            self.herb_dict[key]['safe'] = [re.sub(r'(\[|\]|\'|\"|^\s|\s$)', '', match) for match in \
                                           re.split(r", (?=(?:'[^']*?(?: [^']*)*))|, (?=[^',]+(?:,|$))", \
                                               self.herb_dict[key].get('safe'))]
            
            
        
    def get_herb(self, idx):
        return self.herb_dict[idx]
    
   