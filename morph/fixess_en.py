import re
class Fixes_en:

    def __init__(self):
        self.hash_lemma_set = {'#Acronym',
                                '#ElliptedNoun',
                                '#ElliptedVerb',
                                '#Expression',
                                '#Number',
                                '#Substantivizer',
                                '#UnknownName',
                                '#UnknownWord',
                                '#where',
                                '#which'} #для русского сетик был больше, но в этом датасете были только такие леммы с хэштегом

        self.abbrs = {'m.': 'million',
                      'm': 'million'} #здесь переделать, давать лемму еще по семантике
    def fix_lemmas_en(self, token, lemma, pos, feats, semslot) -> str:
        """
        Исправляет некорректные леммы.
        """

        if lemma in self.hash_lemma_set:
            lemma = token

        if token == '\'d' and lemma == 'will':
            lemma = 'would'

        if token.lower() == 'would':
            lemma = 'will'
            
        if token.lower() == 'should':
            lemma = 'should'

        if token.lower() == 'she':
            lemma = 'she'
        elif token.lower() == 'it':
            lemma = 'it'
        elif token.lower() == 'they':
            lemma = 'they'
        elif token.lower() == 'them':
            lemma = 'they'
        elif token.lower() == 'her' and lemma == 'he':
            lemma = 'she'#у нас есть два вида her(омонимичных), у одного правильно лемма her стоит, у другого he, его мы и исправляем

        return lemma
    


    def null_check(self, sent):

        '''меняет индексацию при .0000000000001'''

        br = re.compile(r'\d+\.\d+01')
        for word in sent:
            if br.fullmatch(str(word['id'])):
                word['id'] = re.sub(r'(\.\d+01)', '.1', str(word['id']))
            if br.match(str(word['head'])):
                word['head'] = re.sub(r'(\.\d+01)', '.1', str(word['head']))
            if br.match(str(word['deps'])):
                word['deps'] = re.sub(r'(\.\d+01)', '.1', str(word['deps']))


    def bounded_tokens(self, sent):
        '''разбивает токены и добавляет строчку
        '''
        # patterns
        num_bounded = re.compile(r'(\d+-\d+) (\d+-\d+)')
        num3_bounded = re.compile(r'(\d+-\d+) (\d+-\d+) (\d+-\d+)')
        num4_bounded = re.compile(r'(\d+-\d+) (\d+-\d+) (\d+-\d+) (\d+-\d+)')
        cannot = re.compile(r'cannot')
        neg_bounded = re.compile(r'[A-za-z]+n\'t') # n't
        double_ind = re.compile(r'(\d+)-(\d+)') # indexes like 12-13, 1-2 etc
        s_bounded = re.compile(r'[A-za-z]+\'s') # she's
        s_end_bounded = re.compile(r'[A-za-z]+s\'') # Elvis'
        lets_bounded = re.compile(r'let\'s') # let's
        dot_number = re.compile(r'\d+\.\d+') # 12.1
        number_of_bounded_words = 0
        added_line = 0
        null = 0

        for word in sent:
            divided_words = []
            stop = 0
            if word['form'] == '#NULL':

                null += 1
            if num_bounded.fullmatch(word['form']) or num3_bounded.fullmatch(word['form']) or num4_bounded.fullmatch(word['form']) or s_bounded.fullmatch(word['form']) or neg_bounded.fullmatch(word['form']) or s_end_bounded.fullmatch(word['form']) or lets_bounded.fullmatch(word['form']) or cannot.fullmatch(word['form']):
                    first_token_id = word['id']
                    if s_bounded.fullmatch(word['form']) or neg_bounded.fullmatch(word['form']) or s_end_bounded.fullmatch(word['form']) or lets_bounded.fullmatch(word['form']) or cannot.fullmatch(word['form']):
                        new_word = {'id': f'{first_token_id}-{first_token_id + 1}',
                                    'form': word['form'],
                                    'lemma': '_', 'pos': '_',
                                    'p0s': '_', 'grammemes': '_',
                                    'head': '_',
                                    'deprel': '_', 
                                    'deps': '_', 
                                    'misc': '_', 
                                    'SemSlot': '_', 
                                    'SemClass': '__'}
                        divided_words.append(new_word)# e.g. 12-13 window's 

                        

                    # num3
                    if num3_bounded.fullmatch(word['form']):
                        if first_token_id > word['head']:
                            new_word = {'id': first_token_id, 'form': num3_bounded.fullmatch(word["lemma"]).group(1), 'lemma':  num3_bounded.fullmatch(word["lemma"]).group(1), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                    'head': word['head'], 'deprel': word['deprel'], 'deps': f'{word["deps"]}', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                            divided_words.append(new_word)
                        else:
                            new_word = {'id': first_token_id, 'form': num4_bounded.fullmatch(word["lemma"]).group(1), 'lemma':  num4_bounded.fullmatch(word["lemma"]).group(1), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                    'head': word['head'] + 1, 'deprel': word['deprel'], 'deps': f'{word["head"] + 1}:{word["deprel"]}', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                            divided_words.append(new_word)

                        new_word = {'id': first_token_id + 1, 'form': num3_bounded.fullmatch(word["lemma"]).group(2), 'lemma': num3_bounded.fullmatch(word["lemma"]).group(2), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                'head': first_token_id, 'deprel': 'flat', 'deps': f'{first_token_id}:flat', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)        
                        new_word = {'id': first_token_id + 2, 'form': num3_bounded.fullmatch(word["lemma"]).group(3), 'lemma': num3_bounded.fullmatch(word["lemma"]).group(3), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                'head': first_token_id, 'deprel': 'flat', 'deps': f'{first_token_id}:flat', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)
                        added = 2
                        

                    # num4
                    if num4_bounded.fullmatch(word['form']):
                        if first_token_id > word['head']:
                            new_word = {'id': first_token_id, 'form': num4_bounded.fullmatch(word["lemma"]).group(1), 'lemma':  num4_bounded.fullmatch(word["lemma"]).group(1), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                    'head': word['head'], 'deprel': word['deprel'], 'deps': f'{word["deps"]}', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                            divided_words.append(new_word)
                        else:
                            new_word = {'id': first_token_id, 'form': num4_bounded.fullmatch(word["lemma"]).group(1), 'lemma':  num4_bounded.fullmatch(word["lemma"]).group(1), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                    'head': word['head'] + 2, 'deprel': word['deprel'], 'deps': f'{word["head"] + 2}:{word["deprel"]}', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                            divided_words.append(new_word)

                        new_word = {'id': first_token_id + 1, 'form': num4_bounded.fullmatch(word["lemma"]).group(2), 'lemma': num4_bounded.fullmatch(word["lemma"]).group(2), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                'head': first_token_id, 'deprel': 'flat', 'deps': f'{first_token_id}:flat', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)  

                        new_word = {'id': first_token_id + 2, 'form': num4_bounded.fullmatch(word["lemma"]).group(3), 'lemma': num4_bounded.fullmatch(word["lemma"]).group(3), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                'head': first_token_id, 'deprel': 'flat', 'deps': f'{first_token_id}:flat', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)
      
                        new_word = {'id': first_token_id + 3, 'form': num4_bounded.fullmatch(word["lemma"]).group(4), 'lemma': num4_bounded.fullmatch(word["lemma"]).group(4), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                'head': first_token_id, 'deprel': 'flat', 'deps': f'{first_token_id}:flat', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)
                        added = 3
                        
                    #num
                    if num_bounded.fullmatch(word['form']):
                        new_word = {'id': first_token_id, 'form': num_bounded.fullmatch(word["lemma"]).group(1), 'lemma':  num_bounded.fullmatch(word["lemma"]).group(1), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                'head': word['head'], 'deprel': word['deprel'], 'deps': f'{word["deps"]}', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)

                        new_word = {'id': first_token_id + 1, 'form': num_bounded.fullmatch(word["lemma"]).group(2), 'lemma': num_bounded.fullmatch(word["lemma"]).group(2), 'pos': 'NUM', 'p0s': word['p0s'], 'grammemes': 'NumForm=Digit|NumType=Card',
                                'head': word['head'], 'deprel': 'flat', 'deps': f'{word["head"]}:flat', 'misc': word['misc'], 'SemSlot': '_', 'SemClass': '__'}
                        divided_words.append(new_word) 
                        added = 1
                        
                    #cannot
                    if cannot.fullmatch(word['form']):
                        new_word = {'id': first_token_id, 'form': 'can', 'lemma': 'can', 'pos': 'AUX', 'p0s': word['p0s'], 'grammemes': 'VerbForm=Fin',
                                'head': word['head'], 'deprel': word['deprel'], 'deps': f'{word["head"]}:aux', 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)

                        new_word = {'id': first_token_id + 1, 'form': 'not', 'lemma': 'not', 'pos': 'PART', 'p0s': '_', 'grammemes': 'Polarity=Neg',
                                'head': word['head'], 'deprel': 'advmod', 'deps': f'{word["head"]}:advmod', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                        divided_words.append(new_word) 
                        added = 1
                    # 's
                    if s_bounded.fullmatch(word['form']):
                        parts = s_bounded.findall(word['form'])
                        new_word = {'id': first_token_id, 'form': parts[0].replace('\'s',''), 'lemma': parts[0].replace('\'s',''), 'pos': word['pos'], 'p0s': word['p0s'], 'grammemes': word['grammemes'],
                                'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)
                        new_word = {'id': first_token_id + 1, 'form': '\'s', 'lemma': '\'s', 'pos': 'PART', 'p0s': '_', 'grammemes': '_',
                                'head': word["id"], 'deprel': 'case', 'deps': f'{first_token_id}:case', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
    
                        divided_words.append(new_word) 
                        added = 1
                    # n't
                    elif neg_bounded.fullmatch(word['form']):
                        parts = re.compile(r'[A-za-z]+n\'t').fullmatch(word['form'])
                        new_word = {'id': first_token_id, 'form': parts[0].replace('n\'t',''), 'lemma': word['lemma'], 'pos': word['pos'], 'p0s': word['p0s'], 'grammemes': word['grammemes'],
                            'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)
                        if new_word['deprel'] == 'root':
                            new_word = {'id': first_token_id + 1, 'form': 'n\'t', 'lemma': 'not', 'pos': 'PART', 'p0s': '_', 'grammemes': 'Polarity=Neg',
                                'head': first_token_id, 'deprel': 'advmod', 'deps': f'{first_token_id}:advmod', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                        else:
                            new_word = {'id': first_token_id + 1, 'form': 'n\'t', 'lemma': 'not', 'pos': 'PART', 'p0s': '_', 'grammemes': 'Polarity=Neg',
                                'head': word['head'], 'deprel': 'advmod', 'deps': f'{word["head"]}:advmod', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                        divided_words.append(new_word)
                        added = 1
                    # s'
                    elif s_end_bounded.fullmatch(word['form']):
                        new_word = {'id': first_token_id, 'form': word['form'].replace('\'',''), 'lemma': word['lemma'], 'pos': word['pos'], 'p0s': word['p0s'], 'grammemes': word['grammemes'],
                                'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)

                        new_word = {'id': word['id'] + 1, 'form': '\'', 'lemma': '\'s', 'pos': 'PART', 'p0s': '_', 'grammemes': '_',
                                    'head': first_token_id, 'deprel': 'case', 'deps': f'{first_token_id}:case', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                        divided_words.append(new_word)
                        added = 1
                    # let's
                    elif lets_bounded.fullmatch(word['form']):
                        new_word = {'id': first_token_id, 'form': word['form'].replace('\'s',''), 'lemma': 'let', 'pos': 'VERB', 'p0s': word['p0s'], 'grammemes': '_',
                                    'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                        divided_words.append(new_word)

                        new_word = {'id': word['id'] + 1, 'form': '\'s', 'lemma': 'we', 'pos': 'PRON', 'p0s': '_', 'grammemes': 'Case=Acc|Number=Plur|Person=1|PronType=Prs',
                                    'head': first_token_id, 'deprel': 'obj', 'deps': f'{first_token_id}:obj', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                        divided_words.append(new_word)

                        added = 1

                    if number_of_bounded_words == 0:
                        number_of_bounded_words +=1
                    elif number_of_bounded_words == 1:
                        number_of_bounded_words +=1


                    start = sent.index(word) # индекс, где был пробельный токен e.g. 12 window's -> 11

                    for i in divided_words: # вставляем сюда наши три строчки, из которых токенов только 2 (window, 's)
                        sent.insert(start, i)
                        start += 1
                    stop = sent.index(word) # e.g. 14
                    sent.remove(word) # убираем старый пробельный токен

                    for old_word in sent[stop:]: # меняем все индексы после пробельного (добавляем единицу)
                        try:
                            old_word['id'] = int(old_word['id']) + added
                            
                        except ValueError: # если после этого следуют строки с индексом типа 15-16
                            old_word['id'] = f'{int(re.search(double_ind, old_word["id"]).group(1)) + 1}-{int(re.search(double_ind, old_word["id"]).group(2)) + 1}'


                    # меняем головы и депс по принципу: если head токена > индекса слова, которое разбиваем, то добавляем 1 к голове и депс (на 1 токен становится больше)
                    for i in range(len(sent)):
                        # поменяли головы
                        if '_' not in str(sent[i]['head']) and int(sent[i]['head']) >= (stop - number_of_bounded_words - null) and '.' not in str(sent[i]['head']):
                            sent[i]['head'] = int(sent[i]['head']) + 1


                        # меняем депс
                        # это если в депс есть точка
                        if dot_number.match(str(sent[i]['deps'])):
                            s = re.compile(r'((\d+\.\d+\.\d+|\d+\.\d+))').match(sent[i]["deps"]).group(0)
                            # если в депс есть точка и разделены |

                            # если есть второй |
                            if sent[i]['deps'].count('|') > 1:   
                                d = re.match(r'\d+:.+\|(\d+):.+\|(\d+):.+', sent[i]['deps']).group(1)
                                e = re.match(r'\d+:.+\|(\d+):.+\|(\d+):.+', sent[i]['deps']).group(2) 

                                if '_' not in str(sent[i]['deps']) and int(e) >= (stop - number_of_bounded_words - null):
                                    sent[i]['deps'] = re.sub(e, f'{int(e) + 1}', sent[i]['deps'])
                    
                                # для части до |
                                if '_' not in str(sent[i]['deps']) and float(s) >= (stop - number_of_bounded_words - 1 - null):
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+))', f'{float(s) + 1}', sent[i]['deps'])
                                #для части после |
                                if '_' not in str(sent[i]['deps']) and float(d) >= (stop - number_of_bounded_words - null):
                                    sent[i]['deps'] = re.sub(d, f'{int(d) + 1}', sent[i]['deps'])



                            elif '|' in sent[i]['deps']: 
                                d = re.match(r'.+:.+\|(\d+)', sent[i]['deps']).group(1)
                                # для части до |
                                if '_' not in str(sent[i]['deps']) and float(s) >= (stop - number_of_bounded_words - 1 - null):
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+))', f'{float(s) + 1}', sent[i]['deps'])
                                #для части после |
                                if '_' not in str(sent[i]['deps']) and float(d) >= (stop - number_of_bounded_words - null):
                                    sent[i]['deps'] = re.sub(r'(\|\d+)', f'|{int(d) + 1}', sent[i]['deps'])

                                

                            # если есть точка, но нет |
                            else:
                                if '_' not in str(sent[i]['deps']) and float(s) >= (stop - number_of_bounded_words - 1 - null):
                                   sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))', f'{float(s) + 1}', sent[i]['deps'])



                        # если нет точки в депс
                        else:

                            # если есть разделение | в депс
                            if sent[i]['deps'].count('|') > 1:
                
                                    s = re.match(r'(\d+):.+\|\d+', sent[i]['deps']).group(1)
                                    d = re.match(r'\d+:.+\|(\d+):.+\|(\d+):.+', sent[i]['deps']).group(1)
                                    e = re.match(r'\d+:.+\|(\d+):.+\|(\d+):.+', sent[i]['deps']).group(2) #если есть третий депс

                                    if '_' not in str(sent[i]['deps']) and int(s) >= (stop - number_of_bounded_words - null):
                                        sent[i]['deps'] = re.sub(s, f'{int(s) + 1}', sent[i]['deps'])

                                    # меняем депс после |
                                    if '_' not in str(sent[i]['deps']) and int(d) >= (stop - number_of_bounded_words - null):
                                        sent[i]['deps'] = re.sub(d, f'{int(d) + 1}', sent[i]['deps'])

                                    if '_' not in str(sent[i]['deps']) and int(e) >= (stop - number_of_bounded_words - null):
                                        sent[i]['deps'] = re.sub(e, f'{int(e) + 1}', sent[i]['deps'])
                                    


                            
                            elif '|' in sent[i]['deps']:

                                s = re.match(r'(\d+):.+\|\d+', sent[i]['deps']).group(1)
                                d = re.match(r'\d+:.+\|(\d+)', sent[i]['deps']).group(1)

                                if s > d: 
                                    # меняем депс до |
                                    if '_' != str(sent[i]['deps']) and int(s) >= (stop - number_of_bounded_words - null):
                                        sent[i]['deps'] = re.sub(re.match(r'(\d+):.+\|\d+', sent[i]['deps']).group(1), f'{int(s) + 1}', sent[i]['deps'])


                                    # меняем депс после |
                                    if '_' != str(sent[i]['deps']) and int(d) >= (stop - number_of_bounded_words - null):
                                        sent[i]['deps'] = re.sub(re.match(r'\d+:.+\|(\d+)', sent[i]['deps']).group(1), f'{int(d) + 1}', sent[i]['deps'])


                                if d > s:
                                    # меняем депс после |
                                    if '_' != str(sent[i]['deps']) and int(d) >= (stop - number_of_bounded_words - null):
                                        sent[i]['deps'] = re.sub(re.match(r'\d+:.+\|(\d+)', sent[i]['deps']).group(1), f'{int(d) + 1}', sent[i]['deps'])


                                    if '_' != str(sent[i]['deps']) and int(s) >= (stop - number_of_bounded_words - null):
                                        sent[i]['deps'] = re.sub(re.match(r'(\d+):.+\|\d+', sent[i]['deps']).group(1), f'{int(s) + 1}', sent[i]['deps'])
                            s = re.compile(r'(\d+)\:(\w+|\w+:\w+)')

                            # самый обычный депс без | и .
                            if s.fullmatch(sent[i]["deps"]):
                                a = int(s.fullmatch(sent[i]["deps"]).group(1))
                                if '_' != str(sent[i]['deps']) and a >= (stop - number_of_bounded_words - null):
                                    sent[i]['deps'] = re.sub(r'(\d+\:)', f'{a + 1}:', sent[i]['deps'])



    def new_line1(self, sent):

        """
        добавляет строчку уже разбитым токенам
        """

        counter = 0
        a = len(sent) - 1
        while counter < a: 
                
            if sent[counter]['form'] in {'\'ll', '\'re', '\'ve', '\'d', '\'s', '\'m'} and sent[counter]['pos'] in {'VERB', 'AUX'}:                
                new_token = {'id': f'{sent[counter-1]["id"]}-{sent[counter]["id"]}',
                            'form': sent[counter-1]["form"] + sent[counter]['form'],
                            'lemma': '_',
                            'pos': '_',
                            'p0s': '_',
                            'grammemes': '_',
                            'deprel': '_',
                            'deps': '_',
                            'head': '_',
                            'misc': '_',
                            'SemSlot': '_',
                            'SemClass': '_'}             
                sent.insert(sent.index(sent[counter-1]), new_token)
                counter += 2
                a -= 1 
            else:
                counter += 1

    def csv_div(self, sent, csv_dict, bounded_token_list):

        """
        Разделяет токены, которые есть в доке csv, состоящие из нескольких токенов.
        Меняет индексацию.
        """
        dot_number = re.compile(r'\d+\.\d+')
        number_csv = 0
        null = 0
        for word in sent:
            if word['form'] == '#NULL':
                null += 1
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


                            if part['pos'] == 'PROPN' or part['form'] in ('I', 'II'):
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
                        # print(word['id'], word['lemma'], start, stop, null)
                        sent.remove(word)
                        for old_word in sent[stop:]:
                            old_word['id'] += len(divided_words) - 1
                        stop = stop - null
                        for i in range(len(sent)):
                            # поменяли головы
                            # print(sent[i]['form'], stop, sent[i]['head'], dw)
                            if '_' not in str(sent[i]['head']) and int(sent[i]['head']) >= (stop - dw) and '.' not in str(sent[i]['head']) and '__' not in str(sent[i]['SemClass']):
                                sent[i]['head'] = int(sent[i]['head']) + dw
                                # print(111111111111111)
                            # меняем депс
                            # если есть точка
                            if dot_number.match(str(sent[i]['deps'])):
                                s = re.compile(r'((\d+\.\d+\.\d+|\d+\.\d+))').match(sent[i]["deps"]).group(0)
                                if '|' in sent[i]['deps']:
                                    d = re.match(r'.+:.+\|(\d+)', sent[i]['deps']).group(1)
                                    
                                    if '_' not in str(sent[i]['deps']) and float(s) >= (stop - dw):
                                        sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+))', f'{float(s) + dw}', sent[i]['deps'])
                                    
                                    if '_' not in str(sent[i]['deps']) and float(d) >= (stop - dw) and '.' not in str(sent[i]['deps']):
                                        sent[i]['deps'] = re.sub(r'(\|\d+)', f'|{int(d) + dw}', sent[i]['deps'])
                                    
                                else:
                                    if '_' not in str(sent[i]['deps']) and float(s) >= (stop - dw):
                                        sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))', f'{float(s) + dw}', sent[i]['deps'])
                            # если нет точки
                            else:
                                # если больше одного разделения
                                if sent[i]['deps'].count('|') > 1:
                    
                                    s = re.match(r'(\d+):.+\|\d+', sent[i]['deps']).group(1)
                                    d = re.match(r'\d+:.+\|(\d+):.+\|(\d+):.+', sent[i]['deps']).group(1)
                                    e = re.match(r'\d+:.+\|(\d+):.+\|(\d+):.+', sent[i]['deps']).group(2) #если есть третий депс
                                    if d > e:
                                        if '_' not in str(sent[i]['deps']) and int(s) >= (stop - dw):
                                            sent[i]['deps'] = re.sub(s, f'{int(s) + dw}', sent[i]['deps'])
                                    
                                        if '_' not in str(sent[i]['deps']) and int(d) >= (stop - dw):
                                            sent[i]['deps'] = re.sub(d, f'{int(d) + dw}', sent[i]['deps'])
                          
                                        if '_' not in str(sent[i]['deps']) and int(e) >= (stop - dw):
                                            sent[i]['deps'] = re.sub(e, f'{int(e) + dw}', sent[i]['deps'])
                        
                                    elif d < e: 
                                        if '_' not in str(sent[i]['deps']) and int(s) >= (stop - dw):
                                            sent[i]['deps'] = re.sub(s, f'{int(s) + dw}', sent[i]['deps'])
                        
                                        if '_' not in str(sent[i]['deps']) and int(e) >= (stop - dw):
                                            sent[i]['deps'] = re.sub(e, f'{int(e) + dw}', sent[i]['deps'])
                               
                                        if '_' not in str(sent[i]['deps']) and int(d) >= (stop - dw):
                                            sent[i]['deps'] = re.sub(d, f'{int(d) + dw}', sent[i]['deps'])
                               
                                # если один разделитель
                                elif '|' in sent[i]['deps']:
                                    s = re.match(r'(\d+):.+\|\d+', sent[i]['deps']).group(1)
                                    d = re.match(r'\d+:.+\|(\d+)', sent[i]['deps']).group(1)
                                    
                                    if '_' not in str(sent[i]['deps']) and int(s) >= (stop - dw):
                                        sent[i]['deps'] = re.sub(s, f'{int(s) + dw}', sent[i]['deps'])

                                    if '_' not in str(sent[i]['deps']) and int(d) >= (stop - dw):
                                        sent[i]['deps'] = re.sub(r'(\|\d+)', f'|{int(d) + dw}', sent[i]['deps'])

                                s = re.compile(r'(\d+)\:(\w+|\w+:\w+|\w+:\w+:\w+_\w+|\w+:\w+_\w+)')

                                if s.fullmatch(sent[i]["deps"]):
                                    # print(sent[i]['lemma'], sent[i]['deps'], stop, dw)
                                    a = int(s.fullmatch(sent[i]["deps"]).group(1))
                                    if '_' != str(sent[i]['deps']) and a >= (stop - dw) and '__' not in str(sent[i]['SemClass']):
                                        # print(sent[i]['lemma'], sent[i]['deps'], stop, dw, a, sent[i]['head'])
                                        sent[i]['deps'] = re.sub(r'(\d+\:)', f'{a + dw}:', sent[i]['deps'])

                                if sent[i]['SemClass'] == '__':
                                    sent[i]['SemClass'] = '_'


    def merge(self, sent):
        """
        Сливает токены
        """
        
        counter = 0
        double_ind = 0
        null = 0
        null_id = 100
        merged = ''
        for i in range(len(sent) - 1):
            if sent[i]['form'] == '#NULL':
                null_id = sent[i]['id']
        while counter != len(sent) - 1:
            
            c = 0
            if sent[counter]['lemma'] == '#NULL':
                null += 1

            if (sent[counter]['pos'] == 'Prefixoid' and sent[counter]['form'].lower() in {"o'",  "non", "pre", "re", "multi", "anti", "co", "ex", "e", "un", "pro", "post", "self", "single"}) or (sent[counter + 1]['form'] == 'th' and sent[counter]['pos'] == 'NUM') or ('SurfSlot'in sent[counter] and sent[counter]["SurfSlot"] == 'Modifier_Composite_Hyphen_Adjective') or (sent[counter]['SemClass'] == 'TIME' and sent[counter + 1]['lemma'] == 's'):
                to_merge_token = sent[counter]['form']
                id_skip = sent[counter]['id']
                if sent[counter + 1]['form'] == '-':    # если слово через тире
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
                    merged = 'two'
                    c += 2
                    dic = {k: k for k in range(1, len(sent))}
                    dic[id_skip] = '_'

                    dic[id_skip + 1] = '_'
                    for i in range(id_skip + 2, len(dic) + 1):
                        dic[i] = dic[i] - 2

                    for j in range(new_token['id'] + null - 1, len(sent) - c):
                        if j == new_token['id'] + null - 1:
                            del sent[j]
                            del sent[j + 1]
                            sent[j] = new_token
                        else:

                                sent[j]['id'] = int(sent[j]['id']) - c   

                                
                else: # если слово не через тире
                    if sent[counter]['form'].lower() in {"un", "re", "multi", "anti", "co", "ex", "e", "pro", "post", "self", "single"}:
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
                        
                    elif (sent[counter + 1]['form'] == 'th' and sent[counter]['pos'] == 'NUM') or sent[counter]['form'].lower() == "o'":
                        new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'],
                                    'pos': sent[counter + 1]['pos'],
                                    'p0s': sent[counter + 1]['p0s'],
                                    'grammemes': sent[counter + 1]['grammemes'],
                                    'deprel': sent[counter]['deprel'],
                                    'deps': sent[counter]['deps'],
                                    'head': sent[counter]['head'],
                                    'misc': sent[counter + 1]['deprel'],
                                    'SemSlot': sent[counter + 1]['SemSlot'],
                                    'SemClass': sent[counter + 1]['SemClass']}
                        
                    elif sent[counter + 1]['lemma'] == 's' and sent[counter]['SemClass'] == 'TIME':
                        new_token = {'id': sent[counter]['id'],
                                    'form': to_merge_token + sent[counter + 1]['form'],
                                    'lemma': to_merge_token + sent[counter + 1]['lemma'],
                                    'pos': sent[counter]['pos'],
                                    'p0s': sent[counter]['p0s'],
                                    'grammemes': sent[counter]['grammemes'],
                                    'deprel': sent[counter]['deprel'],
                                    'deps': sent[counter]['deps'],
                                    'head': sent[counter]['head'],
                                    'misc': sent[counter]['deprel'],
                                    'SemSlot': sent[counter]['SemSlot'],
                                    'SemClass': sent[counter]['SemClass']}                        

                    merged = 'one'
                    c += 1
                    dic = {k: k for k in range(1, len(sent))}
                    dic[id_skip] = '_'

                    for i in range(id_skip + 1, len(dic)):
                        dic[i] = dic[i] - 1

                    for j in range(new_token['id'] + null - 1, len(sent) - c):
                        if j == new_token['id'] + null - 1:
                            del sent[j + 1]
                            sent[j] = new_token
                        else:
                            sent[j]['id'] = int(sent[j]['id']) - c


                for i in range(len(sent)):
                        for item in dic:
                            if sent[i]['head'] == item:
                                if dic[item] == '_' or sent[i]['id'] == new_token['id']:
                                    diff = 1
                                else:
                                    # b = sent[i]['head']
                                    if merged == 'two':
                                        diff = 2
                                    elif merged =='one':
                                        diff = 1
                                if sent[i]['head'] > new_token['id']:
                                    # print(sent[i]['lemma'], sent[i]['head'], sent[i]['deps'], very_first, diff)
                                    sent[i]['head'] = sent[i]['head'] - diff
                                very_second = 0


                                
                                # если есть разделитель
                                # если больше одного разделения
                                if sent[i]['deps'].count('|') > 1:
                    
                                    # very_first = re.match(r'(\d+):.+\|\d+', sent[i]['deps']).group(1)
                                    # if '.' in very_first:
                                    #     very_first = float(very_first)
                                    # else:
                                    #     very_first = int(very_first)
                                    very_second = re.match(r'.+:.+\|(\d+|\d+\.\d+).+\|(\d+|\d+\.\d+)', sent[i]['deps']).group(1)
                                    if '.' in very_second:
                                        very_second = float(very_second)
                                    else:
                                        very_second = int(very_second)
                                    print(very_second)
                                    very_third = re.match(r'.+:.+\|(\d+|\d+\.\d+).+\|(\d+|\d+\.\d+).+', sent[i]['deps']).group(2) #если есть третий депс
                                    if '.' in very_third:
                                        very_third = float(very_third)
                                    else:
                                        very_third = int(very_third)
                                    print(sent[i]['lemma'])

                                
                                elif '|' in sent[i]['deps']:
                                    very_second = re.match(r'.+:.+\|(\d+|\d+\.\d+)', sent[i]['deps']).group(1)
                                    if '.' in very_second:
                                        very_second = float(very_second)
                                    else:
                                        very_second = int(very_second)
                                very_first = re.match(r'(\d+\.\d+|\d+)', sent[i]["deps"]).group(1)

                                if '.' in very_first:
                                    very_first = float(very_first)
                                else:
                                    very_first = int(very_first)
                            

                                    
                                # если нет разделителя
                                
                                if very_first > new_token['id'] and '|' not in sent[i]["deps"]:
                                    # print(sent[i]['lemma'], sent[i]['deps'], very_first, diff)
                                    # print(sent[i]['lemma'], very_first, diff, new_token['id'])
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{very_first - diff}:', sent[i]['deps'])


                                # если есть разделитель
                                # если два разделителя

                                if sent[i]['deps'].count('|') > 1:
                                    first = re.match(r'(\d+\.\d+\.\d+|\d+\.\d+|\d+):.+\|(\d+|\d+\.\d+).+(\d+|\d+\.\d+)', sent[i]['deps']).group(1)
                                    second = re.match(r'.+:.+\|(\d+|\d+\.\d+).+\|(\d+|\d+\.\d+)', sent[i]['deps']).group(1)
                                    third = re.match(r'.+:.+\|(\d+|\d+\.\d+).+\|(\d+|\d+\.\d+)', sent[i]['deps']).group(2)
                                    if '.' in first:
                                        first = float(first)
                                    else:
                                        first = int(first)                       
                                    if '.' in second:
                                        second = float(second)
                                    else:
                                        second = int(second)
                                    if '.' in third:
                                        third = float(third)
                                    else:
                                        third = int(third)
                                        
                                    if very_second > very_third: 
                                        if very_first >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(first), f'{first - diff}', sent[i]['deps']) 
                                        
                                        if very_third >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(third), f'{third - diff}', sent[i]['deps'])
                                        if very_second >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(second), f'{second - diff}', sent[i]['deps'])
                                        
                                  
                                    elif very_third > very_second:
                                        if very_first >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(first), f'{first - diff}', sent[i]['deps']) 
                                        
                                        if very_second >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(second), f'{second - diff}', sent[i]['deps'])
                                        if very_third >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(third), f'{third - diff}', sent[i]['deps'])
                                        print(sent[i]['lemma'], diff, second, third, very_third, very_second)
                                        
                                                 

                                # если один разделитель
                                elif '|' in sent[i]["deps"] and '_' not in str(sent[i]['deps']):
                     
                                    first = re.match(r'(\d+\.\d+\.\d+|\d+\.\d+|\d+):.+\|(\d+|\d+\.\d+)', sent[i]['deps']).group(1)
                                    second = re.match(r'.+:.+\|(\d+|\d+\.\d+)', sent[i]['deps']).group(1)

                                    if '.' in first:
                                        first = float(first)
                                    else:
                                        first = int(first)                       
                                    if '.' in second:
                                        second = float(second)
                                    else:
                                        second = int(second)
                
                                    if very_first < very_second: 
                                        if very_first >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(first), f'{first - diff}', sent[i]['deps']) 
                                        if very_second >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(second), f'{second - diff}', sent[i]['deps'])
                                  
                                    elif very_first > very_second:
                                        if very_second >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(second), f'{second - diff}', sent[i]['deps'])
                                        if very_first >= new_token['id']:
                                            sent[i]['deps'] = re.sub(str(first), f'{first - diff}', sent[i]['deps'])       




                            elif sent[i]['lemma'] == '#NULL' and sent[i]['deps'] != '0:root' or sent[i]['head'] == 0 and sent[i]['deps'] != '0:root':
                                # print(11111111111111)
                                if merged == 'two':
                                    diff = 2
                                elif merged =='one':
                                    diff = 1

                                very_second = 0
                                # если есть разделитель
                                if '|' in sent[i]['deps']:
                                    very_second = re.match(r'.+:.+\|(\d+|\d+\.\d+)', sent[i]['deps']).group(1)
                                    if '.' in very_second:
                                        very_second = float(very_second)
                                    else:
                                        very_second = int(very_second)
                                very_first = re.match(r'(\d+\.\d+|\d+)', sent[i]["deps"]).group(1)

                                if '.' in very_first:
                                    very_first = float(very_first)
                                else:
                                    very_first = int(very_first)

                                if very_first >= new_token['id'] and '|' not in sent[i]["deps"]:
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{very_first - diff}:', sent[i]['deps'])
                                    break


                                
            else:
                counter += 1