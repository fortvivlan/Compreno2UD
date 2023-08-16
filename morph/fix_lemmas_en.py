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

