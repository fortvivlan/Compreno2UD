# 's притяжательное разбить на токены

import re
class Pos_module_en:
    def __init__(self):

        self.parts_of_speech = {'Noun': 'NOUN',
                    'Pronoun': 'PRON',
                    'Adjective': 'ADJ',
                    'Verb': 'VERB',
                    'Adverb': 'ADV',
                    'Numeral': 'NUM',
                    'Particle': 'PART',
                    'Preposition': 'ADP',
                    'Predicative': 'ADV',
                    'Interjection': 'INTJ',
                    'Article': 'DET',
                    'Invariable': 'ADV'}#словарик для частей речи

        self.symb_set = {'%', '$', '№', '°', '€','£', '+', '=', '#', '@', '~', '^', '\\','/', '&'}#set для symb

    def convert_pos_en(self, token, lemma, pos_tag, feats, deprel, semclass) -> str:

        '''функция для обработки частей речи'''

        # конвертация в лоб по словарю
        if pos_tag in self.parts_of_speech:
            pos_tag = self.parts_of_speech[pos_tag]
        # конвертация с использованием feats
        if pos_tag == 'NOUN' and 'Classifying_Proper' in feats and feats['Classifying_Proper'][0] in {'NounProper', 'CompanyName', 'NounLanguageName'}:
            pos_tag = 'PROPN'  # надо бы еще леммы title делать
        if pos_tag == 'NOUN' and 'Capitalization' in feats and feats['Capitalization'][0] == 'ProperCapitalization':
            pos_tag = 'PROPN'
        elif (pos_tag == 'VERB' and 'TypeOfParadigm' in feats and feats['TypeOfParadigm'][0] == 'AuxiliaryVerb') or semclass == 'NEAREST_FUTURE' or deprel == 'cop':
            pos_tag = 'AUX'
        elif pos_tag == 'Conjunction':
            if 'Coordinator' in feats:
                pos_tag = 'CCONJ'
            else:
                pos_tag = 'SCONJ'

        #порядковые числительные считаются прилагательными:
        if pos_tag == 'NUM':
            if 'PartletOfSpeech' in feats and feats['PartletOfSpeech'] == ['NumeralOrdinal']:
                pos_tag = 'ADJ'

        if pos_tag == 'NOUN':
            if semclass == 'YEAR_NUMBER':
                pos_tag = 'NUM'

        #RomanNumber
        if lemma == '#RomanNumber':
            pos_tag = 'NUM'
        if semclass == 'ACRONYM' and token in {'I', 'II'}:
            pos_tag = 'NUM'

        #todo: для некоторых нужно поменять на DET часть речи

        if lemma == '#Acronym' and pos_tag == 'Invariable':
            pos_tag = 'PROPN'
        #Pron_to_det = {'их', 'его', 'Их', 'Его'}
        if pos_tag == 'ADJ' and lemma.lower() in 'all':
            pos_tag = 'DET'
        elif deprel == 'det' or deprel == 'det:predet':
            pos_tag = 'DET'

        if token in self.symb_set:
            pos_tag = 'SYM'
        
        if lemma.lower() == 'to' and semclass == 'PARTICLE_TO':
            pos_tag = 'PART'
        
        if semclass == 'PHRASAL_PARTICLES':
            pos_tag = 'ADP'
        
        if lemma.lower() == 'as' and semclass == 'COMPARATIVE_CONJUNCTIONS':
            pos_tag = 'ADP'
        
        if lemma.lower() in {'today', 'tomorrow', 'yesterday'}:
            pos_tag = 'NOUN'

        if lemma.lower() in {'hundred', 'million', 'thousand'}:
            pos_tag = 'NUM'

        if lemma.lower() in {'vice', 'phono'} and pos_tag == 'Prefixoid':
            pos_tag = 'PROPN'


        return pos_tag
