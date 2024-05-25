# -*- coding: utf-8 -*-

import csv
import re

class Fixes:
    def __init__(self, path, invariable):
        self.path = path
        self.invariable = invariable
        self.kg_sm_set = {'м': 'метр',
                    'тыс.': 'тысяча',
                    'млн.': 'миллион',
                    'млн': "миллион",
                    'с': "секунда",
                    'кг': "килограмм",
                    'км.': "километр",
                    'км': "километр",
                    'долл.': "доллар",
                    'долл': "доллар",
                    'т': "тонна",
                    'кв': "квадратный",
                    'кв.': "квадратный",
                    'сек.': "секунда",
                    'обл.': "область",
                    'млрд': "миллиард",
                    'млрд.': "миллиард",
                    'см': "сантиметр",
                    'руб': "рубль",
                    'бул.': "бульвар",
                    'буль.': "бульвар",
                    'Гб': "гигабайт",
                    'Мб' : "мегабайт",
                    'Тб' : "терабайт",
                    'ГВт': "гигаватт",
                    'ГГц': "гигагерц",
                    'ГДж': "гигаджоуль",
                    'ул.': "улица"}
        self.hash_lemma_set = {'#Acronym',
                        '#AngleBrackets',
                        '#BoxBracketsProperName',
                        '#BracketedProperName',
                        '#CommaDash',
                        '#CommaForDirectSpeech',
                        '#Cue',
                        '#DashColonForQuotation',
                        '#DashCommaForQuotation',
                        '#DashFullStopForQuotation',
                        '#ElliptedAdjective',
                        '#ElliptedNoun',
                        '#ElliptedNumeral',
                        '#ElliptedPseudoNumeral',
                        '#ElliptedVerb',
                        '#EmergencyGap',
                        '#Enumeration',
                        '#ExclamationSentence',
                        '#Expression',
                        '#ForeignWord',
                        '#FormattedProperName',
                        '#IgnorableBrackets',
                        '#NormalForPostpositionalDeclarativeQuotation',
                        '#NormalNotSentenceParenthetic',
                        '#NormalSentence',
                        '#NormalSentenceWithDots',
                        '#Number',
                        '#ParagraphForCue',
                        '#PhoneNumber',
                        '#QuestionExclamationSentence',
                        '#QuestionSentence',
                        '#Quotation',
                        '#QuotationWithComma',
                        '#QuotationWithStop',
                        '#Reference',
                        '#Reporting_AfterMarkedEnd',
                        '#Reporting_Colon',
                        '#Reporting_Comma',
                        '#Reporting_FullStop',
                        '#RomanNumber',
                        '#Sentence_IntroducingDirectSpeech',
                        '#SentenceWithBracketBoundaries',
                        '#SentenceWithReport',
                        '#TemplateExpression',
                        '#UnbracketedProperName',
                        '#UnknownName',
                        '#UnknownWord',
                        '#URL',
                        '#Субстантиватор'}
        self.acronim_semrel_set = {'AIRBUS_AS_AIRPLANE',
                            'BOEING_AIRPLANE',
                            'DREAMLINER',
                            'EUROFIGHTER_AIRPLANE',
                            'FOKKER_AIRPLANE',
                            'MESSERSCHMITT_AIRPLANE',
                            'RIVET_JOINT',
                            'SUKHOI_SUPERJET',
                            'AN_AIRPLANES',
                            'ATLANT_AIRPLANE',
                            'BE_AIRPLANES',
                            'BOEING_AIRPLANE',
                            'GULFSTREAM_AIRPLANE',
                            'IL_AIRPLANES',
                            'CAUDRON',
                            'CONCORD_AIRPLANE',
                            'MESSERSCHMITT_AIRPLANE',
                            'RIVET_JOINT',
                            'CESSNA_AIRPLANE',
                            'SU_AIRPLANES',
                            'SUKHOI_SUPERJET',
                            'T_THIRTYTHREE',
                            'TU_AIRPLANES',
                            'FOKKER_AIRPLANE',
                            'CESSNA_AIRPLANE',
                            'YAK_AIRPLANES'}

        self.acronim_pattern = re.compile(r'\w+-\d+\w*')

    def imp_and_perf(self, lemma, feats) -> str:
        """
        Меняет леммы совершенного вида на несовершенный
        у токенов несовершенного вида.
        """
        dict_of_aspect_pairs = {}

        with open(self.path, 'r', encoding='utf8') as perfect_txt:
            for line in perfect_txt:
                imp, pf = line.strip('\n').split('\t')
                dict_of_aspect_pairs[pf] = imp
        if 'Aspect' in feats:
            if lemma in dict_of_aspect_pairs and feats['Aspect'][0] == 'Imperfective':
                lemma = dict_of_aspect_pairs[lemma]

        perfect_txt.close()

        return lemma
    
    def check_verb_lemmas(self, lemma, pos):

        """
        Возвращает список лемм, которых нет в
        списке на конвертацию из совершенного в несовершенный вид.
        """
        
        absent_verbs = []

        with open(self.path, 'r', encoding='utf8') as perfect_txt:
            l = list(perfect_txt)
            verb_list = []
            for line in l:
                new = line.strip('\n').split('\t')
                for i in new:
                    verb_list.append(i)

            if pos == 'Verb' and lemma not in verb_list:
                absent_verbs.append(lemma)

        return absent_verbs
    
    def fix_lemmas(self, token, lemma, feats) -> str:
        """
        Изменяет некорректные леммы.
        """

        if lemma in self.hash_lemma_set:
            lemma = token
        if lemma == 'считывать': #очень неприятный костыль для глагола в случаях: "он считает, что сделал правильно"
            lemma = 'считать'
        if token.lower() == 'они':
            lemma = 'они'
        elif token.lower() == 'оно':
            lemma = 'оно'
        elif token.lower() == 'она':
            lemma = 'она'

        if lemma in self.kg_sm_set and 'SpecialLexemes' in feats and feats['SpecialLexemes'][0] == 'Lex_KgSm':
            lemma = self.kg_sm_set[lemma]

        return lemma

    def indexation_bounded_csv(self, sent, csv_dict, bounded_token_list):
        """
        Разделяет токены, которые есть в доке csv, состоящие из нескольких токенов.
        Меняет индексацию.
        """
        dot_number = re.compile(r'\d+\.\d+')
        number_csv = 0
        for word in sent:
            divided_words = []
            c = 0
            if word['form'].lower() in bounded_token_list:
                for token in csv_dict.items():
                    if token[0].lower() == word['form'].lower():
                        for part in token[1]:
                            if part['head'] != '_':
                                head = int(part['head'])
                            else:
                                head = word['head']
                            if part['pos'] == 'PROPN' or part['form'] in ('I', 'II'):#с I можно еще подумать
                                new_word = {'id': word['id'] + c, 'form': part['form'], 'lemma': part['lemma'].lower().capitalize(), 'p0s': '_',
                                            'pos': part['pos'], 'grammemes': part['grammemes'], 'deprel': part['deprel'], 'deps': word['deps'], 'head': head, 'misc': '_',
                                            'SemSlot': '_', 'SemClass': '__'}
                            else:
                                new_word = {'id': word['id'] + c, 'form': part['form'], 'lemma': part['lemma'].lower(), 'p0s': '_',
                                            'pos': part['pos'], 'grammemes': part['grammemes'], 'deprel': part['deprel'], 'deps': word['deps'], 'head': head, 'misc': '_',
                                            'SemSlot': '_', 'SemClass': '__'}                                
                            
                            if new_word['head'] != 0:#если не вершина
                                new_word['head'] = new_word['id'] - new_word['head']
                                if 'None' in new_word['deps']:
                                    new_word['deps'] = f'{new_word["head"]}:{part["deprel"]}'
                                else:
                                    new_word['deps'] = f'{new_word["head"]}:{part["deprel"]}'
                                if part['pos'] == 'ADP' and part['deprel']== 'obl':
                                    new_word['deps'] = f'{new_word["head"]}:{part["deprel"]}:case'
                            else:#если вершина
                                new_word['head'] = word['head']
                                new_word['SemSlot'] = word['SemSlot']
                                new_word['SemClass'] = word['SemClass']
                                new_word['deprel'] = word['deprel']
                                new_word['deps'] = new_word['deps']
                                new_word['misc'] = '_'
                                new_word['p0s'] ='_'

                            if new_word['id'] == 1:
                                new_word['form'] = new_word['form'].title()
                            c += 1
                            divided_words.append(new_word)
                        dw = len(divided_words) - 1

                        if number_csv == 0:
                            number_csv +=1 
                        
                        start = sent.index(word)
                        for i in divided_words:
                            sent.insert(start, i)
                            start += 1
                        stop = sent.index(word)
                        sent.remove(word)
                        for old_word in sent[stop:]:
                            old_word['id'] += len(divided_words) - 1

                        for i in range(len(sent)):
                            # поменяли головы
                            if '_' not in str(sent[i]['head']) and int(sent[i]['head']) >= (stop - dw) and '.' not in str(sent[i]['head']) and '__' not in str(sent[i]['SemClass']):
                                
                                sent[i]['head'] = int(sent[i]['head']) + dw
                            # меняем депс
                            if dot_number.match(str(sent[i]['deps'])):
                                s = re.compile(r'((\d+\.\d+\.\d+|\d+\.\d+))').match(sent[i]["deps"]).group(0)
                                if '|' in sent[i]['deps']:
                                    def increment_numbers(match):
                                            number = float(match.group())
                                            if '_' != str(sent[i]['deps']) and number >= (stop - dw):
                                                return str(number + dw)
                                            return str(number)
                                    output_string = re.sub(r'(\d+\.\d+\.\d+|\d+\.\d+|\d+)', increment_numbers, sent[i]['deps'])
                                    sent[i]['deps'] = output_string
                                else:
                                    # если без | но с точкой
                                    if '_' != str(sent[i]['deps']) and float(s) >= (stop - dw):
                                        sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))', f'{float(s) + dw}', sent[i]['deps'])
                            else:
                                if '|' in sent[i]['deps']:
                                    def increment_numbers(match):
                                            number = int(match.group())
                                            if '_' != str(sent[i]['deps']) and number >= (stop - dw):
                                                return str(number + dw)
                                            return str(number)
                                    output_string = re.sub(r'\d+', increment_numbers, sent[i]['deps'])
                                    sent[i]['deps'] = output_string
                                s = re.compile(r'(\d+)\:(\w+|\w+:\w+|\w+:\w+:\w+)')

                                if s.fullmatch(sent[i]["deps"]):
                                    a = int(s.fullmatch(sent[i]["deps"]).group(1))
                                    if '_' != str(sent[i]['deps']) and a >= (stop - dw) and '__' not in str(sent[i]['SemClass']):
                                        sent[i]['deps'] = re.sub(r'(\d+\:)', f'{a + dw}:', sent[i]['deps'])
                                if sent[i]['SemClass'] == '__':
                                    sent[i]['SemClass'] = '_'


    def bounded_foreign(self, sent):
        """
        Разделяет иностранные слова, состоящие из нескольких токенов.
        Разделяет токены типа: 1990-1991
        """

        foreign_bounded_token = re.compile(r'[A-za-z]+ [A-za-z]+')
        number_bounded = re.compile(r'\d+,?\d*?-\d+,?\d*?')
        divided_words = []
        dot_number = re.compile(r'\d+\.\d+')
        number_csv = 0
        c = 0
        for word in sent:
            divided_words = []
            c = 0
            if foreign_bounded_token.search(word['form']):
                f_parts = word['form'].split()
                first_token_id = word['id'] + c
                new_word = {'id': first_token_id, 'form': f_parts[0], 'lemma': f_parts[0], 'pos': 'X', 'p0s': word['p0s'], 'grammemes': 'Foreign=Yes',
                            'deprel': word['deprel'], 'deps': word['deps'], 'head': word['head'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                divided_words.append(new_word)
                c += 1
                for f_part in f_parts[1:]:
                    new_word = {'id': word['id'] + c, 'form': f_part, 'lemma': f_part, 'pos': 'X', 'p0s': '_', 'grammemes': 'Foreign=Yes',
                                'deprel': 'flat:foreign', 'deps': f'{first_token_id}:flat:foreign', 'head': first_token_id, 'misc': '_', 'SemSlot': '_', 'SemClass': word['SemClass']}
                    c += 1
                    divided_words.append(new_word)
                dw = len(divided_words) - 1

                if number_csv == 0:
                    number_csv +=1 
                
                start = sent.index(word)
                for i in divided_words:
                    sent.insert(start, i)
                    start += 1
                stop = sent.index(word)
                sent.remove(word)
                for old_word in sent[stop:]:
                    old_word['id'] += len(divided_words) - 1

                for i in range(len(sent)):
                    # поменяли головы
                    if '_' not in str(sent[i]['head']) and int(sent[i]['head']) > (stop - dw) and '.' not in str(sent[i]['head']) and '__' not in str(sent[i]['SemClass']):
                            sent[i]['head'] = int(sent[i]['head']) + dw
                    # меняем депс
                    if dot_number.match(str(sent[i]['deps'])):
                        
                        s = re.compile(r'((\d+\.\d+\.\d+|\d+\.\d+))').match(sent[i]["deps"]).group(0)
                        if '|' in sent[i]['deps']:
                            def increment_numbers(match):
                                    number = float(match.group())
                                    if '_' != str(sent[i]['deps']) and number >=  (stop - dw):
                                        return str(number + dw)
                                    return str(number)
                            output_string = re.sub(r'(\d+\.\d+\.\d+|\d+\.\d+|\d+)', increment_numbers, sent[i]['deps'])
                            sent[i]['deps'] = output_string
                            
                        else:
                            if '_' != str(sent[i]['deps']) and float(s) >= (stop - dw):
                                sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))', f'{float(s) + 1}', sent[i]['deps'])
                    else:                        
                        if '|' in sent[i]['deps']:
                            def increment_numbers(match):
                                    number = int(match.group())
                                    if '_' != str(sent[i]['deps']) and number >= (stop - dw):
                                        return str(number + dw)
                                    return str(number)
                            output_string = re.sub(r'\d+', increment_numbers, sent[i]['deps'])
                            sent[i]['deps'] = output_string
                        s = re.compile(r'(\d+)\:(\w+|\w+:\w+|\w+:\w+:\w+)')

                        if s.fullmatch(sent[i]["deps"]):
                            a = int(s.fullmatch(sent[i]["deps"]).group(1))
                            
                            if '_' != str(sent[i]['deps']) and a > (stop - dw) and '__' not in str(sent[i]['SemClass']):
                                sent[i]['deps'] = re.sub(r'(\d+\:)', f'{a + dw}:', sent[i]['deps'])

                        if sent[i]['SemClass'] == '__':
                            sent[i]['SemClass'] = '_'

            elif number_bounded.fullmatch(word['form']) and word['pos'] in ('ADJ', 'NUM') and word['SemSlot'] != 'Specification':
                    parts = re.compile(r'(\d+,?\d*?)(-)(\d+,?\d*?)').findall(word['form'])
                    first_token_id = word['id'] + c
                    new_word = {'id': first_token_id, 'form': parts[0][0], 'lemma': parts[0][0], 'pos': word['pos'], 'p0s': word['p0s'], 'grammemes': word['grammemes'],
                                'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                    c += 1
                    divided_words.append(new_word)
                    new_word = {'id': word['id'] + c, 'form': parts[0][1], 'lemma': parts[0][1], 'pos': '__', 'p0s': '_', 'grammemes': '_',
                                'head': first_token_id, 'deprel': 'punct', 'deps': f'{first_token_id}:{word["deprel"]}', 'misc': 'SpaceAfter=No', 'SemSlot': '_', 'SemClass': 'punct'}
                    c += 1
                    divided_words.append(new_word)
                    new_word = {'id': word['id'] + c, 'form': parts[0][2], 'lemma': parts[0][2], 'pos': '__', 'p0s': word['p0s'],  'grammemes': word['grammemes'],
                                'head': first_token_id, 'deprel': word['deprel'], 'deps': f'{first_token_id}:{word["deprel"]}:minus', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                    c += 1
                    divided_words.append(new_word)
                    dw = len(divided_words) - 1

                    if number_csv == 0:
                        number_csv +=1 
                    
                    start = sent.index(word)
                    for i in divided_words:
                        sent.insert(start, i)
                        start += 1
                    stop = sent.index(word)
                    sent.remove(word)
                    for old_word in sent[stop:]:
                        old_word['id'] += len(divided_words) - 1

                    for i in range(len(sent)):
                        # поменяли головы
                        if '_' not in str(sent[i]['head']) and int(sent[i]['head']) > (stop - dw) and '.' not in str(sent[i]['head']) and '__' not in str(sent[i]['SemClass']):
                            sent[i]['head'] = int(sent[i]['head']) + dw
                        # меняем депс
                        if dot_number.match(str(sent[i]['deps'])):
                            s = re.compile(r'((\d+\.\d+\.\d+|\d+\.\d+))').match(sent[i]["deps"]).group(0)
                            if '|' in sent[i]['deps']:
                                def increment_numbers(match):
                                        number = float(match.group())
                                        if '_' != str(sent[i]['deps']) and number >=  (stop - dw):
                                            return str(number + dw)
                                        return str(number)
                                output_string = re.sub(r'(\d+\.\d+\.\d+|\d+\.\d+|\d+)', increment_numbers, sent[i]['deps'])
                                sent[i]['deps'] = output_string
                                
                            else:
                                if '_' != str(sent[i]['deps']) and float(s) >= (stop - dw):
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))', f'{float(s) + dw}', sent[i]['deps'])
                        else:
                            if '|' in sent[i]['deps']:
                                def increment_numbers(match):
                                        number = int(match.group())
                                        if '_' != str(sent[i]['deps']) and number >=  (stop - dw):
                                            return str(number + dw)
                                        return str(number)
                                output_string = re.sub(r'\d+', increment_numbers, sent[i]['deps'])
                                sent[i]['deps'] = output_string

                            s = re.compile(r'(\d+)\:(\w+|\w+:\w+|\w+:\w+:\w+)')
                            if s.fullmatch(sent[i]["deps"]):
                                a = int(s.fullmatch(sent[i]["deps"]).group(1))
                                
                                if '_' != str(sent[i]['deps']) and a > (stop - dw) and '__' not in str(sent[i]['SemClass']):
                                    sent[i]['deps'] = re.sub(r'(\d+\:)', f'{a + dw}:', sent[i]['deps'])

                            if sent[i]['SemClass'] == '__':
                                sent[i]['SemClass'] = '_'

    def merge(self, sent):
        """
        Сливает токены
        """
        dot_number = re.compile(r'\d+\.\d+')
        counter = 0
        null = 0
        while counter != len(sent) - 1:
            c = 0
            if sent[counter]['form'] == '#NULL':
                null += 1
            
            # Если Case = ZeroCase/DativeSpecial или pos = Prefixoid или случаи типа ТУ-154 / 70 - х
            if sent[counter]['pos'] in ('NOUN', 'NUM') and sent[counter]['grammemes'] != None and type(sent[counter]['grammemes']) != str and 'Case' in sent[counter]['grammemes'] and sent[counter]['grammemes']['Case'] == 'ZeroCase' \
                    or sent[counter]['pos'] == 'Prefixoid' and sent[counter]['form'] not in ('бен', 'де') \
                    or sent[counter]['SemClass'] in self.acronim_semrel_set and sent[counter + 1]['form'] == '-' and sent[counter + 2]['SemSlot'] == 'Specifier_Number'\
                    or sent[counter]['pos'] in ('NOUN', 'ADJ') and sent[counter]['grammemes'] != None and type(sent[counter]['grammemes']) != str and 'Case' in sent[counter]['grammemes'] and 'DativeSpecial' in sent[counter]['grammemes']['Case'] \
                    or sent[counter]['form'].isdigit() and sent[counter + 1]['form'] == '-' and sent[counter + 2]['lemma'] in ('й', 'ый') \
                    or sent[counter]['pos'] == 'PROPN' and sent[counter + 1]['form'] == '-' and sent[counter + 2]['form'].startswith('на-') \
                    or sent[counter]['SemSlot'] == 'QuantityForComposite' and sent[counter]['pos'] == 'Invariable':
                
                to_merge_token = sent[counter]['form']
                id_skip = sent[counter]['id']
                if sent[counter + 1]['form'] == '-':    # если слово через тире
                    if sent[counter]['form'].isdigit() and sent[counter + 2]['lemma'] in ('й', 'ый'):
                        new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'] + sent[counter + 2]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'] + sent[counter + 2]['lemma'],
                                    'pos': 'ADJ',
                                    'p0s': sent[counter]['p0s'],
                                    'grammemes': sent[counter]['grammemes'],
                                    'deprel': 'amod',
                                    'deps': sent[counter]['deps'],
                                    'head': sent[counter]['head'],
                                    'misc': sent[counter]['misc'],
                                    'SemSlot': sent[counter]['SemSlot'],
                                    'SemClass': sent[counter]['SemClass']}
                    elif sent[counter]['pos'] == 'PROPN' and sent[counter + 2]['form'].startswith('на-'):
                        new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'] + sent[counter + 2]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'] + sent[counter + 2]['lemma'],
                                    'pos': sent[counter]['pos'],
                                    'p0s': sent[counter]['p0s'],
                                    'grammemes': sent[counter]['grammemes'],
                                    'deprel': sent[counter]['deprel'],
                                    'deps': sent[counter]['deps'],
                                    'head': sent[counter]['head'],
                                    'misc': sent[counter]['misc'],
                                    'SemSlot': sent[counter]['SemSlot'],
                                    'SemClass': sent[counter]['SemClass']}

                    elif sent[counter]['SemClass'] in self.acronim_semrel_set and sent[counter + 2]['SemSlot'] == 'Specifier_Number':
                        new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'] + sent[counter + 2]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'] + sent[counter + 2]['lemma'],
                                    'pos': 'PROPN',
                                    'p0s': sent[counter]['p0s'],
                                    'grammemes': 'Abbr=Yes',
                                    'deprel': sent[counter]['deprel'],
                                    'deps': sent[counter]['deps'],
                                    'head': sent[counter]['head'],
                                    'misc': sent[counter]['misc'],
                                    'SemSlot': sent[counter]['SemSlot'],
                                    'SemClass': sent[counter]['SemClass']}

                    else:
                        new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'] + sent[counter + 2]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'] + sent[counter + 2]['lemma'],
                                    'pos': sent[counter + 2]['pos'],
                                    'p0s': sent[counter + 2]['p0s'],
                                    'grammemes': sent[counter + 2]['grammemes'],
                                    'deprel': sent[counter + 2]['deprel'],
                                    'deps': sent[counter + 2]['deps'],
                                    'head': sent[counter + 2]['head'],
                                    'misc': sent[counter + 2]['misc'],
                                    'SemSlot': sent[counter + 2]['SemSlot'],
                                    'SemClass': sent[counter + 2]['SemClass']}
                        
                    c += 2
                    dic = {k: k for k in range(1, len(sent))}
                    dic[id_skip] = '_'

                    dic[id_skip + 1] = '_'
                    for i in range(id_skip + 2, len(dic) + 1):
                        dic[i] = dic[i] - 2


                    if null >= 1:
                        for j in range(new_token['id'], len(sent) - c):
                            if j == new_token['id']:
                                del sent[j]
                                del sent[j + 1]
                                sent[j] = new_token
                            else:
                                sent[j]['id'] = int(sent[j]['id']) - c
                                    
                    elif null < 1:
                        for j in range(new_token['id'] - 1, len(sent) - c):
                            if j == new_token['id'] - 1:
                                del sent[j]
                                del sent[j + 1]
                                sent[j] = new_token
                            else:
                                if sent[j]['form'] == '#NULL':
                                    sent[j]['id'] = float(sent[j]['id']) - c
                                else:
                                    sent[j]['id'] = int(sent[j]['id']) - c
      
                        
            
                else: # если слово не через тире
                    new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'],
                                    'pos': sent[counter + 1]['pos'],
                                    'p0s': sent[counter + 1]['p0s'],
                                    'grammemes': sent[counter + 1]['grammemes'],
                                    'deprel': sent[counter + 1]['deprel'],
                                    'deps': sent[counter + 1]['deps'],
                                    'head': sent[counter + 1]['head'],
                                    'misc': sent[counter + 1]['deprel'],
                                    'SemSlot': sent[counter + 1]['SemSlot'],
                                    'SemClass': sent[counter + 1]['SemClass']}
                    c += 1
                    dic = {k: k for k in range(1, len(sent))}
                    dic[id_skip] = '_'
                    for i in range(id_skip + 1, len(dic)):
                        dic[i] = dic[i] - 1

                    if null >= 1:
                        for j in range(new_token['id'], len(sent) - c):
                            if j == new_token['id']:
                                del sent[j + 1]
                                sent[j] = new_token
                            else:
                                sent[j]['id'] = int(sent[j]['id']) - c
                                    
                    elif null < 1:
                        for j in range(new_token['id'] - 1, len(sent) - c):
                    
                            if j == new_token['id'] - 1:
                                del sent[j + 1]
                                sent[j] = new_token
                            else:
                                if sent[j]['form'] == '#NULL':
                                    sent[j]['id'] = float(sent[j]['id']) - c
                                else:
                                    sent[j]['id'] = int(sent[j]['id']) - c

                for i in range(len(sent)):
                    for item in dic:
                        if sent[i]['head'] == item:
                            a = sent[i]['head']
                            if dic[item] != '_':
                                sent[i]['head'] = dic[item]
                            if sent[i]['head'] == sent[i]['id']:
                                sent[i]['head'] -= 1
                                
                            s = re.match(r'(\d+\.\d+|\d+)', sent[i]["deps"]).group(1)
                            if '.' in s:
                                s = float(s)
                            else:
                                s = int(s)
                            # print(sent[i]['form'], new_token['id'], s)
                            if s == new_token['id'] and sent[i]['id'] < new_token['id']:
                                pass
                            elif s >= new_token['id'] and '|' not in sent[i]["deps"]:
                                
                                sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{s - c}:', sent[i]['deps'])
                            
                            elif '|' in sent[i]["deps"] and '_' != str(sent[i]['deps']): 
                                if dot_number.match(str(sent[i]['deps'])):
                                    def increment_numbers(match):
                                            number = float(match.group())
                                            if '_' != str(sent[i]['deps']) and number >= new_token['id']:
                                                return str(number - c)
                                            return str(number)
                                    output_string = re.sub(r'\d+|\d+\.\d+\.\d+|\d+\.\d+', increment_numbers, sent[i]['deps'])
                                    sent[i]['deps'] = output_string
                                else:
                                    def increment_numbers(match):
                                            number = int(match.group())
                                            if '_' != str(sent[i]['deps']) and number >= new_token['id']:
                                                return str(number - c)
                                            return str(number)
                                    output_string = re.sub(r'\d+|\d+\.\d+\.\d+|\d+\.\d+', increment_numbers, sent[i]['deps'])
                                    sent[i]['deps'] = output_string
            else:
                counter += 1
    def pos_invariable_fix(self, token, pos):
        """
        Меняет часть речи, если она invariable
        """
        dict_of_pairs = {}

        with open(self.invariable, 'r', encoding='utf8') as pos_txt:
            for line in pos_txt:
                t, ps = line.strip('\n').split('\t')
                dict_of_pairs[t] = ps

            if token.lower() in dict_of_pairs:
                pos = dict_of_pairs[token.lower()]
        pos_txt.close()

        return pos
