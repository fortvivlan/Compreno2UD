import re

#тут только одна функция помимо init: def convert_pos(self, token, lemma, pos_tag, feats, dep, label, semrel) -> str

class Pos_module:
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
                   'Interjection': 'INTJ'}#словарик для частей речи
        
        self.det_set = {'такой', 'какой', 'всякий',
           'некоторый', 'никакой', 'некий', 'сей', 'чей',
           'какой-либо', 'какой-нибудь','кое-какой',
           'весь', 'этот', 'тот', 'каждый',
           'мой', 'твой', 'ваш', 'наш', 'свой',
           'любой', 'каждый', 'какой-то', 'некоторый', 'такой-то',
           'чей-то', 'чей-либо', 'кой', 'никой'}#set для det
        
        self.symb_set = {'%', '$', '№', '°', '€', '+', '=', '#', '@', '~', '^', '\\','/', '&'}#set для symb
    
    def convert_pos(self, token, lemma, pos_tag, feats, dep, label, semrel) -> str:

        '''функция для обработки частей речи'''

        # конвертация в лоб по словарю
        if pos_tag in self.parts_of_speech:
            pos_tag = self.parts_of_speech[pos_tag]
        # конвертация с использованием feats
        if pos_tag == 'NOUN' and 'Proper' in feats:
            pos_tag = 'PROPN'  # надо бы еще леммы title делать
        elif pos_tag == 'VERB' and 'SyntacticParadigm' in feats and feats['SyntacticParadigm'][0] == 'SyntAuxVerb' or token in ('б', 'бы'):
            pos_tag = 'AUX'
        elif pos_tag == 'Conjunction':
            if 'Coordinator' in feats:
                pos_tag = 'CCONJ'
            else:
                pos_tag = 'SCONJ'
        if feats != None and pos_tag == 'NUM' and 'MaximallyRestrictiveModifiers' in feats and feats['MaximallyRestrictiveModifiers'][0] == 'Ordinal' \
                or label == 'OrderInTimeAndSpace' and semrel == 'DIGITAL_NUMBER' \
                or semrel == 'DAY_NUMBER':
                pos_tag = 'ADJ'

        if lemma in ('бен', 'аль', 'де') and pos_tag == 'Prefixoid':
            pos_tag = 'PROPN'
            if 'Case' in feats:
                feats.pop('Case')

        if lemma == '#Acronym' and pos_tag == 'Invariable':
            pos_tag = 'PROPN'
        Pron_to_det = {'их', 'его', 'Их', 'Его'}
        if dep == 'det':
            if lemma in self.det_set or token in Pron_to_det and token.lower() == lemma or token.lower() == 'ее' and lemma == 'её':
                pos_tag = 'DET'

        if token in self.symb_set:
            pos_tag = 'SYM'

        return pos_tag