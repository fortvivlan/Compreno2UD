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
    
    def pos_s(self, sent):
        """
        Разделяет токены, с притяжательным s
        """

        for word in sent:
            divided_words = []
            c = 0
            if word['form'].lower() == re.compile(r"\w+'s"):
                for token in csv_dict.items():
                    if token[0].lower() == word['form'].lower():#- тут добавлю, когда размечу все омонимичные токены #token[0].startswith(word['form'].lower()) and word['pos'] in token[0] 
                        for part in token[1]:
                            if part['head'] != '_':
                                head = int(part['head'])#upd: исправила
                            #elif part['head'] == 'None':
                                #head = 0
                            else:
                                head = word['head']
                            new_word = {'id': word['id'] + c, 'form': part['form'], 'lemma': part['lemma'].lower(),
                                        'pos': part['pos'], 'grammemes': part['grammemes'], 'deprel': part['deprel'], 'head': head,
                                        'SemSlot': '_', 'SemClass': '__'}

                            if new_word['head'] != 0:
                                new_word['head'] = new_word['id'] - new_word['head']
                            else:
                                new_word['head'] = word['head']
                                new_word['SemSlot'] = new_word['SemSlot']
                                new_word['SemClass'] = word['SemClass']
                                new_word['deprel'] = word['deprel']
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

                if word['form'].lower() == re.compile(r"\w+'s"):
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

