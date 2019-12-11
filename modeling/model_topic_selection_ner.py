#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Nov  2 05:22:44 2019

@author: gurdit.chahal
"""

exec(open('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/modeling/extraction_utils.py').read())

from pyMeSHSim.metamapWrap.MetamapInterface import MetaMap
from pyMeSHSim.Sim.similarity import metamapFilter
mm_path='/Users/gurdit.chahal/public_mm/bin/metamap18'
mm_filter = metamapFilter(path=mm_path)
sem_types=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/SemanticTypes_2018.txt',sep='|',header=None)
sem_types.columns=['Abrev','Ref','Mapping']
#concepts = filter.runMetaMap(semantic_types=filter.semanticTypes 
#results = filter.discardAncestor(concepts=concepts)
metamap = MetaMap(path=mm_path)

medline=pd.read_excel('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/medline_nih_attribs.xls')

#mesh extractions
columns=['background','know','learned','safety']
extracted_dict=defaultdict(lambda:{})
for col in columns:
    medline[col+'_extract']=medline[col].apply(lambda x: ascii_only(x))
    for row in medline.itertuples(index=True, name='Pandas'):
        name=getattr(row,'herb')
        extracted_dict[name].update({col:''})
        text_fromcol=(getattr(row,col+'_extract'))
        concepts= metamap.runMetaMap(semantic_types=metamap.semanticTypes , conjunction=False, term_processing=False, text=text_fromcol) 
        for con in concepts:
            #if ast.literal_eval(con['score'])>9:
                #herb-->column-->concepts in column
                # , sep tuple of concept attributes, | sep for concepts
            extracted_dict[name][col]+=','.join([con['preferred_name'],con['semtypes'],con['score'],con['cui']])+'|'
    print(name + ' concepts extracted for '+col)       

med_herbs=list(medline.herb)

accepted=['[bpoc]','[dsyn]','[fndg]','[sosy]',['mobd'],'[virs]','[hops]',['inpo']]

medline['treats']='No Info'
medline['harm']='No Info'
for row in medline.itertuples(index=True, name='Pandas'):
    name=getattr(row,'herb')
    sympts=extracted_dict[name]['background'].split('|')
    accepted_sympts=[]
    for symp in sympts:
        triple=symp.split(',')
        print(triple)
        if len(triple)==4 and (triple[1] in accepted):
            accepted_sympts.append(triple[0]+'*'+triple[3])
    medline.set_value(row.Index,'treats','|'.join(accepted_sympts))
   
    harms=extracted_dict[name]['safety'].split('|')
    accepted_harms=[]
    for harm in harms:
        triple=harm.split(',')
        print(triple)
        if len(triple)==4 and (triple[1] in accepted):
            accepted_harms.append(triple[0]+'*'+triple[3])
    medline.set_value(row.Index,'harm','|'.join(accepted_harms))

medline['CommonNames']=medline['common_names'].apply(lambda x: str(x).split(':')[-1])

medline['CommonNames']=medline['CommonNames'].apply(lambda s: '|'.join(s.split(',')) ) 

#learned --> SVO

medline=medline[['herb','CommonNames','treats','harm']]
medline.columns=['Herb','CommonNames','Treats','Harms']
medline.to_csv('medline_herb_symptoms.csv')

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

ff_symp=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/fifty_fundamental_extract.csv')
ff_symp=ff_symp[['Unnamed: 0','Text']]
ff_symp.columns=['HerbTopicPair','Text']
ff_symp['Text']=ff_symp['Text'].apply(lambda x: ascii_only(x))
extracted_dict=defaultdict(lambda:{})

for row in ff_symp.itertuples(index=True, name='Pandas'):
        name=getattr(row,'HerbTopicPair')
        extracted_dict[name].update({'Text':''})
        text_fromcol=(getattr(row,'Text'))
        '''text_fromcol=text_fromcol.split()
        texty=[]
        for text in text_fromcol:
            if text.startswith('anti'):
                text=text.replace('anti','anti ')
                if text.endswith('al'):
                    text.replace('al','a')
            elif text.startswith('anti-'):
                text=text.replace('anti-','anti- ')
            elif text.endswith('cant'):
                text=text.replace('cant','ify')
            texty.append(text)
        text_fromcol=' '.join(texty)'''
        concepts= metamap.runMetaMap(semantic_types=metamap.semanticTypes , conjunction=False, term_processing=False, text=text_fromcol) 
        for con in concepts:
            #if ast.literal_eval(con['score'])>9:
                #herb-->column-->concepts in column
                # , sep tuple of concept attributes, | sep for concepts
            extracted_dict[name]['Text']+=','.join([con['preferred_name'],con['semtypes'],con['score'],con['cui']])+'|'
            print(name + ' concepts extracted for '+name) 

ff_symp['Medical']='No Info'

for row in ff_symp.itertuples(index=True, name='Pandas'):
    name=getattr(row,'HerbTopicPair')
    sympts=extracted_dict[name]['Text'].split('|')
    accepted_sympts=[]
    for symp in sympts:
        triple=symp.split(',')
        print(triple)
        if len(triple)==4:
            accepted_sympts.append(triple[0]+'*'+triple[3])
    ff_symp.set_value(row.Index,'Medical','|'.join(accepted_sympts))

danger_words=np.asarray(['adverse','interact','warn','effect','side effect','react','toxic','regulate','death','poison','allergy','risk','overdose','unsafe','safe'])

ff_symp['IsHarm']= ff_symp['HerbTopicPair'].apply(lambda toc_list:(match_subset(lower_all(ast.literal_eval(toc_list)[1].split()),danger_words)))   

ff_symp['Herb']=ff_symp['HerbTopicPair'].apply(lambda pair: ast.literal_eval(pair)[0]) 
ff_symp.to_csv('FiftySymptoms.csv')

ff_symp=pd.read_csv('FiftySymptoms.csv')
fifty_fundamental['Chinese_Name']=fifty_fundamental['Chinese_Name'].apply(lambda x: x.strip('()'))
fifty_dict=dict(fifty_fundamental[['Scientific_Name','Chinese_Name']].values.tolist())
ff_symp['ChineseName']=ff_symp['Herb'].apply(lambda h: fifty_dict[h])
ff_symp['Url']='No Url'
for row in ff_symp.itertuples(index=True, name='Pandas'):
    name=getattr(row,'Herb')
    wikipage=wikipediamw.page(name)
    ff_symp.set_value(row.Index,'Url',wikipage.url)


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

symmap=pd.read_excel('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/SymMap v1.0, SMHB file (1).xlsx')

summary_dict=defaultdict(lambda:'')
for row in symmap.itertuples(index=True, name='Pandas'):
    name=getattr(row,'Latin_name')
    if isinstance(name,float):
        name=getattr(row,'English_name')
        if isinstance(name,float):
            name==getattr(row,'Pinyin_name')
    wikipage,page_used=wiki_search(name.split(';')[0],return_type='both')
    print("Looked for "+name+" got "+page_used)
    try:
        wikipage=wikipediamw.page(page_used)
        toc=wikipage.sections
        summary_dict[name]={'name_used':page_used,'summary':wiki_summary(wikipage,toc,[],mode='single')}
    except:
        pass
sym_sum=pd.DataFrame.from_dict(summary_dict,orient='index')
sym_sum.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/symmap_summary.csv')

medline_nat=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/medline_natmedicines_1.csv')



summary_dict=defaultdict(lambda:'')
for row in medline_nat.itertuples(index=True, name='Pandas'):
    name=getattr(row,'herb')
    wikipage,page_used=wiki_search(name,return_type='both')
    print("Looked for "+name+" got "+page_used)
    try:
        wikipage=wikipediamw.page(page_used)
        toc=wikipage.sections
        summary_dict[name]={'name_used':page_used,'summary':wiki_summary(wikipage,toc,[],mode='single')}
    except:
        pass
mn_sum=pd.DataFrame.from_dict(summary_dict,orient='index')

mn_sum.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/medline_natmedicines_summary.csv')

medline_nih=pd.read_excel('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/medline_nih_attribs.xlsx')
summary_dict=defaultdict(lambda:'')
for row in medline_nih.itertuples(index=True, name='Pandas'):
    name=getattr(row,'herb')
    wikipage,page_used=wiki_search(name,return_type='both')
    print("Looked for "+name+" got "+page_used)
    try:
        wikipage=wikipediamw.page(page_used)
        toc=wikipage.sections
        summary_dict[name]={'name_used':page_used,'summary':wiki_summary(wikipage,toc,[],mode='single')}
    except:
        pass
mih_sum=pd.DataFrame.from_dict(summary_dict,orient='index')

mih_sum.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/medline_nih_summary.csv')

top_words= ['poison',
 'react',
 'unsafe',
 'adverse',
 'safe',
 'regulate',
 'allergy',
 'interact',
 'medicine',
 'warn',
 'death',
 'side effect',
 'risk',
 'toxic',
 'overdose',
 'effect',
 'medic',
 'use',
 'application',
 'poison',
 'health',
 'pharm',
 'treat',
 'mental',
 'psych',
 'nutrition',
 'benefi',
 'diet']

english=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/herb.csv')
summary_dict=defaultdict(lambda:'')
english_dict=defaultdict(lambda:'')
content_dict=defaultdict(lambda:'')
url_dict=defaultdict(lambda:'')
english['new_english_name']=english['new_english_name'].str.replace(r"\(.*\)","")



for row in english.itertuples(index=True, name='Pandas'):
    name=getattr(row,'new_english_name')
    herbId=getattr(row,'herb_id')
    wikipage,page_used=wiki_search(name,return_type='both')
    #print("Looked for "+name+" got "+page_used)
    try:
       
        if (bool(wikipage) == False):
            next_best=name.split(' of ')
            if len(next_best)>1:
               next_best.reverse()
               second_best=' '.join(next_best)
               wikipage,page_used=wiki_search(second_best,return_type='both')
              # wikipage=wikipediamw.page(page_used)
               if (bool(wikipage) == False):
                   next_try=next_best[0]
                   wikipage,page_used=wiki_search(next_try,return_type='both')
                   #wikipage=wikipediamw.page(page_used)
        
        wikipage=wikipediamw.page(page_used)
        toc=get_toc_mw(wikipage)
        for section in toc:
                toc_list=match_subset(lower_all(list(section)),top_words)
                if toc_list[0]=='NO_MATCH':
                    continue
                print(name,section[0])
                #e.g. https://en.wikipedia.org/wiki/Ginseng#Other_plants_sometimes_called_ginseng
                url_dict[name,section[0]]+=wikipage.url+'#'+'_'.join(section[-1].split())+'|'
                content_dict[name,section[0]]+=wiki_topic_text(wikipage,section)+' \n '
        english_dict[name]={'OriginalName':name,'NameUsed':wikipage.title,'Url':wikipage.url,'Toc':toc,'HerbId':herbId}
        print('attempted entry for '+wikipage.title+' alias for '+name )
        summary_dict[name]={'HerbId':herbId,'name_used':page_used,'summary':wiki_summary(wikipage,toc,[],mode='single'),'Url':wikipage.url}
    except requests.exceptions.ReadTimeout:
        print('timeout!')
        time.sleep(5)
        try:
            
            if (bool(wikipage) == False):
                next_best=name.split(' of ')
                if len(next_best)>1:
                   next_best.reverse()
                   second_best=' '.join(next_best)
                   wikipage,page_used=wiki_search(second_best,return_type='both')
                  # wikipage=wikipediamw.page(page_used)
                   if (bool(wikipage) == False):
                       next_try=next_best[0]
                       wikipage,page_used=wiki_search(next_try,return_type='both')
                       #wikipage=wikipediamw.page(page_used)
            
            wikipage=wikipediamw.page(page_used)
            toc=get_toc_mw(wikipage)
            for section in toc:
                toc_list=match_subset(lower_all(list(section)),top_words)
                if toc_list[0]=='NO_MATCH':
                    continue
                print(name,section[0])
                url_dict[name,section[0]]+=wikipage.url+'#'+'_'.join(section[-1].split())+'|'
                content_dict[name,section[0]]+=wiki_topic_text(wikipage,section)+' \n '
            english_dict[name]={'OriginalName':name,'NameUsed':wikipage.title,'Url':wikipage.url,'Toc':toc,'HerbId':herbId}
            summary_dict[name]={'HerbId':herbId,'name_used':page_used,'summary':wiki_summary(wikipage,toc,[],mode='single'),'Url':wikipage.url}
            print('attempted entry for '+wikipage.title+' alias for '+name )
        
        except:
            print('passed on '+name)
        pass
    except:
        print('passed on '+name)
        pass
     

extracted_wiki=pd.DataFrame.from_dict(content_dict,orient='index')
extracted_wiki.columns=['Text']
extracted_wiki['Text']=extracted_wiki['Text'].apply(lambda x: ascii_only(x))
extracted_wiki['UMLS']='No Info'
for row in extracted_wiki.itertuples(index=True, name='Pandas'):
        text_fromcol=getattr(row,'Text')
        concepts= metamap.runMetaMap(semantic_types=metamap.semanticTypes , conjunction=False, term_processing=False, text=text_fromcol) 
        joined=''
        for con in concepts:
            
                #herb-->column-->concepts in column
                # * sep tuple of concept attributes, | sep for concepts
                #,con['semtypes'],con['score'],
            joined+='*'.join([con['preferred_name'],con['cui'],con['semtypes']])+'|'
            extracted_wiki.set_value(row.Index,'UMLS',joined)
        print(' concepts extracted for '+str(row.Index))  
#add herbid
extracted_wiki['Herb']=extracted_wiki.index
extracted_wiki['Herb']=extracted_wiki['Herb'].apply(lambda tup: tup[0])
extracted_wiki['HerbId']=extracted_wiki['Herb'].apply(lambda name:  english_dict[name]['HerbId'])
extracted_wiki['Url']=extracted_wiki.index
extracted_wiki['Url']=extracted_wiki['Url'].apply(lambda index: url_dict[index])
extracted_wiki['HarmFlag']=extracted_wiki.index
extracted_wiki['HarmFlag']=extracted_wiki['HarmFlag'].apply(lambda tup: tup[1])
extracted_wiki['HarmFlag']=extracted_wiki['HarmFlag'].apply(lambda topic: match_subset(lower_all([topic]),danger_words)) 
extracted_wiki.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/extracted_wiki.csv')
english_wiki=pd.DataFrame.from_dict(english_dict,orient='index')
english_wiki.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/english_wiki.csv')
english_sum=pd.DataFrame.from_dict(summary_dict,orient='index')
english_sum.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/english_summary_url.csv')

symmap=pd.read_csv('symmap_herbs.csv',encoding='utf8')
sym=symmap[['Herb_ID','Pinyin_Name','English_Name']]
sym=symmap[['Herb_Id','Pinyin_Name','English_Name']]
sym['Url']='No info'
sym_prefix='SMHB'
url_base='https://www.symmap.org/detail/'
sym['Url']=sym['Herb_Id'].apply(lambda h: url_base+sym_prefix+('0'*(5-len(str(h))))+str(h))

condition_dict=defaultdict(lambda:'')
conditions=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/condition_v8.csv',encoding='utf8')
for row in conditions.itertuples(index=True, name='Pandas'):
    name=getattr(row,'condition')
    conditionId=getattr(row,'condition_id')
    try:
            
        wikipage,page_used=wiki_search(name,return_type='both')
        wikipage=wikipediamw.page(page_used)
        toc=get_toc_mw(wikipage)
        condition_dict[name]={'ConditionId':conditionId,'name_used':wikipage.title,'summary':clean_summary(wiki_summary(wikipage,toc,[],mode='single')),'url':wikipage.url,'toc':toc}
        print('attempted entry for '+wikipage.title+' alias for '+name )
    except:
        pass
condition_wiki=pd.DataFrame.from_dict(condition_dict,orient='index')    
condition_wiki.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/conditionv8_wiki.csv')   

interaction_dict=defaultdict(lambda:'')        
interactions=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/interaction_v5.csv',encoding='utf8')
for row in interactions.itertuples(index=True, name='Pandas'):
    name=getattr(row,'interaction')
    interactionId=getattr(row,'interaction_id')
    try:
        wikipage,page_used=wiki_search(name,return_type='both')
        wikipage=wikipediamw.page(page_used)
        toc=get_toc_mw(wikipage)
        interaction_dict[name]={'InteractionIdId':interactionId,'name_used':wikipage.title,'summary':clean_summary(wiki_summary(wikipage,toc,[],mode='single')),'url':wikipage.url,'toc':toc}
        print('attempted entry for '+wikipage.title+' alias for '+name )
    except:
         pass
interaction_wiki=pd.DataFrame.from_dict(interaction_dict,orient='index')    
interaction_wiki.to_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/interactionv5_wiki.csv')   


topic_select=pd.read_csv('/Users/gurdit.chahal/Capstone_Data_Mining/w210-herbert/data_sources/fifty_fundamental_herbs_g.csv')
master_contents=list(np.unique(topic_select.Table_Contents.apply(ast.literal_eval).sum())) #132 unique headings
m_contents=list(topic_select.Table_Contents.apply(ast.literal_eval).sum())
topic_select.Table_Contents.apply(ast.literal_eval).apply(len).describe()
topic_select.Relavent_A.apply(ast.literal_eval).apply(len).describe()

tally=[]
for row in topic_select.itertuples(index=True,name='Pandas'):
    master=len(ast.literal_eval(getattr(row,'Table_Contents')))
    sub=len(ast.literal_eval(getattr(row,'Relavent_Model')))
    if master >0:
        tally.append(sub/master)
np.mean(tally)

tally_dict={}
for row in topic_select.itertuples(index=True,name='Pandas'):
    master=ast.literal_eval(getattr(row,'Table_Contents'))
    sub_A=ast.literal_eval(getattr(row,'Relavent_A'))
    sub_M=ast.literal_eval(getattr(row,'Relavent_Model'))
    herb=getattr(row,'Scientific Name')
    
    
indiv_contentsa=list(topic_select.Relavent_A.apply(stringify_eval).sum())
indiv_contentsml=list(topic_select.Relavent_Model.apply(stringify_eval).sum())
        
indiv_contentsa=list(np.unique(topic_select.Relavent_A.apply(stringify_eval).sum()))
indiv_contentsb=list(np.unique(topic_select.Relavent_B.apply(stringify_eval).sum()))
indiv_contentsc=list(np.unique(topic_select.Relavent_C.apply(stringify_eval).sum()))
indiv_contentsd=list(np.unique(topic_select.Relavent_D.apply(stringify_eval).sum()))
indiv_contentsml=list(np.unique(topic_select.Relavent_Model.apply(stringify_eval).sum()))
