import re
# пофиксить леммы у личных местоимений - done
# #Number - проверить hash lemma set - done
# 's притяжательное разбить на токены - тоже сделаю в этом модуле

#что за  эти #where и #which для #NULL, надо или их менять/убирать, в корпусах вообще нет таких токенов? 
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
                      'm': 'million'} 
        
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

    def bounded_neg(self, sent):

        '''разбивает n't и меняет индексацию в таких предложениях'''

        neg_bounded = re.compile(r'[A-za-z]+n\'t')
        first_ind = re.compile(r'(\d+)-(\d+)')
        divided_words = []
        c = 0
        null = 0
        b = 0

        for word in sent:
            if word['form'] == '#NULL':
                null += 1      

        for word in sent:
            divided_words = []
            if neg_bounded.fullmatch(word['form']):
                parts = re.compile(r'[A-za-z]+n\'t').fullmatch(word['form'])
                first_token_id = word['id']
                new_word = {'id': f'{first_token_id}-{first_token_id + 1}', 'form': parts[0], 'lemma': '_', 'pos': '_', 'p0s': '_', 'grammemes': '_',
                            'head': '_', 'deprel': '_', 'deps': '_', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                
                divided_words.append(new_word)
                new_word = {'id': first_token_id, 'form': parts[0].replace('n\'t',''), 'lemma': word['lemma'], 'pos': word['pos'], 'p0s': word['p0s'], 'grammemes': word['grammemes'],
                            'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                c+=1
                divided_words.append(new_word)
                new_word = {'id': first_token_id + 1, 'form': 'n\'t', 'lemma': 'not', 'pos': 'PART', 'p0s': '_', 'grammemes': 'Polarity=Neg',
                            'head': word['head'] + 1, 'deprel': 'advmod', 'deps': f'{word["head"] + 1}:advmod', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                c+=1
                divided_words.append(new_word)

                b+=1


                dic = {k: k for k in range(1, len(sent))}
                start = sent.index(word)
                for i in divided_words:
                    sent.insert(start, i)
                    start += 1
                stop = sent.index(word)
                sent.remove(word)
                for old_word in sent[stop:]:
                    # old_word['id'] += len(divided_words) - c
                    try:
                        old_word['id'] += len(divided_words) - c
                    except TypeError:
                        old_word['id'] = len(divided_words) - c + int(re.search(first_ind, old_word['id']).group(1))
                        
                count = 1
                c = 0
                for i in range(len(sent)):
                    if sent[i]['SemClass'] == '__':
                        continue
                    else:
                        dic[count] = sent[i]['id']
                        count += 1
                    if '.' in sent[i]['deps'] and float(re.findall(r'\d+\.\d+\.\d+|\d+\.\d+|\d+', sent[i]['deps'])[0]) >= first_token_id:
                        for item in dic:
                            if sent[i]['head'] == item:
                                null = (float(re.findall(r'\d+\.\d+\.\d+|\d+\.\d+|\d+', sent[i]['deps'])[0]) + 1)
                                sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{a}:',sent[i]['deps'])  
                                if sent[i]['head'] >=  first_token_id:
                                    sent[i]['head'] = sent[i]['head'] + 1
                                break

                for i in range(len(sent)):  
                    if sent[i]['SemClass'] == '__':
                        sent[i]['SemClass'] = '_'
                        continue         
                    if '.' not in sent[i]['deps'] and type(sent[i]['head']) == int and sent[i]['head'] > first_token_id:
                        if sent[i]['head'] != '_':
                            for item in dic:
                                if sent[i]['head'] == item:
                                    if null or sent[i]['SemClass'] == '_':
                                        sent[i]['head'] = sent[i]['head'] + b
                                    else:
                                        sent[i]['head'] = dic[item]
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break

                    if sent[i]['head'] == '_' and sent[i]['lemma'] != '_' and float(re.findall(r'\d+\.\d+\.\d+|\d+\.\d+|\d+', sent[i]['deps'])[0]) >= first_token_id:
                        for item in dic:
                            sent[i]['head'] = int(re.findall(r'\d+\.\d+\.\d+|\d+\.\d+|\d+', sent[i]['deps'])[0])
                            if sent[i]['head'] == item:
                                null = int(re.findall(r'\d+\.\d+\.\d+|\d+\.\d+|\d+', sent[i]['deps'])[0])
                                sent[i]['head'] = sent[i]['head']
                                sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{null + 1}:', sent[i]['deps'])
                                sent[i]['head'] = '_'
                                break


                    

    def bounded_s(self, sent, bounded_fgn):

        """
        разбивает токены, заканчивающиеся на 's и s и меняет индексацию в таких предложениях'
        """

        number_bounded = re.compile(r'[A-za-z]+\'s') # she's
        number0_bounded = re.compile(r'[A-za-z]+s\'') # Elvis'
        number1_bounded = re.compile(r'let\'s') # let's
        first_ind = re.compile(r'(\d+)-(\d+)') # 10-12
        divided_words = []
        c = 0
        number_of_s = 0
        for word in sent:
            divided_words = []
            c = 0
            
            if number0_bounded.fullmatch(word['form']):
                    # s'
                    , csv_dict, bounded_token_list
                    first_token_id = word['id'] + c
                    new_word = {'id': f'{first_token_id}-{first_token_id+1}', 'form': word['form'], 'lemma': '_', 'pos': '_', 'p0s': '_', 'grammemes': '_',
                                'head': '_', 'deprel': '_', 'deps': '_', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                    c+=1
                    divided_words.append(new_word)
                    new_word = {'id': first_token_id, 'form': word['form'].replace('\'',''), 'lemma': word['lemma'], 'pos': word['pos'], 'p0s': word['p0s'], 'grammemes': word['grammemes'],
                                'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                    c+=1
                    divided_words.append(new_word)
                    new_word = {'id': word['id'] + 1, 'form': '\'', 'lemma': '\'s', 'pos': 'PART', 'p0s': '_', 'grammemes': '_',
                                'head': first_token_id, 'deprel': 'case', 'deps': f'{first_token_id}:case', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                    c+=1
                    divided_words.append(new_word)

                    dic = {k: k for k in range(1, len(sent))}
                    start = sent.index(word)

                    for i in divided_words:
                        sent.insert(start, i)
                        start += 1
                    stop = sent.index(word)

                    sent.remove(word)
                    for old_word in sent[stop:]:
                        try:
                            old_word['id'] = int(old_word['id']) + 1
                        except ValueError:
                            old_word['id'] = f'{int(re.search(first_ind, old_word["id"]).group(1)) + 1}-{int(re.search(first_ind, old_word["id"]).group(2)) + 1}'

                    count = 1
                    dd = re.compile(r'\d+-\d+')
                    cc = re.compile(r'\d+\.\d+')
                    for i in range(len(sent)):
                        if sent[i]['SemClass'] == '__' or dd.fullmatch(str(sent[i]['id'])) or cc.fullmatch(str(sent[i]['id'])):
                            continue
                        else:
                            dic[count] = sent[i]['id']
                            count += 1
                        print(dic)
                        
                    for i in range(len(sent)):
                        if sent[i]['SemClass'] == '__':
                            sent[i]['SemClass'] = '_'
                            continue
                        if cc.fullmatch(str(sent[i]['head'])):
                            sent[i]['head'] += 1
                        if cc.match(str(sent[i]['deps'])) and bounded_fgn == 1:
                            # если это второе слово с 's и deps в формате 16.1
                            s = re.compile(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))').match(sent[i]["deps"]).group(0)
                            sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))', f'{float(s) + 1}', sent[i]['deps'])
                        elif cc.match(str(sent[i]['deps'])) and bounded_fgn != 1: 
                            # если это не второе слово с 's и deps в формате 16.1
                            print('')

                        else:
                            for item in dic:
                                if sent[i]['head'] == item:
                                    sent[i]['head'] = dic[item]
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break
                    bounded_fgn -= 1
 
            

            if number1_bounded.fullmatch(word['form'].lower()):
                    # let's
                    parts = re.compile(r'let\'s').findall(word['form'])
                    first_token_id = word['id'] + c
                    new_word = {'id': f'{first_token_id}-{first_token_id+1}', 'form':  'let\'s', 'lemma': '_', 'pos': '_', 'p0s': '_', 'grammemes': '_',
                                'head': '_', 'deprel': '_', 'deps': '_', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                    c+=1
                    divided_words.append(new_word)
                    new_word = {'id': first_token_id, 'form': word['form'].replace('\'s',''), 'lemma': 'let', 'pos': 'VERB', 'p0s': word['p0s'], 'grammemes': '_',
                                'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                    c+=1
                    divided_words.append(new_word)
                    new_word = {'id': word['id'] + 1, 'form': '\'s', 'lemma': 'we', 'pos': 'PRON', 'p0s': '_', 'grammemes': 'Case=Acc|Number=Plur|Person=1|PronType=Prs',
                                'head': first_token_id, 'deprel': 'obj', 'deps': f'{first_token_id}:obj', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                    c+=1
                    divided_words.append(new_word)

                    dic = {k: k for k in range(1, len(sent))}
                    start = sent.index(word)
                    for i in divided_words:
                        sent.insert(start, i)
                        start += 1
                    stop = sent.index(word)
                    sent.remove(word)
                    for old_word in sent[stop:]:
                        old_word['id'] += 1
                    count = 1
                    dd = re.compile(r'\d+-\d+')
                    cc = re.compile(r'\d+\.\d+')
                    for i in range(len(sent)):
                        if sent[i]['SemClass'] == '__' or dd.fullmatch(str(sent[i]['id'])) or cc.fullmatch(str(sent[i]['id'])):
                            continue
                        else:
                            dic[count] = sent[i]['id']
                            count += 1
                        
                    for i in range(len(sent)):
                        if sent[i]['SemClass'] == '__':
                            sent[i]['SemClass'] = '_'
                            continue
                        if cc.fullmatch(str(sent[i]['head'])):
                            sent[i]['head'] += 1
                        if cc.match(str(sent[i]['deps'])) and bounded_fgn == 1:
                            s = re.compile(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))').match(sent[i]["deps"]).group(0)
                            sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))', f'{float(s) + 1}', sent[i]['deps'])
                        elif cc.match(str(sent[i]['deps'])) and bounded_fgn != 1: 
                            print('')
 

                        else:
                            for item in dic:
                                if sent[i]['head'] == item:
                                    sent[i]['head'] = dic[item]
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break
                    bounded_fgn-=1



            elif number_bounded.fullmatch(word['form']):
                    # 's
                    parts = re.compile(r'[A-za-z]+\'s').findall(word['form'])
                    first_token_id = word['id']
                    new_word = {'id': f'{first_token_id}-{first_token_id + 1}', 'form': parts[0], 'lemma': '_', 'pos': '_', 'p0s': '_', 'grammemes': '_',
                                'head': '_', 'deprel': '_', 'deps': '_', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                    
                    divided_words.append(new_word)
                    new_word = {'id': first_token_id, 'form': parts[0].replace('\'s',''), 'lemma': parts[0].replace('\'s',''), 'pos': word['pos'], 'p0s': word['p0s'], 'grammemes': word['grammemes'],
                                'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                    c+=1
                    divided_words.append(new_word)
                    new_word = {'id': first_token_id + 1, 'form': '\'s', 'lemma': '\'s', 'pos': 'PART', 'p0s': '_', 'grammemes': '_',
                                'head': f'{first_token_id}', 'deprel': 'case', 'deps': f'{first_token_id}:case', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                    c+=1
                    divided_words.append(new_word)

                    dic = {k: k for k in range(1, len(sent))}
                    
                    start = sent.index(word)
                    for i in divided_words:
                        sent.insert(start, i)
                        start += 1
                    stop = sent.index(word)
                    sent.remove(word)
                    for old_word in sent[stop:]:
                        try:
                            old_word['id'] = int(old_word['id']) + 1
                        except ValueError:
                            old_word['id'] = f'{int(re.search(first_ind, old_word["id"]).group(1)) + 1}-{int(re.search(first_ind, old_word["id"]).group(2)) + 1}'
                    count = 1
                    dd = re.compile(r'\d+-\d+')
                    cc = re.compile(r'\d+\.\d+')
                    for i in range(len(sent)):
                        if sent[i]['SemClass'] == '__' or dd.fullmatch(str(sent[i]['id'])) or cc.fullmatch(str(sent[i]['id'])):
                            continue
                        else:
                            dic[count] = sent[i]['id']
                            count += 1

                        
                    for i in range(len(sent)):
                        if sent[i]['SemClass'] == '__':
                            sent[i]['SemClass'] = '_'
                            continue
                        if cc.fullmatch(str(sent[i]['head'])):
                            sent[i]['head'] += 1
                        if cc.match(str(sent[i]['deps'])) and bounded_fgn == 1:
                            s = re.compile(r'((\d+\.\d+\.\d+|\d+\.\d+))').match(sent[i]["deps"]).group(0)
                            if '|' in sent[i]['deps']:
                                d = re.match(r'.+:.+\|(\d+)', sent[i]['deps']).group(1)
                                if sent[i]['head'] == item:
                                    sent[i]['head'] = dic[item]
                                sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+))', f'{float(s) + 1}', sent[i]['deps'])
                                sent[i]['deps'] = re.sub(r'(\|\d+)', f'|{int(d) + 1}', sent[i]['deps'])
                            else:
                                sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))', f'{float(s) + 1}', sent[i]['deps'])
                        else:
                            for item in dic:
                                if sent[i]['head'] == item:
                                    sent[i]['head'] = dic[item]
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{sent[i]["head"]}:', sent[i]['deps']) 
                                    break
                    bounded_fgn -= 1
                          
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

        for word in sent:
            divided_words = []
            c = 0
            if word['form'].lower() in bounded_token_list:
                for token in csv_dict.items():
                    if token[0].lower() == word['form'].lower():
                        for part in token[1]:
                            if part['head'] != '_':
                                head = int(part['head'])#upd: исправила
                            #elif part['head'] == 'None':
                                #head = 0
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
                        cc = re.compile(r'\d+\.\d')
                        for i in range(len(sent)):
                            if sent[i]['SemClass'] == '__' or cc.fullmatch(str(sent[i]['id'])):
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
                                        sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{dic[item]}:', sent[i]['deps'])
                                        break
                        break



 
                
                    



