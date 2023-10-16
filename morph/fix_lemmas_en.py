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
                                '#which'}#для русского сетик был больше, но в этом датасете были только такие леммы с хэштегом

        self.abbrs = {'m.': 'million',
                      'm': 'million'}#здесь переделать, давать лемму еще по семантике
        
    def fix_lemmas_en(self, token, lemma, pos, feats, semslot) -> str:
        """
        Изменяет некорректные леммы.
        """

        if lemma in self.hash_lemma_set:
            lemma = token

        if token == '\'d' and lemma == 'will':
            lemma = 'would'

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
    


    #def divide_words(self, sent):
        '''
        1.
        's
        тут у нас есть необычная 's let's, лемму можно захардкодить просто как 'we',
        остальные можно поделить на 2 группы - у притяжательной частички лемма как и токен - 's,
        у сокращения is/has лемма соответственно is/has 
        2.
        где еще есть апострофы:
        I'm - am
        we’re / they’re - are
        they've / we've - have
        had/would - 'd;
        shall/will - 'll
        not - n't
        3.
        для притяжательных существительных во мн.ч. и на -s (Beatles'), у них токен ', лемма 's
        '''
        bounded_s_pattern = re.compile(r'')
        for word in sent:
            divided_words = []
            '''план для 's такой:
                все токены с апострофом разбиваю, а потом по фичам слитого токена смотрю как чего приписывать'''
    def null_check(self, sent):
        br = re.compile(r'\d+\.\d+01')
        broken_id = re.compile(r'\d+01')
        for word in sent:
            if br.fullmatch(str(word['id'])):
                word['id'] = re.sub(r'(\.\d+01)', '.1', str(word['id']))
            if br.match(str(word['head'])):
                word['head'] = re.sub(r'(\.\d+01)', '.1', str(word['head']))
            if br.match(str(word['deps'])):
                word['deps'] = re.sub(r'(\.\d+01)', '.1', str(word['deps']))

    def bounded_neg(self, sent, sent1):
        neg_bounded = re.compile(r'[A-za-z]+n\'t')
        divided_words = []
        c = 0
        a = 0
        b = 0
        for word in sent:
            if word['form'] == '#NULL':
                a += 1        
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
                            'head': first_token_id, 'deprel': 'advmod', 'deps': f'{first_token_id}:advmod', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
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
                    old_word['id'] += len(divided_words) - c
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
                                a = (float(re.findall(r'\d+\.\d+\.\d+|\d+\.\d+|\d+', sent[i]['deps'])[0]) + 1)
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
                                    if a or sent[i]['SemClass'] == '_':
                                        sent[i]['head'] = sent[i]['head'] + b
                                    else:
                                        sent[i]['head'] = dic[item]
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break

                    if sent[i]['head'] == '_' and sent[i]['lemma'] != '_' and float(re.findall(r'\d+\.\d+\.\d+|\d+\.\d+|\d+', sent[i]['deps'])[0]) >= first_token_id:
                        for item in dic:
                            sent[i]['head'] = int(re.findall(r'\d+\.\d+\.\d+|\d+\.\d+|\d+', sent[i]['deps'])[0])
                            if sent[i]['head'] == item:
                                a = int(re.findall(r'\d+\.\d+\.\d+|\d+\.\d+|\d+', sent[i]['deps'])[0])
                                sent[i]['head'] = sent[i]['head']
                                sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{a + 1}:', sent[i]['deps'])
                                sent[i]['head'] = '_'
                                break


                    

    def bounded_s(self, sent):
        """
        разбивает токены, заканчивающиеся на 's и s'
        """

        number_bounded = re.compile(r'[A-za-z]+\'s')
        number0_bounded = re.compile(r'[A-za-z]+s\'')
        number1_bounded = re.compile(r'let\'s')
        divided_words = []
        c = 0
        for word in sent:
            divided_words = []
            c = 0
            if number1_bounded.fullmatch(word['form'].lower()):
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
                        old_word['id'] += len(divided_words) - 2
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
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break
                    break
            
            
            if number0_bounded.fullmatch(word['form']):
                    parts = number0_bounded.findall(word['form'])
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
                        old_word['id'] += len(divided_words) - 2
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
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break
                    break
            





            if number_bounded.fullmatch(word['form']):
                    parts = re.compile(r'[A-za-z]+\'s').findall(word['form'])
                    first_token_id = word['id']
                    new_word = {'id': f'{first_token_id}-{first_token_id+1}', 'form': parts[0], 'lemma': '_', 'pos': '_', 'p0s': '_', 'grammemes': '_',
                                'head': '_', 'deprel': '_', 'deps': '_', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                    c+=1
                    divided_words.append(new_word)
                    new_word = {'id': first_token_id, 'form': parts[0].replace('\'s',''), 'lemma': parts[0].replace('\'s',''), 'pos': word['pos'], 'p0s': word['p0s'], 'grammemes': word['grammemes'],
                                'head': word['head'] + 1, 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                    
                    divided_words.append(new_word)
                    new_word = {'id': first_token_id + 1, 'form': '\'s', 'lemma': '\'s', 'pos': 'PART', 'p0s': '_', 'grammemes': '_',
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
                        old_word['id'] += len(divided_words) - 2
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
                                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break
                    


            
                    '''elif a == 1:
                        for i in range(len(sent)):
                            if sent[i]['SemClass'] == '__':
                                sent[i]['SemClass'] = '_'
                                continue
                            else:
                                for item in dic:
                                    if sent[i]['head'] == item:
                                        sent[i]['head'] = dic[item]
                                        sent[i]['deps'] = re.sub(r'.+\:', f'{sent[i]["head"]}:', sent[i]['deps'])
                                        break
                        break     '''              

                    
    def new_line1(self, sent):
        """
        добавляет строчку уже разбитым токенам
        """
        counter = 0
        a = len(sent) - 1
        while counter < a:     
            if sent[counter]['form'] == '\'ll' or sent[counter]['form'] == '\'re' or sent[counter]['form'] == '\'ve' or sent[counter]['form'] == '\'d' or sent[counter]['form'] == '\'s' and sent[counter]['pos'] == 'AUX' or sent[counter]['form'] == '\'m': 
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
                                        sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+)\:)', f'{dic[item]}:', sent[i]['deps'])
                                        break
                        break



 
                
                    



