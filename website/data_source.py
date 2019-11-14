import pandas as pd
import re

         
class DataSource:
    
    herb_dict = None
    
    def __init__(self):
        
        '''
        self.herb_dict = pd.read_csv('data/meAndQi.csv', encoding='utf8').transpose().to_dict()

        for key in self.herb_dict.keys():
            self.herb_dict[key]['conditions'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                                                       self.herb_dict[key].get('conditions')).split(',')
                                                       
        '''
        self.herb_dict = pd.read_csv('data/herbert_herbs_v1.csv', encoding='utf-8').fillna('').transpose().to_dict()

        for key in self.herb_dict.keys():

            self.herb_dict[key]['english_name'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                        self.herb_dict[key].get('english_name')).split(',')

            self.herb_dict[key]['pinyin_name'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                        self.herb_dict[key].get('pinyin_name')).split(',')

            self.herb_dict[key]['new_conditions'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                        self.herb_dict[key].get('new_conditions')).split(',')

            self.herb_dict[key]['interactions'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                        self.herb_dict[key].get('interactions')).split(',')

            self.herb_dict[key]['likely_safe'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                        self.herb_dict[key].get('likely_safe')).split(',')

            self.herb_dict[key]['likely_unsafe'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                        self.herb_dict[key].get('likely_unsafe')).split(',')

            self.herb_dict[key]['possibly_safe'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                        self.herb_dict[key].get('possibly_safe')).split(',')

            self.herb_dict[key]['possibly_unsafe'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                        self.herb_dict[key].get('possibly_unsafe')).split(',')

            self.herb_dict[key]['safe'] = re.sub(r'(\[|\]|\'|^\s|\s$)', '', \
                        self.herb_dict[key].get('safe')).split(',')
    
    
            
        
    def get_herb(self, idx):
        return self.herb_dict[idx]
    
   