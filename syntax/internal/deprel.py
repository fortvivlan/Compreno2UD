import pickle

class DeprelConverter:
    def __init__(self, lang):
        self.lang = lang
        self.exceptions = {'Adjunct_Reason_Clause', 'Adjunct_Time_FiniteForm', 'ComparClause_As', 'Comparative_Чем_Clause', 'Clause_Infinitive_Чтобы_NoControl', 'AdditionalComplement', 'ЧтоFinite', 'ComparClauseDegree'}
        #####################
        ## Language specific
        if lang == 'Ru':
            ru = pickle.load(open('syntax/internal/ru.slots', 'rb'))
            self.__dict__.update(ru)
            self.detlist = {'весь', 'этот', 'такой', 'сей', 'любой', 'свой', 'никакой', 'некоторый', 'каждый', 'какой-то'}
            self.discourse = {'увы', 'ох', 'тем не менее', 'в частности', 'вот', 'ну'} # надо все же тупо захардкодить всякие ох эй
            # self.advmod = {'именно', 'лишь', 'более', 'наиболее', 'менее', 'наименее', 'всего лишь', 'в общей сложности'}
            self.composite = {'Composite_cki', 'Composite_cko', 'Composite_ComplexNumeral', 'Composite_e', 'Composite_iko', 'Composite_null', 
                            'Composite_Numeral', 'Composite_NumeralFull', 'Composite_NumeralShort', 'Composite_o', 'Composite_ski', 'Composite_sko', 'Composite_usek'}

        if lang == 'En':
            en = pickle.load(open('syntax/internal/en.slots', 'rb'))
            self.__dict__.update(en)

    def headswap(self, sent, token, depcase):
        # swaps heads for token and its first dependent (probably the only one)
        deps = [t for t in sent['tokens'] if t['head'] == token['id']]
        newhead = deps[0]['id']
        for dep in deps:
            dep['head'] = token['head']
            dep['deprel'] = 'obl'
            dep['deps'] = f"{dep['head']}:obl:{depcase}"
        token['head'] = newhead

    def en_flatnameswap(self, sent, token, head):
        # print('Swap pair token head:', token['form'], token['head'], head['form'], head['head'])
        # flat:name swaps
        if token['SurfSlot'] == 'Modifier_Composite_Hyphen':
            return
        headofhead = [t for t in sent['tokens'] if t['id'] == head['head']]
        if headofhead and headofhead[0]['grammemes'] != '_' and headofhead[0]['grammemes'].get('Classifying_Proper') and head['deprel'] != 'conj':
            allhead = headofhead[0]
            deps = [t for t in sent['tokens'] if t['head'] == allhead['id'] or t['head'] == head['id']]
        else:
            allhead = token
            deps = [t for t in sent['tokens'] if t['head'] == head['id']]
            deps.append(head)
            allhead['head'] = head['head']
            allhead['deprel'] = head['deprel']
        propdeps = []
        i = [idx for idx, t in enumerate(sent['tokens']) if t is allhead][0]
        while True:
            if not (sent['tokens'][i]['SurfSlot'] == 'ProperNamePrefix' or sent['tokens'][i]['grammemes'] != '_' and sent['tokens'][i]['grammemes'].get('Classifying_Proper')):
                break
            propdeps.append(sent['tokens'][i])
            i += 1
        # print([t['form'] for t in propdeps])
        for d in deps:
            if d is not allhead:
                d['head'] = allhead['id']
        idxs = [idx for idx, t in enumerate(sent['tokens']) if t in propdeps]
        start = min(idxs)
        end = max(idxs) + 1
        for i, t in enumerate(sent['tokens'][start + 1:end]):
            t['head'] = allhead['id'] + i
            t['deprel'] = 'flat:name'
            t['propername'] = True
        if allhead is token:
            token['SurfSlot'] = head['SurfSlot']
            head['deprel'] = 'flatname'
            token['van'] = head
        if head['deprel'] is not None and head['id'] < token['id']:
            # print('conj')
            token['deprel'] = 'conj'
            head['deprel'] = 'flat:name'
            head['head'] = token['id']
        return allhead or head

    def ru_flatnameswap(self, sent, token, head):
        # print('Swap pair token head:', token['form'], token['head'], head['form'], head['head'])
        # flat:name swaps
        if token['SurfSlot'] == 'Modifier_Composite_Hyphen':
            return
        headofhead = [t for t in sent['tokens'] if t['id'] == head['head']]
        if headofhead and headofhead[0]['grammemes'] != '_' and headofhead[0]['grammemes'].get('Classifying_Proper'):
            allhead = headofhead[0]
            deps = [t for t in sent['tokens'] if t['head'] == allhead['id'] or t['head'] == head['id']]
        else:
            allhead = token
            deps = [t for t in sent['tokens'] if t['head'] == head['id']]
            deps.append(head)
            allhead['head'] = head['head']
            allhead['deprel'] = head['deprel']
        propdeps = []
        if allhead['id'] > token['id']:
            allhead = token
        i = [idx for idx, t in enumerate(sent['tokens']) if t is allhead][0]
        while True:
            if not (sent['tokens'][i]['SurfSlot'] == 'ProperNamePrefix' or 
                    sent['tokens'][i]['grammemes'] != '_' and 
                    sent['tokens'][i]['grammemes'].get('Classifying_Proper') or 
                    sent['tokens'][i]['form'] == '-'):
                break
            if sent['tokens'][i]['form'] != '-':
                propdeps.append(sent['tokens'][i])
            i += 1
        for d in deps:
            if d is not allhead:
                d['head'] = allhead['id']
        if propdeps:
            if propdeps[-1]['form'] == '-':
                del propdeps[-1]
            start = allhead['id']
            end = max([idx for idx, t in enumerate(sent['tokens']) if t in propdeps]) + 1
            heads = [t for t in propdeps if t['head'] < start or t['head'] > end]
            if heads:
                candidate = [t for t in sent['tokens'] if t['id'] == heads[0]['head']]
                if candidate:
                    allhead = candidate[0]
            # КОСТЫЛЬ time
            c = 0
            hyph = -1
            for i, t in enumerate(sent['tokens'][start + 1:end]):
                if t['form'] == '-':
                    hyph += 1
                    continue
                t['head'] = allhead['id'] + c + hyph
                if i == 0:
                    t['head'] += 1
                t['deprel'] = 'flat:name'
                t['propername'] = True
                c += 1

        if allhead is token:
            token['SurfSlot'] = head['SurfSlot']
            head['deprel'] = 'flat:name'
            token['van'] = head
        if head['deprel'] is not None and head['id'] < token['id']:
            # print('conj')
            token['deprel'] = 'conj'
            head['deprel'] = 'flat:name'
            head['head'] = token['id']
        return allhead or head
        
    def convert(self, sent):
        for token in sent['tokens']:
            # punct
            if token['grammemes'] == '_' or token['deprel'] in {'cop', 'fixed', 'conj', 'flat:name'} or token.get('propername') or token['lemma'] == 'out of':
                if token['lemma'] == 'out of' and token['deprel'] is None:
                    token['deprel'] = 'case'
                continue 
                
            #############################
            # get head of token
            head = [idx for idx, t in enumerate(sent['tokens']) if t['id'] == token['head']]
            if head:
                head = sent['tokens'][head[0]]
            else:
                head = None
            if token['SemSlot'] == 'Classifier_Name_LeftComponent':
                if self.lang == 'En':
                    h = self.en_flatnameswap(sent, token, head)
                else:
                    h = self.ru_flatnameswap(sent, token, head)
                if h is not None:
                    head = h
            # get case
            case = token['grammemes'].get('Case')
            if token.get('van'):
                case = token['van']['grammemes'].get('Case')
            if case and len(case) == 1:
                case = case[0]
            elif case and len(case) == 2 and 'Genitive' in case:
                case = 'Genitive'
            else:
                case = None
            #############################

            ############
            ### LIKE
            ############
            if token['lemma'] == 'like' and token['SemSlot'] == 'Ch_Relation_Coincidence':
                token['deprel'] = 'case'
                deps = [t for t in sent['tokens'] if t['head'] == token['id']]
                if deps:
                    deps[0]['head'] = token['head']
                    token['head'] = deps[0]['id']
                    if head['pos'] not in {'Noun', 'Pronoun'}:
                        deps[0]['deprel'] = 'obl'
                    else:
                        deps[0]['deprel'] = 'nmod'
                    if len(deps) > 1:
                        for d in deps[1:]:
                            d['head'] = deps[0]['id']
                            d['deprel'] = 'conj'
                            d['deps'] = f"{deps[0]['head']}:{deps[0]['deprel']}|{deps[0]['id']}:conj"

                    continue
            ############
            ### LET'S
            ############

            if token['SurfSlot'] in {'Let_s', 'Давай'}:
                ## HEAD SWAP ##
                token['head'] = head['head']
                head['head'] = token['id']
                head['deprel'] = 'xcomp'
                if head['head'] == 0:
                    token['deprel'] = 'root'
                else:
                    if head['SurfSlot'] == 'Verb':
                        headhead = [t for t in sent['tokens'] if t['id'] == token['head']]
                        if headhead and headhead[0]['SemClass'] == 'TO_SAY_SPEAK_TELL_TALK': # костыль для told "let's"
                            token['deprel'] = 'ccomp'
                    token['SurfSlot'] = head['SurfSlot']
                headdeps = [t for t in sent['tokens'] if t['head'] == head['id'] and t['SemClass'] != 'BE']
                if headdeps:
                    for d in headdeps:
                        if d['deprel'] == 'conj':
                            d['deps'] = f"{head['head']}:xcomp|{d['head']}:conj"
                        else:
                            d['head'] = token['id']
                if token['deprel'] == 'root':
                    continue
                head = [t for t in sent['tokens'] if t['id'] == head['head']][0]

            ############
            ### SUCH AS
            ############

            if token['lemma'] == 'such':
                nexttok = [t for t in sent['tokens'] if t['id'] == token['id'] + 1][0]
                if nexttok['form'] == 'as':   
                    token['deprel'] = 'case'
                    deps = [t for t in sent['tokens'] if t['head'] == token['id']]
                    if not deps:
                        raise Exception # маловероятно
                    deps[0]['head'] = token['head']
                    token['head'] = deps[0]['id']
                    nexttok['head'] = token['id']
                    nexttok['deprel'] = 'fixed'
                    deps[0]['deps'] = f"{deps[0]['head']}:nmod:such_as"
                    deps[0]['deprel'] = 'nmod'
                    if len(deps) > 1:
                        for d in deps[1:]:
                            d['head'] = deps[0]['id']
                            d['deprel'] = 'conj'
                            d['deps'] = f"{deps[0]['deps']}|{deps[0]['id']}:conj"
                    continue

            ## dep, моржи
            if token['SurfSlot'].startswith('Modifier_Prefixoid') or 'Composite' in token['SurfSlot'] or token['SurfSlot'] == 'Non_Prefixoid' or token['pos'] == 'Prefixoid':
                if token['pos'] in {'Noun', 'Prefixoid'}:
                    token['deprel'] = 'compound'
                else:
                    token['deprel'] = 'amod'

            ### ROOT ###
            ############
            if token['head'] == 0:
                token['deprel'] = 'root'
                continue

            # aux, aux:pass
            if token['SurfSlot'].startswith('Aux') or token['SurfSlot'] in {'DoEmphatic', 'DoIndefinite', 'ParticleБы', 'Бы_AfterConjunction'}:
                if token['SurfSlot'] == 'AuxPassive':
                    token['deprel'] = 'aux:pass'
                else:
                    token['deprel'] = 'aux'

            # discourse
            if token['lemma'] in self.discourse or token['SurfSlot'] in self.discoursePP:
                token['deprel'] = 'discourse'

            # case 
            # if token['pos'] == 'Preposition' or (token['SurfSlot'] in {'AsLike', 'Than', 'GenitiveS'} and head['pos'] in {'Noun', 'Pronoun'}): # посмотреть русское как
            if token['SurfSlot'] in self.case or token['pos'] == 'Preposition': # на всякий
                token['deprel'] = 'case'
            ## HEAD SWAP ##
            if head is None:
                print(sent['text'])
            if head['lemma'] == 'согласно':
                token['deprel'] = 'obl'
                continue
            if token['lemma'] == 'согласно':
                headofhead = None
                token['deprel'] = 'case'
                # if head['pos'] == 'Noun': # lang spec - пока костыль
                #     head['head'] = token['head']
                #     token['head'] = head['id']
                # if head['pos'] == 'Verb':
                if head['pos'] in {'Noun', 'Pronoun'}:
                    headofhead = [t['id'] for t in sent['tokens'] if t['id'] == head['head']]
                    if not headofhead:
                        raise Exception('Согласно говну')
                    headofhead = headofhead[0]
                deps = [t for t in sent['tokens'] if t['head'] == token['id'] and t['pos'] in {'Noun', 'Pronoun'}]
                if deps:
                    deps[0]['head'] = headofhead or token['head']
                    token['head'] = deps[0]['id']
                continue

            # as to why - CHECK
            if token['lemma'] == 'as to' and token['SurfSlot'] == 'Modifier_Adverbial_ForNouns':
                deps = [t for t in sent['tokens'] if t['head'] == token['id']]
                if deps:
                    deps[0]['head'] = token['head']
                    if head['pos'] in {'Noun', 'Pronoun'}:
                        deps[0]['deps'] = f"{deps[0]['head']}:acl:as_to"
                    else:
                        deps[0]['deps'] = f"{deps[0]['head']}:advcl:as_to"
                    token['head'] = deps[0]['id']
                    token['dep'] = 'mark'

            # bug fix for RelativeGroup and det = CHECK
            if token['SurfSlot'] == 'RelativeGroup' and token['pos'] == 'Noun':
                headeps = [t for t in sent['tokens'] if t['head'] == head['id'] and t['form'] == '#NULL']
                if headeps:
                    if headeps[0]['SurfSlot'] in self.obj and head['pos'] not in {'Noun', 'Pronoun'}:
                        token['deprel'] = 'obj'
                        continue
                    elif headeps[0]['SurfSlot'] in self.iobj and head['pos'] not in {'Noun', 'Pronoun'}:
                        token['deprel'] = 'iobj'
                        continue
                    elif headeps[0]['SurfSlot'] in self.oblnmod and head['pos'] not in {'Noun', 'Pronoun'}:
                        token['deprel'] = 'obl'
                        dependentadp = [t for t in sent['tokens'] if t['head'] == headeps[0]['id'] and t['pos'] == 'Preposition']
                        if dependentadp:
                            token['deps'] = f"{token['id']}:obl:{dependentadp[0]['lemma']}"
                        continue
                    else:
                        token['SurfSlot'] = headeps[0]['SurfSlot']
                else:
                    deppreps = [t for t in deps if t['pos'] == 'Preposition']
                    if deppreps:
                        token['deprel'] = 'obl'
                    token['deprel'] = 'obj'

            ########################
            ### OBJ, IOBJ, OBL, NMOD
            ########################

            if head['pos'] not in {'Noun', 'Pronoun'}:
                # obj
                if token['SurfSlot'] in self.obj and token['pos'] not in {'Verb', 'Adverb', 'Adjective', 'Predicative'}:
                    token['deprel'] = 'obj'

                # obl 
                if token['SurfSlot'] in self.oblnmod and token['pos'] not in {'Verb', 'Adverb', 'Adjective', 'Predicative'}:
                    token['deprel'] = 'obl'
                if token['SurfSlot'] == 'Idiomatic_AdjectivePostmodifierGen':
                    token['deprel'] = 'obl'

                # iobj
                if token['SurfSlot'] in self.iobj and token['pos'] not in {'Verb', 'Adverb', 'Adjective', 'Predicative'} or token['SurfSlot'] == 'Object_Indirect' and case == 'Dative':
                    token['deprel'] = 'iobj'

                if self.lang == 'En' and token['SurfSlot'] in self.npmod:
                    token['deprel'] = 'obl:npmod'

                # obl:agent
                if token['SurfSlot'] == 'Object_Instrumental' and head['grammemes'].get('Voice') and 'Passive' in head['grammemes'].get('Voice'):
                    token['deprel'] = 'obl:agent'

                # obl:tmod
                if self.lang == 'En' and token['SurfSlot'] == 'TimeNPPostCore':
                    token['deprel'] = 'obl:tmod'

            else:
                # nmod 
                if token['SurfSlot'] in self.oblnmod or token['SurfSlot'] in self.obj or token['SurfSlot'] in self.iobj:
                    token['deprel'] = 'nmod'
                if self.lang == 'En' and token['SurfSlot'] in self.poss:
                    token['deprel'] = 'nmod:poss'
                if token['SurfSlot'] in {'PostMeridiem_AnnoDomini', 'TimeNPPostCore'}:
                    token['deprel'] = 'nmod:tmod'
                if token['SurfSlot'] in self.npmod:
                    token['deprel'] = 'nmod:npmod'

                # Idiomatic_Object_Direct
                if token['SurfSlot'] == 'Idiomatic_Object_Direct':
                    token['deprel'] = 'obj'

            ############

            ############
            ### NUMMODS
            ############

            # nummod 
            if token['SurfSlot'].startswith('CardNumeral') or token['SurfSlot'] in self.nummod:
                if head['SemSlot'] == 'YEAR':
                    token['deprel'] = 'amod'
                    continue
                if head['grammemes'].get('Case') and 'Genitive' in head['grammemes'].get('Case') and case != 'Genitive':
                    token['deprel'] = 'nummod:gov'
                else:
                    token['deprel'] = 'nummod'
            if token['SurfSlot'] in {'Interval_Between', 'Interval_From', 'Interval_NeutralEC', 'Interval_StartingLimit_Hyphen', 'Quantity_Post'} and token['pos'] == 'Numeral':
                token['deprel'] = 'nummod'

            # ru spec тысяча as token
            if token['lemma'] == 'тысяча':
                dgramtypes = [t['grammemes'].get('GrammaticalType') for t in sent['tokens'] if t['head'] == token['id'] and t.get('grammemes')]
                if 'GTNumeral' in dgramtypes:
                    token['deprel'] = 'nummod:gov'
                else:
                    token['deprel'] = 'nummod'

            # nummod:entity
            if self.lang == 'Ru':
                if token['SurfSlot'] == 'Modifier_Appositive_Numeral' or token['SurfSlot'] in self.nummodent and token['pos'] == 'Numeral':
                    if head['lemma'] == 'тысяча': # ru spec
                        token['deprel'] = 'compound' # check!
                    token['deprel'] = 'nummod:entity'

            ############

            # cc 
            if token['SurfSlot'] in self.cc:
                token['deprel'] = 'cc'

            # mark
            if token['SurfSlot'] in self.mark and (head['pos'] not in {'Noun', 'Pronoun'}or head.get('copulasc')):
                token['deprel'] = 'mark'
            if token['SurfSlot'] in {'Conjunction_DependentClause', 'Conjunction_NominalDependentClause', 'Чем'}:
                token['deprel'] = 'mark'
            if token['lemma'] == 'that' and head['SurfSlot'] == 'RelativeClause_DirectFiniteThat':
                token['deprel'] = 'nsubj'

            ############
            ### DETS
            ############

            # ru, en det 
            if token['lemma'] in self.detlist or (token['SurfSlot'] in self.det and token['pos'] != 'Noun'): # lang spec - check rus for demonstrative
                if head['pos'] == 'Verb':
                    token['deprel'] = 'xcomp'
                    continue
                token['deprel'] = 'det'
            if self.lang == 'Ru' and token['SurfSlot'] in {'PossessorPremod', 'Чей'}:
                token['deprel'] = 'det'
            if self.lang == 'Ru' and token['pos'] == 'Pronoun' and token['grammemes'].get('Classifying_Possessiveness'):
                token['deprel'] = 'det'
            # en det 
            if self.lang == 'En'and token['SemSlot'] in {'Ch_Reference_IndefiniteAndQuantification'}: # any, all?
                token['deprel'] = 'det'
            # Such, det:predet
            if token['SurfSlot'] == 'Such' and sent['tokens'][token['id']]['lemma'] == 'a':
                token['deprel'] = 'det:predet'

            # amod
            if token['SurfSlot'] in self.amod and head['pos'] in {'Noun', 'Pronoun', 'Numeral'} and token['pos'] != 'Noun':
                token['deprel'] = 'amod'
            if token['SurfSlot'] == 'Idiomatic_AdjPronounPremodifierHyphen':
                token['deprel'] = 'amod'

            ############
            ## NSUBJs
            ############
            if token['SurfSlot'] in {'Subject', 'Idiomatic_Subject', 'Tag_Subject', 'Что_Parenthetical'}:
                if head['grammemes'].get('SyntVoice') and 'SyntPassive' in head['grammemes']['SyntVoice']:
                    token['deprel'] = 'nsubj:pass'
                else:
                    token['deprel'] = 'nsubj'
                if head.get('nsubjouter'):
                    headdeps = [t for t in sent['tokens'] if t['head'] == head['id'] and t['SurfSlot'] == 'Subject']
                    if len(headdeps) > 1:
                        token['deprel'] = 'nsubj:outer'
                        del head['nsubjouter']
                        continue

            # advmod 
            if token['SurfSlot'] in self.advmod: 
                token['deprel'] = 'advmod'
            if token['lemma'] == 'all' and head['SurfSlot'] == 'Complement_Nominal': # какой-то костыль для all, lang spec
                token['deprel'] = 'advmod'
            if token['SurfSlot'] == 'DegreeMultiplicative' and token['pos'] == 'Adverb':
                token['deprel'] = 'advmod'
            if token['pos'] == 'Adverb' and (head['pos'] not in {'Noun', 'Pronoun'}or head.get('copula')):
                token['deprel'] = 'advmod'
            if token['lemma'] == 'always':
                token['deprel'] = 'advmod'

            ############
            ## ACL, ADVCL, XCOMP, CCOMP
            ############

            if head['pos'] not in {'Noun', 'Pronoun'}:

                # advcl
                if token['SurfSlot'] in self.advcl and (token['pos'] not in {'Noun', 'Pronoun'} or token.get('copula')):
                    token['deprel'] = 'advcl'

                # of promoting
                if self.lang == 'En' and token['SurfSlot'] in self.oblnmod and token['pos'] in {'Verb', 'Adjective'}:
                    token['deprel'] = 'advcl'

                # xcomp
                if token['SurfSlot'] in self.xcomp:
                    token['deprel'] = 'xcomp'

                # ccomp
                if token['SurfSlot'] in self.ccomp:
                    token['deprel'] = 'ccomp'

                # xcomp, ccomp - пока оставлю, потому что не вытаскиваю Substituted
                if token['SurfSlot'] in {'Clause_Infinitive_Control', 'Clause_Infinitive_Raising'} or token['SurfSlot'] == 'Object_Direct' and token['pos'] == 'Verb':
                    token['deprel'] = 'xcomp'
                elif 'Clause' in token['SurfSlot'] and ('Object' in token['SemSlot'] or token['SemSlot'] == 'State' and not token.get('copula')) : # check
                    token['deprel'] = 'ccomp'
                if token['SurfSlot'].startswith('Complement'): # check!
                    token['deprel'] = 'xcomp'
            
            else:
        
                # acl
                if token['pos'] not in {'Noun', 'Pronoun'} or token.get('copulasc'):
                    if token['SemSlot'] == 'ParticipleRelativeClause' or token['SurfSlot'] in self.acl or token.get('copulasc') and token['copulasc'] in self.acl:
                        token['deprel'] = 'acl'
                    if token['SurfSlot'] in self.aclrel or token.get('copulasc') and token['copulasc'] in self.aclrel:
                        token['deprel'] = 'acl:relcl'
                    if token['SurfSlot'] == 'Clause_Finite' and token['SemSlot'] == 'Relation_Correlative': # ??
                        token['deprel'] = 'acl:relcl'
                    if token['SurfSlot'] in self.advcl and head.get('copula') or token['SurfSlot'] in self.exceptions: # костыль
                        token['deprel'] = 'advcl'
                    

            # acl:cleft
            if token['SurfSlot'] == 'Cleft_Group':
                token['deprel'] = 'acl:cleft'

            ############

            # vocative
            if token['SurfSlot'] in {'Voc', 'Voc_NoComma'}:
                token['deprel'] = 'vocative'

            # compound 
            if token['SurfSlot'] in self.compound:
                token['deprel'] = 'compound'
            if self.lang == 'En':
                if token['SurfSlot'] == 'Modifier_Nominal' and token['grammemes'].get('Placement') == ['LeftPlacement']:
                    token['deprel'] = 'compound'
                if token['SurfSlot'] == 'Modifier_Attributive' and head['pos'] == 'Verb':
                    token['deprel'] = 'compound'
            compositeness = token['grammemes'].get('Compositeness')
            if compositeness and len(compositeness) == 1:
                if compositeness[0] in self.composite:
                    token['deprel'] = 'compound'
            if token['pos'] == 'Numeral' and head['lemma'] == 'тысяча' and token['id'] > head['id']: # ru spec
                token['deprel'] = 'compound'
            if token['SurfSlot'] == 'PhrasalParticle':
                token['deprel'] = 'compound:prt'

            # appos 
            if token['SurfSlot'] in self.appos:
                token['deprel'] = 'appos'

            # NominalPostMod_Colon
            if token['SurfSlot'] == 'NominalPostMod_Colon' and token['pos'] in {'Noun', 'Pronoun'}:
                token['deprel'] = 'appos'

            if token['grammemes'].get('Usage'):
                usage = token['grammemes'].get('Usage')
                # nsubj for cases like which
                if 'SubjectUsage' in usage and token['pos'] in {'Noun', 'Pronoun'}:
                    if token['deprel'] != 'nsubj:pass':
                        token['deprel'] = 'nsubj'
                # csubj, csubj:pass 
                # if 'DependentUsage' in usage and token['pos'] == 'Verb' and head['grammemes'].get('ArgumentDiathesis') == ['DiaActive_EmptySubject'] and token['SurfSlot'] != 'Adjunct_Time_FiniteForm': # костыль - чекать
                if 'DependentUsage' in usage and token['SurfSlot'] in self.csubj:
                    if head['pos'] != 'Predicative' and head['grammemes'].get('SyntVoice') == ['SyntPassive']:
                            token['deprel'] = 'csubj:pass'
                    else:
                        token['deprel'] = 'csubj'
                # appos, tmod
                if 'AppositiveUsage' in usage and token['SurfSlot'] not in {'Modifier_Appositive_Numeral', 'Idiomatic_CommunicativeParticle'}:
                    token['deprel'] = 'appos'
                if token['grammemes'].get('Classifying_Temporal') == ['Year_Digital'] and head['pos'] == 'Noun':
                    if token['deprel'] is None:
                        token['deprel'] = 'nmod:tmod'
                # flat:name
                if 'AnthroponymComponentUsage' in usage:
                    token['deprel'] = 'flat:name'

            # flat
            if token['SurfSlot'] in {'Modifier_Reduplicated_Noun', 'Modifier_Reduplicated_Invar', 'Quantity_Dictate', 'Specification_NumericCharacteristicAddress'}:
                token['deprel'] = 'flat'
            if head['grammemes'].get('ClassifyingTemporal') and head['grammemes']['ClassifyingTemporal'] == 'ЧислоМесяца':
                token['deprel'] == 'flat'
            if token['grammemes'].get('Classifying_Temporal') == ['MonthName'] and head['SemClass'] == 'DAY_NUMBER': # ?
                token['deprel'] = 'flat'
            
            # flat:name 
            if token['SurfSlot'] == 'Modifier_ProperNamePostfix':
                token['deprel'] = 'flat:name'
            if token['SurfSlot'] == 'Modifier_Appositive' and token['SemSlot'] == 'Classifier_Name' and head['grammemes'].get('Classifying_FormOfAddress_or_Title') == ['FormOfAddress_or_Title']:
                token['deprel'] = 'flat:name'
            if token['SurfSlot'] in {'Modifier_Appositive_FirstLastName', 'Modifier_Appositive_InitialsOrPatronymic'}:
                token['deprel'] = 'flat:name' # не уверена, надо править
            appcore = token['grammemes'].get('Classifying_AppositiveCore')
            if (appcore and 'ProperNamePrefix' in appcore and (not token['grammemes'].get('Usage') or token['grammemes'].get('Usage') != ['AnthroponymComponentUsage'])):
                part = [t for t in sent['tokens'] if t['head'] == token['id'] and t['SurfSlot'] == 'ProperNamePrefix']
                ## HEAD SWAP ##
                if part:
                    part[0]['deprel'] = token['deprel']
                    token['deprel'] = 'flat:name'
                    part[0]['head'] = token['head']
                    token['head'] = part[0]['id']
            if token['SurfSlot'] == 'ProperNamePrefix' and head['grammemes'].get('Usage') and head['grammemes'].get('Usage') == ['AnthroponymComponentUsage']:
                token['deprel'] = 'flat:name'
                if token['head'] > 2:
                    token['head'] -= 2

            # flat:foreign
            if head['grammemes'].get('SpecialLexemes') == ['Lex_Foreign']:
                token['deprel'] == 'flat:foreign'

            # expl
            # ru
            if token['SurfSlot'] in {'Это', 'EmptySubject_Это'}:
                token['deprel'] = 'expl'
            # en
            if 'EmptySubject' in token['SemSlot']:
                token['deprel'] = 'expl'

            # parataxis
            if token['grammemes'].get('ClauseType') == ["CT_NormalNotSentenceParenthetic"]:
                if token['SemSlot'] != 'DirectSpeech':
                    token['deprel'] = 'parataxis'
            if token['deprel'] != 'cop': #copula
                if token['SurfSlot'] in self.parataxis: # or token['SemSlot'] == 'DirectSpeech' and head['id'] < token['id']
                    token['deprel'] = 'parataxis'
            else:
                if head['SurfSlot'] in self.parataxis: # or head['SemSlot'] == 'DirectSpeech'
                    token['deprel'] = 'parataxis'
            # проверка для копулы
            deps = [t for t in sent['tokens'] if t['head'] == token['id'] and t['deprel'] == 'cop']
            if deps and 'SpecificationClause' in deps[0]['SurfSlot']: 
                token['deprel'] = 'parataxis'
            
            # allegedly костыль - но оно рил может быть паратаксисом
            if token['lemma'] == 'allegedly':
                token['deprel'] = 'advmod'

            # fixed
            if token['SurfSlot'] == 'Idiomatic_Appositive':
                token['deprel'] = 'fixed'            
            # Ru fixed
            if self.lang == 'Ru' and token['SurfSlot'] in self.fixed:
                token['deprel'] = 'fixed'
                continue

            # conj
            if token['SurfSlot'] in self.conj:
                token['deprel'] = 'conj'

            # list
            if token['SurfSlot'] in {'Modifier_Nominal_Address', 'Specification_Address', 'Specification_NumericCharacteristicComma'}:
                token['deprel'] = 'list'

            # punct_word
            if token['SurfSlot'] in {'Quantity_Dictate'}:
                token['deprel'] = 'punct'

            ############
            ### ПП с учетом ГП
            ############

            # Adjunct_Purpose_FiniteForm
            if token['SurfSlot'] in {'Adjunct_Purpose_FiniteForm'}:
                if token['SemSlot'] == 'Cause_Actant':
                    token['deprel'] = 'ccomp'
                else:
                    token['deprel'] = 'advcl'

            # Clause_Infinitive_Raising => xcomp
            if token['SurfSlot'] == 'Clause_Infinitive_Raising' and token['SemSlot'] == 'Purpose_Goal':
                token['deprel'] = 'xcomp'

            # Clause_Participle_With_Movement => advcl
            if token['SurfSlot'] == 'Clause_Participle_With_Movement' and token['SemSlot'] == 'Cause':
                token['deprel'] = 'advcl'

            # Complement_Adverbial => advcl
            if token['SurfSlot'] == 'Complement_Adverbial' and token['SemSlot'] in {'Function', 'ConcurrentComplement'}:
                token['deprel'] = 'advcl'

            # Complement_Attribute_As_Participle => advcl
            if token['SurfSlot'] == 'Complement_Attribute_As_Participle' and token['SemSlot'] == 'Function':
                token['deprel'] = 'advcl'

            #########################
            ## INTERNALS EXPERIMENTAL and ONE_ANOTHER
            #########################

            # InternalInfinitive 
            if token['SurfSlot'] == 'InternalInfinitive':
                # csubj
                if head.get('Usage') and head['Usage'] == 'MainUsage':
                    token['deprel'] = 'csubj'

            # Internals
            if token['SurfSlot'] in self.internal: # очень сомнительное
                if token['SurfSlot'] == 'InternalAdjective_OrdinalNumeral' and head['pos'] in {'Noun', 'Pronoun'}:
                    token['deprel'] = 'amod'
                    continue
                if token['SurfSlot'] == 'Ellipted_Right':
                    elleft = [t for t in sent['tokens'] if t['head'] == head['id'] and t['SurfSlot'] == 'Ellipted_Left']
                    if elleft:
                        token['deprel'] = 'nmod'
                        continue
                deps = [t for t in sent['tokens'] if t['head'] == token['id']]
                deppreps = [t for t in deps if t['pos'] == 'Preposition']
                # nsubj, nsubj:pass
                if token.get('Usage') and token['Usage'] == ['SubjectUsage']:
                    if head['grammemes'].get('SyntVoice') and 'SyntPassive' in head['grammemes']['SyntVoice']:
                        token['deprel'] = 'nsubj:pass'
                    else:
                        token['deprel'] = 'nsubj'
                # appos
                if head['pos'] in {'Noun', 'Pronoun', 'Prefixoid'} and head['id'] < token['id']:
                    if token['SurfSlot'] == 'InternalNoun':
                        token['deprel'] = 'appos'
                    else:
                        token['deprel'] = 'nmod'
                elif head['pos'] in {'Noun', 'Pronoun'} and head['SemSlot'] == 'Relation_Correlative':
                    token['deprel'] = 'nsubj'
                # compound
                elif head['pos'] in {'Noun', 'Pronoun', 'Numeral'}:
                    if self.lang == 'En' and head['id'] > token['id']:
                        token['deprel'] = 'compound'
                    else:
                        token['deprel'] = 'nmod'
                # nsubj, obl, obj
                if head['pos'] in {'Verb', 'Adverb', 'Adjective', 'Predicative'}:
                    if deppreps or token['grammemes'].get('Case') and set(token['grammemes']['Case']) & {"Genitive", "Partitive", "Instrumental", "Locative", "Prepositional"}:
                        token['deprel'] = 'obl'
                    elif token['grammemes'].get('Case') == ["Nominative"]:
                        token['deprel'] = 'nsubj'
                    elif token['grammemes'].get('Case') == ["Dative"]:
                        token['deprel'] = 'iobj'
                    else:
                        token['deprel'] = 'obj' # сомнительное
                depsadvcl = [t for t in deps if t['SurfSlot'] == 'Comparative_Than_Controlled']
                if head['pos'] not in {'Noun', 'Pronoun'} and depsadvcl:
                    token['deprel'] = 'advcl'

            # Internal Finite Verb
            if token['SurfSlot'] == 'InternalFiniteVerb':
                if head['pos'] == 'Noun':
                    token['deprel'] = 'compound'
                else:
                    token['deprel'] = 'xcomp' # временная заглушка

            # InternalAdverb
            if token['SurfSlot'] == 'InternalAdverb':
                if head and head['pos'] in {'Verb', 'Adverb', 'Adjective', 'Predicative'}:
                    token['deprel'] = 'advmod'
                elif head and head['pos'] in {'Noun', 'Pronoun'}:
                    token['deprel'] = 'nmod'

            ############
            ### SWAPS
            ############

            # это могут быть структуры
            if token['SurfSlot'] == 'ЭтоMR':
                token['deprel'] = 'nsubj'
                notnsubj = [t for t in sent['tokens'] if t['head'] == head['id'] and t['grammemes'].get('Usage') == ['SubjectUsage']]
                if notnsubj:
                    notnsubj[0]['deprel'] = 'obl'
                    
            # 12 March - temporals
            if token['grammemes'].get('Classifying_Temporal') == ['CalendarDay'] and not head['grammemes'].get('Classifying_Temporal'):
                deps = [t for t in sent['tokens'] if t['head'] == token['id'] and t['grammemes'].get('Classifying_Temporal')]
                if deps:
                    deps[0]['head'] = token['head']
                    token['head'] = deps[0]['id']
                    token['deprel'] = 'nummod'

            # Neg_Alternative = HEAD SWAP
            if token['SurfSlot'] == 'Neg_Alternative':
                if 'whether or not' in sent['text'].lower():
                    ornot = 'fixed'
                else:
                    ornot = None
                whetheror = [t for t in sent['tokens'] if t['head'] == head['id'] and t['lemma'] == 'or']
                if whetheror:
                    whetheror[0]['deprel'] = ornot or 'cc'
                    if ornot:
                        whetheror[0]['head'] -= 1
                        whetheror[0]['deps'] = f"{whetheror[0]['head']}:cc"
                    else:
                        whetheror[0]['head'] = token['id']
                        whetheror[0]['deps'] = f"{token['id']}:cc"
                token['deprel'] = ornot or 'conj'
                if not ornot:
                    token['deps'] = f"{token['head']}:conj:or|{head['head']}:{head['deprel']}:whether"

            # including??
            ## HEAD SWAP ##
            if token['form'].lower() == 'including' and token['SurfSlot'] == 'ParticiplePostmodifier':
                token['deprel'] = 'case'
                self.headswap(sent, token, 'including')

            # like
            if token['form'].lower() == 'like' and token['SurfSlot'] == 'Modifier_Attributive_Post':
                token['deprel'] = 'case'
                self.headswap(sent, token, 'like')

            # DS ccomp
            #Dislocation_Left_Quotation
            headdeps = [t for t in sent['tokens'] if t['head'] == head['id'] and (t['grammemes'].get('Usage') == ['PredicativeUsage'] or t['grammemes'].get('Usage') == ['MainUsage'] or t['grammemes'].get('Usage') == ['IdiomaticUsage'])]
            if head['grammemes'].get('DirectSpeechDiathesis') and (token['deprel'] == 'cop' or not token['deprel']):
                if head['id'] < token['id']:
                    # print('ONE')
                    token['deprel'] = 'ccomp' # test
                    continue
                ### HEAD SWAP ###
                if not headdeps:
                    token['deprel'] = 'ccomp'
                    # print('TWO', sent['text'], token['form'])
                else:
                    # print('THREE')
                    # head['head'] = headdeps[0]['id']
                    # headdeps[0]['head'] = 0
                    headdeps[0]['deprel'] = 'ccomp'
                    headdeps[0]['deps'] = f"{headdeps[0]['head']}:ccomp"
                    # head['deprel'] = 'root' # test
                if len(headdeps) > 1:
                    for t in headdeps[1:]:
                        t['deps'] = f"{headdeps[0]['id']}:conj|{t['head']}:ccomp"
                        t['deprel'] = 'conj'
                        t['head'] = headdeps[0]['id']
            if token['SemSlot'] == 'DirectSpeech' and headdeps:
                ### HEAD SWAP ### 
                head['head'] = headdeps[0]['id']
                headdeps[0]['head'] = 0
                headdeps[0]['deprel'] = 'root'
                # print('FOUR', token['form'], token['id'])
                head['deprel'] = 'ccomp' # test
                if len(headdeps) > 0:
                    for h in headdeps[1:]:
                        h['head'] = headdeps[0]['id']
                        h['deprel'] = 'conj'
                        h['deps'] = f"0:root|{headdeps[0]['id']}:conj"
            if token['SemSlot'] == 'DirectSpeech':
                # print('FIVE', token['form'])
                token['deprel'] = 'ccomp'
            copula = [t for t in sent['tokens'] if t['head'] == token['id'] and t['SemClass'] in {'BE', 'NEAREST_FUTURE'}]
            if copula and copula[0]['SemSlot'] == 'DirectSpeech':
                token['deprel'] = 'ccomp' #test
                # print('SIX', token['form'], token['head'], token['deprel'])

            # просто шобы не бесило
            if token['SurfSlot'] == 'Dislocation_Right' and token['pos'] in {'Noun', 'Pronoun'} and head['pos'] not in {'Noun', 'Pronoun'}:
                token['deprel'] = 'obl'

            # Idiomatic_AdjectivePremodifier
            if token['SurfSlot'] == 'Idiomatic_AdjectivePremodifier' and head['pos'] == 'Adjective':
                token['deprel'] = 'amod'
                token['head'] = head['head']

            if token['deprel'] is None and token['grammemes'].get('GrammaticalType') == ['GTInfinitive'] and head['pos'] in {'Noun', 'Pronoun', 'Adjective'}:
                token['deprel'] = 'csubj'

            # Idiomatic_Noun_Before_Conjunction 
            if token['SurfSlot'] == 'Idiomatic_Noun_Before_Conjunction':
                head['deprel'] = 'conj'
                head['deps'] = f"{token['id']}:conj|{head['head']}:{token['deprel']}"
                token['head'] = head['head']
                head['head'] = token['id']

            # csubj
            if token['deprel'] is None and token['SurfSlot'] in self.csubj:
                token['deprel'] = 'csubj'

            # let's костыль
            if token['SurfSlot'] == 'Let_s' and token['deprel'] is None:
                token['deprel'] = 'parataxis'

            # goeswith костыль
            if token['form'] == 'ness':
                token['deprel'] = 'goeswith'

            # etc
            if token['SurfSlot'] == 'Et_Cetera' and token['lemma'] == 'etc.' and head['head'] != 0:
                token['head'] = head['head']
                token['deps'] = head['deps']
                token['deprel'] = 'conj'

            if token['deprel'] is None and head['pos'] == 'Preposition' and token['SurfSlot'] == 'Clause_Infinitive_Control':
                token['deprel'] = 'xcomp'

            # RelativeClause_Clausal - advcl:relcl?
            if token['SurfSlot'] == 'RelativeClause_Clausal' and head['pos'] not in {'Noun', 'Pronoun'}:
                token['deprel'] = 'advcl:relcl'

            # NominalPostModifier_Comma - с вершиной в глаголе ЭКСПЕРИМЕНТАЛЬНЫЙ КОСТЫЛЬ
            if token['SurfSlot'] == 'NominalPostModifier_Comma' and head['pos'] == 'Verb':
                token['deprel'] = 'parataxis'

            ############
            ### OUT OF
            ############
            if token['lemma'] == 'out of' and token['pos'] != 'Preposition':
                outdeps = [t for t in sent['tokens'] if t['head'] == token['id'] and t['SurfSlot'] == 'Object_Indirect']
                if outdeps:
                    outdeps[0]['head'] = token['head']
                    token['head'] = deps[0]['id']
                    outdeps[0]['deprel'] = token['deprel']
                    token['deprel'] = 'case'

            ### whole, entire
            if token['lemma'] in {'whole', 'entire'} and head['pos'] == 'Noun':
                token['deprel'] = 'amod'

            # крестики и нолики, босния и герцеговина. Предполагаем, что вершина всегда выше
            if token['deprel'] is None and token['SurfSlot'] == 'Idiomatic_NomAppositive_HyphenCoord':
                token['deprel'] = 'conj'
                token['deps'] = f"{head['head']}:{head['deprel']}"
            if token['SurfSlot'] == 'Idiomatic_CommunicativeParticle' and token['lemma'] == 'и':
                try:
                    idiom = [t for t in sent['tokens'] if t['SurfSlot'] == 'Idiomatic_NomAppositive_HyphenCoord' and t['head'] == head['id']][0]
                    token['head'] = idiom['id']
                except IndexError:
                    print('Idiomatic_NomAppositive_HyphenCoord without Idiomatic_NomAppositive_HyphenCoord')
                    print(sent['text'])
                    raise
            
            if token['deprel'] is None and token['SurfSlot'] == 'Complement_NominalNoControl': # костыль
                token['deprel'] = 'acl'
            
            if token['deprel'] is None and token['SurfSlot'] == 'ProperNamePrefix': # тоже костыль
                token['deprel'] = 'flat:name'
            
            if token['pos'] == 'Noun' and token['SurfSlot'] == 'Modifier_Attributive' and head['pos'] in {'Noun', 'Pronoun'}:
                token['deprel'] = 'dep' # заглушка - это надо слить со следующим токеном (win less)
            if token['SurfSlot'] in {'Кое_composite', 'Idiomatic_InvariableAppositive_HyphenToponym', 'NumberHyphen'}:
                token['deprel'] = 'dep' # тоже заглушка
            
            if token['deprel'] is None and token['SurfSlot'] == 'ParticiplePremodifier' and head['pos'] in {'Adjective', 'Verb'}:
                token['deprel'] = 'amod'
            if token['deprel'] is None and token['SurfSlot'] == 'ParticiplePostmodifier' and head['pos'] in {'Adjective', 'Verb'}:
                token['deprel'] = 'nsubj'

            if token['deprel'] == 'Topic':
                deps = [t for t in sent['tokens'] if t['head'] == token['id'] and t['SurfSlot'] == 'Что_Parenthetical']
                if deps:
                    token['deprel'] = 'advcl'
            # debug print
            # if token['deprel'] is None:
            #     print(token['form'], head['form'], head['SurfSlot'], head['SemSlot'], head['head'])