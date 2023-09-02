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

        self.abbrs = {'m': 'million'}
    def fix_lemmas_en(self, token, lemma, pos, feats, semslot) -> str:
        """
        Изменяет некорректные леммы.
        """

        if lemma in self.hash_lemma_set:
            lemma = token

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
        2.(может эти тоже захардкодить? и добавить в список пробельных?)
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
                                    sent[i]['deps'] = re.sub(r'\d+\:', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break
                    break
            
            elif number0_bounded.fullmatch(word['form']):
                    print('проверка')
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
                                    sent[i]['deps'] = re.sub(r'\d+\:', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break
                    break
            
            elif number_bounded.fullmatch(word['form']):
                    parts = re.compile(r'[A-za-z]+\'s').findall(word['form'])
                    first_token_id = word['id'] + c
                    new_word = {'id': f'{first_token_id}-{first_token_id+1}', 'form': parts[0], 'lemma': '_', 'pos': '_', 'p0s': '_', 'grammemes': '_',
                                'head': '_', 'deprel': '_', 'deps': '_', 'misc': '_', 'SemSlot': '_', 'SemClass': '__'}
                    c+=1
                    divided_words.append(new_word)
                    new_word = {'id': first_token_id, 'form': parts[0].replace('\'s',''), 'lemma': parts[0].replace('\'s',''), 'pos': word['pos'], 'p0s': word['p0s'], 'grammemes': word['grammemes'],
                                'head': word['head'], 'deprel': word['deprel'], 'deps': word['deps'], 'misc': word['misc'], 'SemSlot': word['SemSlot'], 'SemClass': word['SemClass']}
                    c+=1
                    divided_words.append(new_word)
                    new_word = {'id': word['id'] + 1, 'form': '\'s', 'lemma': '\'s', 'pos': 'PART', 'p0s': '_', 'grammemes': '_',
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
                                    sent[i]['deps'] = re.sub(r'\d+\:', f'{sent[i]["head"]}:', sent[i]['deps'])
                                    break
                    break

