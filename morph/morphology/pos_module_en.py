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
                    'Invariable': 'HUI'}#словарик для частей речи

        '''self.det_set = {'такой', 'какой', 'всякий',
                            'некоторый', 'никакой', 'некий', 'сей', 'чей',
                            'какой-либо', 'какой-нибудь','кое-какой',
                            'весь', 'этот', 'тот', 'каждый',
                            'мой', 'твой', 'ваш', 'наш', 'свой',
                            'любой', 'каждый', 'какой-то', 'некоторый', 'такой-то',
                            'чей-то', 'чей-либо', 'кой', 'никой'}#set для det'''
                        
        self.symb_set = {'%', '$', '№', '°', '€','£', '+', '=', '#', '@', '~', '^', '\\','/', '&'}#set для symb
    
    def convert_pos_en(self, token, lemma, pos_tag, feats, semclass) -> str:

        '''функция для обработки частей речи'''

        # конвертация в лоб по словарю
        if pos_tag in self.parts_of_speech:
            pos_tag = self.parts_of_speech[pos_tag]
        # конвертация с использованием feats
        if pos_tag == 'NOUN' and 'Classifying_Proper' in feats and feats['Classifying_Proper'][0] == ('NounProper' or 'CompanyName' or 'NounLanguageName'):
            pos_tag = 'PROPN'  # надо бы еще леммы title делать
        if pos_tag == 'NOUN' and 'Capitalization' in feats and feats['Capitalization'][0] == 'ProperCapitalization':
            pos_tag = 'PROPN'
        elif pos_tag == 'VERB' and 'SyntacticParadigm' in feats and feats['SyntacticParadigm'][0] == 'SyntAuxVerb':
            pos_tag = 'AUX'
        elif pos_tag == 'Conjunction':
            if 'Coordinator' in feats:
                pos_tag = 'CCONJ'
            else:
                pos_tag = 'SCONJ'

        #порядковые числительные считаются прилагательными:
        if pos_tag == 'NUM':
            if 'PartletOfSpeech' in feats and feats['PartletOfSpeech'] == ['NumeralOrdinal']:
                pos_tag == 'ADJ'
        
        if pos_tag == 'NOUN':
            if semclass == 'YEAR_NUMBER':
                pos_tag = 'NUM'
        
        #todo: для некоторых нужно поменять на DET часть речи


        if lemma == '#Acronym' and pos_tag == 'Invariable':
            pos_tag = 'PROPN'
        #Pron_to_det = {'их', 'его', 'Их', 'Его'}


        if token in self.symb_set:
            pos_tag = 'SYM'

        return pos_tag
