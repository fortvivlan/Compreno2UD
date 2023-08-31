import re
class Feats_module_en:
    def __init__(self):
        self.neg_set = {'no', 'not', 'nothing', 'never'}# еще тут должны быть слова на 'un-', 'im-', 'dis-', но их ведь не захардкодить, а в фичах вроде нет ничего такого
        self.pers_pron_sing = {'he', 'his', 'him', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself'}
        self.pers_pron = {'I', 'me', 'my', 'he', 'him', 'his','himself','she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'we', 'us', 'ourselves', 'they', 'them', 'their', 'themselves', 'you', 'your', 'yourself'}
        self.posspron = {'Her', 'His', 'Its', 'My', 'Our', 'Their', 'her', 'his', 'its', 'my', 'our', 'their', 'your', 'whose'}
        self.abbr_set = {'Abbreviation', 'Lex_Abbreviation', 'Lex_KgSm', 'Lex_LetterAbbreviation', 'Lex_LetterDotAbbreviation'}
        self.adj_feats = ('DegreeOfComparison', 'SyntacticParadigm', 'PartletOfSpeech')
        self.adv_feats = ('DegreeOfComparison','SyntacticParadigm', 'TypeOfWH_ForLexicalClasses')
        self.noun_feats = ('Number', 'SyntacticParadigm')
        self.num_feats = ('NumType', 'PartletOfSpeech', 'SpecialNumbers')
        self.verb_feats = ('Mood', 'Number', 'Person', 'Tense', 'Type', 'FiniteClass', 'SyntVoice', 'GrammaticalType', 'PresenceOfAuxiliaryVerb')
        self.pron_feats = ('Case', 'Gender', 'Number', 'Person', 'TypeOfAnaphoricPronoun', 'TypeOfReferenceAndFinalQuantification', 'TypeOfWH_ForLexicalClasses')
        self.det_feats = {'Degree', 'Number', 'PartletOfSpeech', 'TypeOfWH_ForLexicalClasses'}
        self.ind_pron = {'Any', 'IndefSome'}

        self.pos_feats = {'ADJ': self.adj_feats,
                            'ADV': self.adv_feats,
                            'NOUN': self.noun_feats,
                            'PROPN': self.noun_feats,
                            'NUM': self.num_feats,
                            'VERB': self.verb_feats,
                            'PRON': self.pron_feats,
                            'AUX': self.verb_feats,
                            'DET': self.det_feats}

        self.pos_empty = {'ADP', 'INTJ', 'PART', 'SCONJ',
                            'CCONJ', 'PUNCT', 'SYM', 'X', 'DET'}

        self.case_set = {'Accusative': 'Acc',
                        'Genitive': 'Gen',
                        'Nominative': 'Nom'}

        self.person_set = {'PersonFirst': '1',
                            'PersonSecond': '2',
                            'PersonThird': '3'}   #PersonZero

        self.degree_set = {'DegreeSuperlative': 'Sup',
                            'DegreePositive': 'Pos',
                            'DegreeComparative': 'Cmp'}

        self.mood_set = {'Imperative': 'Imp',
                        'SubjunctivePast': 'Sub',
                        'SubjunctivePresent': 'Sub',
                        'Indicative': 'Ind'} #Indicative
        
    def filter_feats_en(self, token, lemma, pos, feats, deprel, semclass, semslot):
            '''обработка фичей'''
            '''abbr_check = 0 #проверяем аббревиатуры
            foreign_check = 0 #проверяем иностранные слова (как?)
            short_check = 0 #проверяем на короткие формы
            neg_check = 0 #проверяем на негатив...'''

            if pos in self.pos_feats:
                needed_feat = {k: v for k, v in feats.items() if k in self.pos_feats[pos]}
                if 'FiniteClass' in needed_feat:
                    needed_feat['VerbForm'] = needed_feat.pop('FiniteClass')
                #если глагол:
                if pos == 'VERB':
                    #тут можно разглядеть только три категории (все, кроме Fin)
                    #сразу отделим герундии от причастий
                    if needed_feat['GrammaticalType'][0] == 'GTParticiple':
                        #это для причастий 1 типа, по идее герундии сюда не входят (умоляю, пусть не входят..)
                        if needed_feat['Type'][0] == 'ParticipleOne' and 'PresenceOfAuxiliaryVerb' in needed_feat and needed_feat['PresenceOfAuxiliaryVerb'][0] == 'AuxPlus':
                            needed_feat['VerbForm'] = 'Part'
                            needed_feat['Tense'] == 'Pres'
                                
                        #это для причастий 2 типа
                        elif needed_feat['Type'][0] == 'ParticipleTwo':
                            needed_feat['VerbForm'] = 'Part'
                            needed_feat['Tense'] == 'Past'
                
                        #это для герундиев, которые указаны в лоб в финит класс или семслот у них подходящий (иногда они совпадают, но не всегда)
                        elif 'VerbForm' in needed_feat and needed_feat['VerbForm'][0] == 'Gerund':
                            needed_feat['VerbForm'] = 'Ger'
                        else:
                            needed_feat['VerbForm'] = 'Ger'  

                        #и сразу для причастий сюда залог впихну, он только у participles может быть (заодно и проверю, все ли причастия определились правильно (если есть залог и это не причастие, то должно быть причастие))
                        if 'SyntVoice' in needed_feat: 
                            if needed_feat['SyntVoice'][0] == 'SyntPassive':
                                needed_feat['Voice'] = needed_feat.pop('SyntVoice')
                                needed_feat['Voice'] = 'Pass'
                                if 'Number' in needed_feat:
                                    needed_feat.pop('Number') 
                            else:
                                needed_feat.pop('SyntVoice')
                    #и тут удаляем ненужное
                   
                    #part и ger закрыли(надеюсь) переходим к Fin и Inf

                    #инфинитив у обычных глаголов определяется просто - для них он указан в финит класс
                    elif 'VerbForm' in needed_feat:
                        if needed_feat['VerbForm'][0] == 'BareInfinitive' or needed_feat['VerbForm'][0] == 'Infinitive':
                            needed_feat['VerbForm'] = 'Inf'

                    else: #т.е., если финит класса нет, и это смысловой глагол, то по умолчанию стоит Fin
                        needed_feat['VerbForm'] = 'Fin'
                    #и тут удаляем ненужное
                    needed_feat.pop('GrammaticalType')
                    needed_feat.pop('Type') 
                    if 'PresenceOfAuxiliaryVerb' in needed_feat:
                        needed_feat.pop('PresenceOfAuxiliaryVerb')
                    #хочется верить, что с лексическими глаголами на этом всё
                    
                #если у нас глагол вспомогательный, фичу Verbform мы ему иначе вытаскиваем

                if pos == 'AUX': #модальные глаголы (GTVerbModal) - вспомогательные и финитные
                    #здесь финитные глаголы
                    if needed_feat['GrammaticalType'][0] == 'GTVerbModal' or needed_feat['GrammaticalType'][0] == 'GTVerb':
                        needed_feat['VerbForm'] = 'Fin'

                    #здесь инфинитивы
                    elif needed_feat['GrammaticalType'][0] == 'GTInfinitive':
                        needed_feat['VerbForm'] = 'Inf'

                    #опять с причастиями и герундиями разребем (надеюсь, что сработает как для лексических глаголов)
                    elif needed_feat['GrammaticalType'][0] == 'GTParticiple':
                        #это для причастий 1 типа, по идее герундии сюда не входят
                        if needed_feat['Type'][0] == 'ParticipleOne' and 'PresenceOfAuxiliaryVerb' in needed_feat and needed_feat['PresenceOfAuxiliaryVerb'][0] == 'AuxPlus':
                            needed_feat['VerbForm'] = 'Part'
                            needed_feat['Tense'] == 'Pres'
                        #это для причастий 2 типа
                        elif needed_feat['Type'][0] == 'ParticipleTwo':
                            needed_feat['VerbForm'] = 'Part'
                            needed_feat['Tense'] == 'Past'
                    
                        #это для герундиев, которые указаны в лоб в финит класс или семслот у них подходящий (иногда они совпадают, но не всегда)
                        elif 'VerbForm' in needed_feat and needed_feat['VerbForm'][0] == 'Gerund':
                            needed_feat['VerbForm'] = 'Ger'
                        else:
                            needed_feat['VerbForm'] = 'Ger'  
                                                     
                        if 'SyntVoice' in needed_feat: 
                            if needed_feat['SyntVoice'][0] == 'SyntPassive':
                                needed_feat['Voice'] = needed_feat.pop('SyntVoice')
                                needed_feat['Voice'] = 'Pass'
                            else:
                                needed_feat.pop('SyntVoice')          
                    #и тут удаляем ненужное
                    needed_feat.pop('GrammaticalType')
                    needed_feat.pop('Type') 
                    if 'PresenceOfAuxiliaryVerb' in needed_feat:
                        needed_feat.pop('PresenceOfAuxiliaryVerb')

                if 'Case' in needed_feat:
                    if needed_feat['Case'][0] in self.case_set and lemma in self.pers_pron: 
                        needed_feat['Case'] = self.case_set[needed_feat['Case'][0]]
                    else:
                        needed_feat.pop('Case')

                if 'Case' in needed_feat:
                    # почему-то эта строчка не работает, понять никак не могу почему, цикл выше был похожим и тоже не работал, так что я захардкодила местоимения..... upd: все поняла 
                    # if pos == 'PRON' and 'Possessiveness' in needed_feat and needed_feat['Possessiveness'][0] == 'Possessive':
                    if lemma in self.posspron: 
                        needed_feat['Case'] = 'Gen'#whose не в генетиве upd: хотя в документации к местоимениям есть вот такая строчка TODO: add Case=Gen for whose
                        needed_feat['Poss'] = 'Yes'#для притяжательных местоимений
                                        #с местоимениями жопа кстати! 
                if 'TypeOfWH_ForLexicalClasses' in needed_feat: 
                    if needed_feat['TypeOfWH_ForLexicalClasses'][0] == 'Interrog_LC':
                        needed_feat.pop('TypeOfWH_ForLexicalClasses')
                        needed_feat = 'PronType=Int'
                    else:
                        needed_feat.pop('TypeOfWH_ForLexicalClasses')
                #фича Reflex=Yes
                if pos == 'PRON':
                    if 'TypeOfAnaphoricPronoun' in needed_feat and needed_feat['TypeOfAnaphoricPronoun'][0] == 'Reflexive_Syntactic':
                        needed_feat.pop('TypeOfAnaphoricPronoun')
                        needed_feat['Reflex'] = 'Yes'
                #фича PronType будет здесь, всего значений может быть 10 для англа: prs-личные, art-артикли, int, rel, dem, emp, neg, rcp - реципроки, tot, ind-indefinite
                if pos == 'PRON':
                    if 'TypeOfAnaphoricPronoun' in needed_feat and needed_feat['TypeOfAnaphoricPronoun'][0] == 'Reciprocal':
                        needed_feat.pop('TypeOfAnaphoricPronoun')
                        needed_feat['PronType'] = 'Rcp'#each other's есть в лексемах с пробелами! а PronType=Rcp добавить для each - добавила в .csv
                    
                    if lemma.lower() in self.posspron or lemma in self.pers_pron:
                        needed_feat['PronType'] = 'Prs'
                    if lemma.lower() == 'all' or lemma.lower() == 'both':
                        needed_feat['PronType'] = 'Tot'
                        if 'Person' in needed_feat:
                            needed_feat.pop('Person')

                    if 'TypeOfReferenceAndFinalQuantification' in needed_feat and needed_feat['TypeOfReferenceAndFinalQuantification'][0] in self.ind_pron:
                        needed_feat.pop('TypeOfReferenceAndFinalQuantification')
                        needed_feat.pop('Person')
                        needed_feat['PronType'] = 'Ind'
                        if needed_feat['Number'][0] == 'Singular':
                            needed_feat['Number'] = 'Sing'
                        else:
                            needed_feat.pop('Number')
                    elif 'TypeOfReferenceAndFinalQuantification' in needed_feat and needed_feat['TypeOfReferenceAndFinalQuantification'][0] not in self.ind_pron:
                        needed_feat.pop('TypeOfReferenceAndFinalQuantification')

                    if semclass == 'DEMONSTRATIVE':
                        needed_feat['PronType'] = 'Dem'
                        needed_feat.pop('Person')

                if pos == 'DET':
                    if 'PartletOfSpeech' in needed_feat and needed_feat['PartletOfSpeech'][0] == 'ArticleIndefinite':
                        needed_feat.pop('PartletOfSpeech')
                        needed_feat['Definite'] = 'Ind'
                        needed_feat['PronType'] = 'Art'
                    elif 'PartletOfSpeech' in needed_feat and needed_feat['PartletOfSpeech'][0] == 'ArticleDefinite':
                        needed_feat.pop('PartletOfSpeech')
                        needed_feat['Definite'] = 'Def'
                        needed_feat['PronType'] = 'Art'
                    else:
                        needed_feat.pop('PartletOfSpeech')
                    if lemma.lower() == 'all' or lemma.lower() == 'both':
                        needed_feat['PronType'] = 'Tot'
                        if 'Person' in needed_feat:
                            needed_feat.pop('Person')
                    

                        # relative and interrogative prons (WDT, WP, WP$ or WRB) будут зависеть от синтаксиса (если у их вершины будет dep acl:relcl, то это rel, если нет, то int)
                                                
                if 'Gender' in needed_feat:
                    '''тут даем род, по документации только местоимениям 3-го лица, ед.ч.тут все просто Fem для she, Masc для he, Neut для it и их форм'''
                    #короче пофиг, захардкодила их, местоимения эти, а то код на пол-экрана, если их выискивать
                    if token.lower() in self.pers_pron_sing and needed_feat['Gender'][0] == 'Feminine' or 'SyntacticGender' in feats and feats['SyntacticGender'] == 'SyntFeminine':
                        needed_feat['Gender'] = 'Fem'
                    elif token.lower() in self.pers_pron_sing and needed_feat['Gender'][0] == 'Neuter' or 'SyntacticGender' in feats and feats['SyntacticGender'] == 'SyntNeuter':
                        needed_feat['Gender'] = 'Neut'
                    elif token.lower() in self.pers_pron_sing and needed_feat['Gender'][0] == 'Masculine':
                        needed_feat['Gender'] = 'Masc'
                    elif token in self.pers_pron_sing and needed_feat['Gender'][0] == 'Common':
                        needed_feat.pop('Gender')
                    else:
                        needed_feat.pop('Gender')
                
                if 'Number' in needed_feat:
                    if needed_feat['Number'][0] == 'Plural':
                        needed_feat['Number'] = 'Plur'
                    else:
                        needed_feat['Number'] = 'Sing'
                    if 'VerbForm' in needed_feat and needed_feat['VerbForm'] == 'Ger':
                        needed_feat.pop('Number')

                if 'VerbForm' in needed_feat and needed_feat['VerbForm'] == 'Inf':
                    if 'Number' in needed_feat:
                        needed_feat.pop('Number')

                if 'Person' in needed_feat:
                    if needed_feat['Person'][0] in self.person_set:
                        needed_feat['Person'] = self.person_set[needed_feat['Person'][0]]
                    else:
                        needed_feat.pop('Person')
                
                if 'DegreeOfComparison' in needed_feat:
                    needed_feat['Degree'] = needed_feat.pop('DegreeOfComparison')

                if 'Degree' in needed_feat:
                    if needed_feat['Degree'][0] in self.degree_set:
                        needed_feat['Degree'] = self.degree_set[needed_feat['Degree'][0]]
                
                '''наклонения'''
                if 'Mood' in needed_feat:
                    '''так как In English, Mood is a feature of finite verbs добавляем только финитным глаголам'''

                    if needed_feat['Mood'][0] == 'Imperative':
                        needed_feat['Mood'] = 'Imp'
                    elif needed_feat['Mood'][0] == 'SubjunctivePast' or needed_feat['Mood'][0] == 'SubjunctivePresent':
                        needed_feat['Mood'] = 'Sub'
                    else:
                        needed_feat.pop('Mood')

                if (pos == 'VERB' or pos=='AUX') and 'Mood' not in needed_feat and 'VerbForm' in needed_feat and needed_feat['VerbForm'] == 'Fin':
                    needed_feat['Mood'] = 'Ind'
                        
                if 'Tense' in needed_feat:
                    if needed_feat['Tense'][0] == 'Past':
                        needed_feat['Tense'] = 'Past'
                    elif needed_feat['Tense'][0] == 'Present':
                        needed_feat['Tense'] = 'Pres'
                    else:
                        needed_feat.pop('Tense')

                #добавляем фичи числам: Card, Ord, Mult, Frac
                if pos == 'ADV' and lemma in {'once', 'twice'}:
                    needed_feat['NumType'] = 'Mult'

                if pos == 'NUM':
                    if 'PartletOfSpeech' in needed_feat and needed_feat['PartletOfSpeech'][0] == 'NumeralCardinal':
                        needed_feat['NumType'] = 'Card'
                        needed_feat.pop('PartletOfSpeech')
                    elif semclass == 'YEAR_NUMBER':
                        needed_feat['NumType'] = 'Card'                        
                    elif 'PartletOfSpeech' in needed_feat:
                        needed_feat.pop('PartletOfSpeech')

                if pos == 'ADJ':
                    if 'PartletOfSpeech' in needed_feat and needed_feat['PartletOfSpeech'][0] == 'NumeralOrdinal':
                        needed_feat.pop('PartletOfSpeech')
                        needed_feat['NumType'] = 'Ord'
                        #сразу добавлю степень, а то ее нет в фичах изначально, и она 'Pos' у порядковых числительных
                        needed_feat['Degree'] = 'Pos'
                    else:
                        needed_feat.pop('PartletOfSpeech')

                if 'SyntacticParadigm' in needed_feat and needed_feat['SyntacticParadigm'][0] == 'SyntPseudoNumeral' and token.lower() in {'third', 'half'}:
                    needed_feat['NumType'] = 'Frac'
                    needed_feat.pop('SyntacticParadigm')
                elif 'SyntacticParadigm' in needed_feat:
                    needed_feat.pop('SyntacticParadigm')

                if pos == 'NUM':
                    if 'SpecialNumbers' in needed_feat and needed_feat['SpecialNumbers'][0] and token in re.findall(re.compile(r'\d+\.\d+'), token):
                        needed_feat['NumType'] = 'Frac'
                        needed_feat.pop('SpecialNumbers')
                    elif 'SpecialNumbers' in needed_feat and needed_feat['SpecialNumbers'][0] and token not in re.findall(re.compile(r'\d+\.\d+'), token):
                        needed_feat.pop('SpecialNumbers')
                        needed_feat['NumType'] = 'Card'
                    elif semclass == 'ACRONYM' and token in {'I', 'II'}:
                        needed_feat['NumType'] = 'Card'

                #тут даем фичу NumForm: значений судя по всему три: Word, Digit, Roman
                if pos == 'NUM':
                    if lemma == '#RomanNumber':
                        needed_feat['NumForm'] = 'Roman'
                    elif semclass == 'ACRONYM' and token in {'I', 'II'}:
                        needed_feat['NumForm'] = 'Roman'
                    elif token in re.findall(re.compile(r'[A-za-z]+'), token):
                        needed_feat['NumForm'] = 'Word'
                    elif token in re.findall(re.compile(r'\d+'), token) or token in re.findall(re.compile(r'\d+.\d+'), token):
                        needed_feat['NumForm'] = 'Digit'#вроде решили все фичи убрать числам, которые не буквами написаны

                if semclass == '#ACRONYM' and token in {'I', 'II'}:
                    needed_feat['NumForm'] = 'Roman'  
                        
                if 'SpecialLexemes' in feats and feats['SpecialLexemes'][0] in self.abbr_set and token == lemma and pos != 'NUM':
                    needed_feat['Abbr'] = 'Yes'

                if lemma in self.neg_set:#здесь еще надо поработать, мб как-то повытаскивать. захардкодить не получится
                    needed_feat['Polarity'] = 'Neg'

                if type(needed_feat) == str:
                    needed_feats = needed_feat
                else:
                    needed_feat = dict(sorted(needed_feat.items()))
                    needed_feats = [(str(m) + '=' + str(n)) for m, n in list(needed_feat.items())]
            else:
                needed_feats = '_'

            return needed_feats