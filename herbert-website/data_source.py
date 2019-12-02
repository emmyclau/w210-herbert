import pandas as pd
import re
import pickle
         
# data source for herbs
class DataSource_Herb:
    
    herb_dict = None
    
    def __init__(self):
        with open('data/herbert_valid_herb_v4.pickle', 'rb') as handle:
            self.herb_dict = pickle.load(handle)
               
    def get_herb(self, idx):
        return self.herb_dict[idx]  
    
    def get_all(self):
        result = []
        for key, value in self.herb_dict.items():
            
            chinese_name = ''
            if (value["chinese_name"] is not None) and len(value["chinese_name"]) > 0:
                chinese_name = value["chinese_name"][0]
            result.append("{}|{}|{}".format(value["english_name"][0], value["english_name"][0], chinese_name))
            result.sort()
           
        return result
        
    
# data source for conditions    
class DataSource_Condition:
    
    cond_dict = None
    
    def __init__(self):
        with open('data/herbert_condition_v4.pickle', 'rb') as handle:
            self.cond_dict = pickle.load(handle)
               
    def get_condition(self, idx):
        return self.cond_dict[idx]  

# data source for interactions        
class DataSource_Interaction:
    
    interaction_dict = None
    
    def __init__(self):
        with open('data/herbert_interaction_v4.pickle', 'rb') as handle:
            self.interaction_dict = pickle.load(handle)
               
    def get_interaction(self, idx):
        return self.interaction_dict[idx]  

 