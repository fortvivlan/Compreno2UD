# -*- coding: utf-8 -*-

import csv
import re

class Fixes:
    def __init__(self, path, invariable):
        #self.path = r'C:\Users\пк\Desktop\compreno2UD (new)\morphology\ImpToPerf.txt'
        #self.invariable = r'C:\Users\пк\Desktop\compreno2UD (new)\morphology\pos_invariable.txt'
        self.path = path
        self.invariable = invariable
        # 'SpecialLexemes': 'Lex_KgSm'
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

        for word in sent:
            divided_words = []
            c = 0
            if word['form'].lower() in bounded_token_list:
                for token in csv_dict.items():
                    if token[0].lower() == word['form'].lower():#- тут добавлю, когда размечу все омонимичные токены #token[0].startswith(word['form'].lower()) and word['pos'] in token[0] 
                        for part in token[1]:
                            if part['head'] != '_':
                                head = int(part['head'])#upd: исправила
                            #elif part['head'] == 'None':
                                #head = 0
                            else:
                                head = word['head']
                            if part['pos'] == 'PROPN' or part['form'] in ('I', 'II'):#с I можно еще подумать
                                new_word = {'id': word['id'] + c, 'form': part['form'], 'lemma': part['lemma'].lower().capitalize(), 'p0s': '_',
                                            'pos': part['pos'], 'grammemes': part['grammemes'], 'deprel': part['deprel'], 'head': head, 'misc': '_',
                                            'SemSlot': '_', 'SemClass': '__'}
                            else:
                                new_word = {'id': word['id'] + c, 'form': part['form'], 'lemma': part['lemma'].lower(), 'p0s': '_',
                                            'pos': part['pos'], 'grammemes': part['grammemes'], 'deprel': part['deprel'], 'head': head, 'misc': '_',
                                            'SemSlot': '_', 'SemClass': '__'}                                

                            if new_word['head'] != 0:
                                new_word['head'] = new_word['id'] - new_word['head']
                            else:
                                new_word['head'] = word['head']
                                new_word['SemSlot'] = new_word['SemSlot']
                                new_word['SemClass'] = word['SemClass']
                                new_word['deprel'] = word['deprel']
                                new_word['misc'] = '_'
                                new_word['p0s'] ='_'
                            if new_word['id'] == 1:
                                new_word['form'] = new_word['form'].title()
                            c += 1
                            divided_words.append(new_word)
                        if word['form'].lower() in ('больше, чем', 'более, чем'):
                            for word in sent:
                                if word['head'] == 0:
                                    b_head = word['id']
                            divided_words[0]['head'] = b_head
                            divided_words[1]['head'] = word['head']
                            divided_words[2]['head'] = word['head']

                        dic = {k: k for k in range(1, len(sent))}
                        start = sent.index(word)
                        for i in divided_words:
                            sent.insert(start, i)
                            start += 1
                        stop = sent.index(word)
                        sent.remove(word)
                        for old_word in sent[stop:]:
                            old_word['id'] += len(divided_words) - 1
                        count = 1
                        for i in range(len(sent)):
                            if sent[i]['SemClass'] == '__':
                                continue
                            else:
                                dic[count] = sent[i]['id']
                                count += 1
                        for i in range(len(sent)):
                            if sent[i]['SemClass'] == '__':
                                sent[i]['SemClass'] = '_'
                                continue
                            else:
                                for item in dic:
                                    if sent[i]['head'] == item:
                                        sent[i]['head'] = dic[item]
                                        break
                        break


    def bounded_foreign(self, sent):
        """
        Разделяет иностранные слова, состоящие из нескольких токенов.
        Разделяет токены типа: 1990-1991
        """

        foreign_bounded_token = re.compile(r'[A-za-z]+ [A-za-z]+')
        number_bounded = re.compile(r'\d+,?\d*?-\d+,?\d*?')
        divided_words = []
        c = 0
        for word in sent:
            divided_words = []
            c = 0
            if foreign_bounded_token.search(word['form']):
                f_parts = word['form'].split()
                first_token_id = word['id'] + c
                new_word = {'id': first_token_id, 'form': f_parts[0], 'lemma': f_parts[0], 'pos': 'X', 'grammemes': 'Foreign=Yes',
                            'deprel': word['deprel'], 'head': word['head'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                divided_words.append(new_word)
                c += 1
                for f_part in f_parts[1:]:
                    new_word = {'id': word['id'] + c, 'form': f_part, 'lemma': f_part, 'pos': '__', 'grammemes': 'Foreign=Yes',
                                'deprel': 'flat:foreign', 'head': first_token_id, 'SemSlot': '_', 'SemClass': word['SemClass']}
                    c += 1
                    divided_words.append(new_word)

                dic = {k: k for k in range(1, len(sent))}
                start = sent.index(word)
                for i in divided_words:
                    sent.insert(start, i)
                    start += 1
                stop = sent.index(word)
                sent.remove(word)
                for old_word in sent[stop:]:
                    old_word['id'] += len(divided_words) - 1
                count = 1
                for i in range(len(sent)):
                    if sent[i]['pos'] == '__':
                        continue
                    else:
                        dic[count] = sent[i]['id']
                        count += 1
                for i in range(len(sent)):
                    if sent[i]['pos'] == '__':
                        if new_word['form'] in ('%', '$', '°', '€', '+', '№', '#', '@', '~', '^', '&'):
                            new_word['pos'] = 'SYM'
                        else:
                            sent[i]['pos'] = 'X'
                        continue
                    else:
                        for item in dic:
                            if sent[i]['head'] == item:
                                sent[i]['head'] = dic[item]
                                break
            elif number_bounded.fullmatch(word['form']) and word['pos'] in ('ADJ', 'NUM') and word['SemSlot'] != 'Specification':
                    parts = re.compile(r'(\d+,?\d*?)(-)(\d+,?\d*?)').findall(word['form'])
                    first_token_id = word['id'] + c
                    new_word = {'id': first_token_id, 'form': parts[0][0], 'lemma': parts[0][0], 'pos': word['pos'], 'grammemes': word['grammemes'],
                                'head': word['head'], 'deprel': word['deprel'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                    c += 1
                    divided_words.append(new_word)
                    new_word = {'id': word['id'] + c, 'form': parts[0][1], 'lemma': parts[0][1], 'pos': '__', 'grammemes': '_',
                                'head': first_token_id + 2, 'deprel': 'punct', 'SemSlot': '_', 'SemClass': 'punct'}
                    c += 1
                    divided_words.append(new_word)
                    new_word = {'id': word['id'] + c, 'form': parts[0][2], 'lemma': parts[0][2], 'pos': '__', 'grammemes': word['grammemes'],
                                'head': first_token_id, 'deprel': word['deprel'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                    c += 1
                    divided_words.append(new_word)

                    dic = {k: k for k in range(1, len(sent))}
                    start = sent.index(word)
                    for i in divided_words:
                        sent.insert(start, i)
                        start += 1
                    stop = sent.index(word)
                    sent.remove(word)
                    for old_word in sent[stop:]:
                        old_word['id'] += len(divided_words) - 1
                    count = 1
                    for i in range(len(sent)):
                        if sent[i]['pos'] == '__':
                            continue
                        else:
                            dic[count] = sent[i]['id']
                            count += 1
                    for i in range(len(sent)):
                        if sent[i]['pos'] == '__':
                            if sent[i]['deprel'] == 'punct':
                                sent[i]['pos'] = 'PUNCT'
                            else:
                                sent[i]['pos'] = word['pos']
                            continue
                        else:
                            for item in dic:
                                if sent[i]['head'] == item:
                                    sent[i]['head'] = dic[item]
                                    break

    def merge(self, sent):
        """
        Сливает токены
        """
        
        counter = 0
        while counter != len(sent) - 1:
            c = 0
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
                                    'grammemes': sent[counter]['grammemes'],
                                    'deprel': 'amod',
                                    'head': sent[counter]['head'],
                                    'SemSlot': sent[counter]['SemSlot'],
                                    'SemClass': sent[counter]['SemClass']}
                    elif sent[counter]['pos'] == 'PROPN' and sent[counter + 2]['form'].startswith('на-'):
                        new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'] + sent[counter + 2]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'] + sent[counter + 2]['lemma'],
                                    'pos': sent[counter]['pos'],
                                    'grammemes': sent[counter]['grammemes'],
                                    'deprel': sent[counter]['deprel'],
                                    'head': sent[counter]['head'],
                                    'SemSlot': sent[counter]['SemSlot'],
                                    'SemClass': sent[counter]['SemClass']}

                    elif sent[counter]['SemClass'] in self.acronim_semrel_set and sent[counter + 2]['SemSlot'] == 'Specifier_Number':
                        new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'] + sent[counter + 2]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'] + sent[counter + 2]['lemma'],
                                    'pos': 'PROPN',
                                    'grammemes': 'Abbr=Yes',
                                    'deprel': sent[counter]['deprel'],
                                    'head': sent[counter]['head'],
                                    'SemSlot': sent[counter]['SemSlot'],
                                    'SemClass': sent[counter]['SemClass']}

                    else:
                        new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'] + sent[counter + 2]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'] + sent[counter + 2]['lemma'],
                                    'pos': sent[counter + 2]['pos'],
                                    'grammemes': sent[counter + 2]['grammemes'],
                                    'deprel': sent[counter + 2]['deprel'],
                                    'head': sent[counter + 2]['head'],
                                    'SemSlot': sent[counter + 2]['SemSlot'],
                                    'SemClass': sent[counter + 2]['SemClass']}
                    c += 2
                    dic = {k: k for k in range(1, len(sent))}
                    dic[id_skip] = '_'
                    dic[id_skip + 1] = '_'
                    for i in range(id_skip + 2, len(dic)):
                        dic[i] = dic[i] - 2

                    for j in range(new_token['id'] - 1, len(sent) - c):
                        if j == new_token['id'] - 1:
                            del sent[j]
                            del sent[j + 1]
                            sent[j] = new_token
                        else:
                            sent[j]['id'] -= c

                    for i in range(len(sent)):
                        for item in dic:
                            if sent[i]['head'] == item:
                                sent[i]['head'] = dic[item]
                                break
                else:   # если слово не через тире
                    new_token = {'id': sent[counter]['id'],
                                'form': to_merge_token + sent[counter + 1]['form'],
                                'lemma': to_merge_token + sent[counter + 1]['lemma'],
                                'pos': sent[counter + 1]['pos'],
                                'grammemes': sent[counter + 1]['grammemes'],
                                'deprel': sent[counter + 1]['deprel'],
                                'head': sent[counter + 1]['head'],
                                'SemSlot': sent[counter + 1]['SemSlot'],
                                'SemClass': sent[counter + 1]['SemClass']}
                    c += 1
                    dic = {k: k for k in range(1, len(sent))}
                    dic[id_skip] = '_'
                    for i in range(id_skip + 1, len(dic)):
                        dic[i] = dic[i] - 1

                    for j in range(new_token['id'] - 1, len(sent) - c):
                        if j == new_token['id'] - 1:
                            sent[j] = new_token
                            del sent[j + 1]
                        else:
                            sent[j]['id'] -= c

                    for i in range(len(sent)):
                        for item in dic:
                            if sent[i]['head'] == item:
                                sent[i]['head'] = dic[item]
                                break
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
