#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov 30 13:09:08 2019

@author: gurdit.chahal
"""

import pandas as pd
from collections import defaultdict

pdf_path='/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/cooking/tcmdietgrouprecipebook.pdf'

#https://pdfminersix.readthedocs.io/en/latest/index.html
#https://pypi.org/project/pdftotext/
import pdftotext

with open(pdf_path, "rb") as f:
    pdf = pdftotext.PDF(f)

recipe_book=defaultdict(lambda:{})
for page in pdf:
    components=page.split('\n')
    if 'Ingredients:' in components:
        ingredient_pos=components.index('Ingredients:')
    else:
        ingredient_pos=0
    if 'Directions:' in components:
        directions_pos=components.index('Directions:')
    elif 'Cooking Instruction:' in components:
        directions_pos=components.index('Cooking Instruction:')
    elif 'Cooking Instructions:' in components:
        directions_pos=components.index('Cooking Instructions:')
    elif 'Cooking methods:' in components:
        directions_pos=components.index('Cooking methods:')
    else:
        directions_pos=0
    print(ingredient_pos)
    if ingredient_pos and directions_pos:
        direction=''
        recipe_book[components[0]]={'Ingredients':'|'.join(components[ingredient_pos:directions_pos])}
        for component in components[directions_pos+1:]:
            direction_flag=component.strip()[0].isdigit()
            if direction_flag:
                direction+='|'+component
            else:
                break
        recipe_book[components[0]].update({'Directions':direction})
        print(components[0])
    else:
        pass
    
recipes=pd.DataFrame.from_dict(recipe_book,orient='index')
    
recipes.to_excel('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/tcmdietgroup.xlsx')   


    