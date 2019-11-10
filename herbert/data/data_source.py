import pandas as pd
import re


class Herb:

    english_name = ''
    pinyin_name = ''
    intro = ''
    conditions = []
    sideeffects = []
    interactions = []
    others = ''
    '''
    intro = "Ginger is an herbal supplement, which can be used as a natural remedy in treatment of antiemetic, carminative, stimulant and also as an anti-inflammatory. It can be effective in treatment of dyspepsia, migraine headache, morning sickness, nausea (chemo induced), post-operative nausea and/or vomiting, osteoarthritis, respiratory infections, rheumatoid arthritis and for SSRI taper/discontinuation.\nDemonstrated antiemetic efficacy in pregnancy, postoperative nausea and vomiting and vertigo. It is possibly ineffective for motion sickness.\nInsufficient reliable data to rate use in chemotherapy induced nausea and vomiting, migraine headache, osteoarthritis and rheumatoid arthritis\nGinger is available under the following different brand names: African ginger, black ginger, cochin ginger, Imber, Jamaica ginger, race ginger, rhizoma zingerberis, rhizome, sheng jiang, Shokyo, zingibain, Zingiber officinale, and Zingiberis."

    conditions = ['digestion', 'nausea', 'cold and flu relief', 'pain reduction', 'inflammation', 'cardiovascular health']
    sideeffects = ['increased bleeding tendency', 'abdominal discomfort', 'cardiac arrhythmias (if overdosed)', \
                       'central nervous system depression (if overdosed)', 'dermatitis (with topical use)', \
                       'diarrhea', 'heartburn', 'mouth or throat irritation']
    interactions = ['Medications that slow blood clotting (Anticoagulant / Antiplatelet drugs)',\
                     'Phenprocoumon', 'Warfarin (Coumadin)']


    others = "Ginger is an herbal supplement, which can be used as a natural remedy in treatment of antiemetic, carminative, stimulant and also as an anti-inflammatory. It can be effective in treatment of dyspepsia, migraine headache, morning sickness, nausea (chemo induced), post-operative nausea and/or vomiting, osteoarthritis, respiratory infections, rheumatoid arthritis and for SSRI taper/discontinuation.\nDemonstrated antiemetic efficacy in pregnancy, postoperative nausea and vomiting and vertigo. It is possibly ineffective for motion sickness.\nInsufficient reliable data to rate use in chemotherapy induced nausea and vomiting, migraine headache, osteoarthritis and rheumatoid arthritis\nGinger is available under the following different brand names: African ginger, black ginger, cochin ginger, Imber, Jamaica ginger, race ginger, rhizoma zingerberis, rhizome, sheng jiang, Shokyo, zingibain, Zingiber officinale, and Zingiberis."
    '''

    def __init__(self,
                 english_name=None,
                 pinyin_name=None,
                 intro=None,
                 conditions=None,
                 sideeffects=None,
                 interactions=None,
                 others=None):

        if english_name is not None:
            self.english_name = english_name

        if pinyin_name is not None:
            self.pinyin_name = pinyin_name

        if intro is not None:
            self.intro = intro

        if conditions is not None:
            self.conditions = conditions

        if sideeffects is not None:
            self.sideeffects = sideeffects

        if interactions is not None:
            self.interactions = interactions

        if others is not None:
            self.others = others


class DataSource:

    herb_dict = None

    def __init__(self):
        self.herb_dict = pd.read_csv('herbert/data/meAndQi.csv').set_index(
            'Herb_Name').to_dict()

    def get_herb(self, name):

        if self.herb_dict['Pinyin_Name'].get(name) is None:
            return Herb()

        else:
            return Herb(name,
                        self.herb_dict['Pinyin_Name'].get(name),
                        conditions=re.sub(
                            r'(\[|\]|\')', '',
                            self.herb_dict['conditions'].get(name)).split(','))
