#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 05:22:44 2019

@author: gurdit.chahal
"""

exec(open('extraction_utils.py').read())

medline=pd.read_excel('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/medline_nih_attribs.xls')

medline['safety_relations']=medline['safety'].apply(lambda doc: [subtree_matcher(sent,find_rel=True) for sent in nlp(doc).sents])

medline['know_relations']=medline['know'].apply(lambda doc: [subtree_matcher(sent,find_rel=True) for sent in nlp(doc).sents])

medline['learned_relations']=medline['learned'].apply(lambda doc: [subtree_matcher(sent,find_rel=True) for sent in nlp(doc).sents])

medline['background_relations']=medline['background'].apply(lambda doc: [subtree_matcher(sent,find_rel=True) for sent in nlp(doc).sents])

cols=['safety','know','learned','background']
for col in cols:
    print(col)
    medline['SVO_'+col]=medline[col].apply(lambda doc:[extract_clausieSVO(collocate_np(sent)) for sent in nlp(doc).sents])
    print('SVO done')
    #'SVOO','SVOA' removed
    medline['Prop_'+col]=medline[col].apply(lambda doc:[extract_clausieProp(collocate_np(sent).strip(),clause_type=['SVO','SVC']) for sent in nlp(doc).sents])
    print('Prop done')
    medline['Propsent_'+col]=medline['Prop_'+col].apply(lambda prop:[clausie.proposition_text_str(p) for p in flatten_list(prop)])


medline_clause_extract=medline.to_csv('medline_nih_extract.csv')

fifty_fundamental=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/fifty_fundamental_herbs_labeled.csv')

from mediawiki import MediaWiki
wikipediamw = MediaWiki()
#wikipedia.page(wikipedia.search('Agastache rugosa')[0])
ff_dict=defaultdict(lambda:'')
for name in fifty_fundamental.Scientific_Name:
    try:
        wikipagemw=wikipediamw.page(name)
    except wikipediamw.PageError:
        print(name)
        search=wikipediamw.search(name)
        if search:
            wikipage=wikipediamw.page(search[0])
        else:
            continue #continue forces to loop to next iteration whereas pass goes to rest of loop
    print("content for: "+name)
    toc=get_toc_mw(wikipagemw) #transform ordered dictionairy of sections and subsections to tuples of sections and subsections
    for section in toc:
        ff_dict[name,section[0]]+=wiki_topic_text(wikipagemw,section)+' \n '

ff_kept=defaultdict(lambda:'')
for row in fifty_fundamental.itertuples(index=True, name='Pandas'):
    name=getattr(row,'Scientific_Name')
    for col in ast.literal_eval(getattr(row, "Relevent_Table_Contents")):
        ff_kept[name,col]=ff_dict[name,col]
    
ff_keptv2=  {k: v for k, v in ff_kept.items() if v}      

ff=pd.DataFrame.from_dict(ff_keptv2,orient='index')
ff.columns=['Text']
ff['relations']=ff['Text'].apply(lambda doc: [subtree_matcher(sent,find_rel=True) for sent in nlp(doc).sents])
import clausiepy as clausie
ff['SVO']=ff['Text'].apply(lambda doc:[extract_clausieSVO(sent.text) for sent in nlp(doc).sents])
ff['Prop']=ff['Text'].apply(lambda doc:[extract_clausieProp(sent.text.strip(),clause_type=['SVO','SVC','SVOO','SVOA']) for sent in nlp(doc).sents])
ff['Prop_sent']=ff['Prop'].apply(lambda prop:[clausie.proposition_text_str(p) for p in flatten_list(prop)])
ff.to_csv('fifty_fundamental_extract.csv')

summary_dict=defaultdict(lambda:'')
for row in fifty_fundamental.itertuples(index=True, name='Pandas'):
    name=getattr(row,'Scientific_Name')
    toc=ast.literal_eval(getattr(row,"Table_Contents"))
    rtoc=ast.literal_eval(getattr(row, "Relevent_Table_Contents"))
    wikipage=wikipediamw.page(name)
    summary_dict[name]=wiki_summary(wikipage,toc,rtoc,mode='single')
ff_sum=pd.DataFrame.from_dict(summary_dict,orient='index')
ff_sum.columns=['Summary']
ff_sum.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/ff_summary.csv')

mq=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/meAndQi.csv')

summary_dict=defaultdict(lambda:'')
for row in mq.itertuples(index=True, name='Pandas'):
    name=getattr(row,'herb')
    wikipage,page_used=wiki_search(name,return_type='both')
    print("Looked for "+name+" got "+page_used)
    try:
        wikipage=wikipediamw.page(page_used)
        toc=wikipage.sections
        summary_dict[name]={'name_used':page_used,'summary':wiki_summary(wikipage,toc,[],mode='single')}
    except:
        pass
mq_sum=pd.DataFrame.from_dict(summary_dict,orient='index')

mq_sum.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/meAndQi_summary.csv')

