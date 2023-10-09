class DeprelConverter:
    def __init__(self, lang):
        self.lang = lang
        #####################
        ## Language specific
        if lang == 'Ru':
            self.detlist = {'весь', 'этот', 'такой', 'сей', 'любой', 'свой', 'никакой', 'некоторый', 'каждый'}
            self.discourse = {'увы', 'ох', 'тем не менее', 'в частности', 'вот', 'ну'} # надо все же тупо захардкодить всякие ох эй
            # self.advmod = {'именно', 'лишь', 'более', 'наиболее', 'менее', 'наименее', 'всего лишь', 'в общей сложности'}
            self.composite = {'Composite_cki', 'Composite_cko', 'Composite_ComplexNumeral', 'Composite_e', 'Composite_iko', 'Composite_null', 
                            'Composite_Numeral', 'Composite_NumeralFull', 'Composite_NumeralShort', 'Composite_o', 'Composite_ski', 'Composite_sko', 'Composite_usek'}

        if lang == 'En':
            self.detlist = {'any'} # dunno if I'll need that
            self.discourse = {'yes', 'yeah'}
            # self.advmod = {'most'} 
            self.composite = set()

        # non lang spec
        
        self.parataxis = {'Parenthetical_EmotionsBehaviour', 'Parenthetical_Secrecy', 'Parenthetical_ConcreteAbstract', 
                          'ParentheticalAccentuation', 'Parenthetical_Standpoint', 'SourceOfInformation_Parenthetical', 
                          'ParentheticalConcession',  'NonClauseModality', 'ParentheticalSalience', 'ParentheticalOrder', 
        'Coincidence_Parenthetic', 'Parenthetic_ResultOfSummation', 'ParentheticalCondition', 'SourceOfInformation_Parenthetical', 'ParentheticalSpecification', 
        'Specification_ParentheticalAttribution', 'TextStructure', 'Parenthetical_Habitualness', 'PragmaticDefinition'} # semslots: replace with surfslots?
        with open('syntax/internal/sslots/amod.txt', encoding='utf8') as f:
            self.amod = {x.strip() for x in f.readlines()}
        with open('syntax/internal/sslots/advmod.txt', encoding='utf8') as f:
            self.advmod = {x.strip() for x in f.readlines()}
        with open('syntax/internal/sslots/advcl.txt', encoding='utf8') as f:
            self.advcl = {x.strip() for x in f.readlines()}
        with open('syntax/internal/sslots/acl.txt', encoding='utf8') as f:
            self.acl = {x.strip() for x in f.readlines()}
        with open('syntax/internal/sslots/aclrelcl.txt', encoding='utf8') as f:
            self.aclrel = {x.strip() for x in f.readlines()}
        with open('syntax/internal/sslots/oblnmod.txt', encoding='utf8') as f:
            self.oblnmod = {x.strip() for x in f.readlines()}
        with open('syntax/internal/sslots/npmod.txt', encoding='utf8') as f:
            self.npmod = {x.strip() for x in f.readlines()}
        with open('syntax/internal/sslots/appos.txt', encoding='utf8') as f:
            self.appos = {x.strip() for x in f.readlines()}
        with open('syntax/internal/sslots/compound.txt', encoding='utf8') as f:
            self.compound = {x.strip() for x in f.readlines()}
        with open('syntax/internal/sslots/xcomp.txt', encoding='utf8') as f:
            self.xcomp = {x.strip() for x in f.readlines()}
        
    def convert(self, sent):
        for token in sent['tokens']:
            # punct
            if token['grammemes'] == '_' or token['deprel'] in {'cop', 'fixed', 'conj'}:
                continue 
            #############################
            # get head of token
            head = [idx for idx, t in enumerate(sent['tokens']) if t['id'] == token['head']]
            if head:
                head = sent['tokens'][head[0]]
            else:
                head = None
            # get case
            case = token['grammemes'].get('Case')
            if case and len(case) == 1:
                case = case[0]
            elif case and len(case) == 2 and 'Genitive' in case:
                case = 'Genitive'
            else:
                case = None
            #############################

            # such as
            if token['lemma'] == 'such' and sent['tokens'][token['id']]['lemma'] == 'as':
                token['deprel'] = 'case'
                deps = [t for t in sent['tokens'] if t['head'] == token['id']]
                if not deps:
                    raise Exception # маловероятно
                deps[0]['head'] = token['head']
                token['head'] = deps[0]['id']
                sent['tokens'][token['id']]['head'] = token['id']
                sent['tokens'][token['id']]['deprel'] = 'fixed'
                deps[0]['deps'] = f"{deps[0]['head']}:nmod:such_as"
                deps[0]['deprel'] = 'nmod'
                if len(deps) > 1:
                    for d in deps[1:]:
                        d['head'] = deps[0]['id']
                        d['deprel'] = 'conj'
                        d['deps'] = f"{deps[0]['deps']}|{deps[0]['id']}:conj"
                continue

            # dep, моржи
            if token['SurfSlot'].startswith('Modifier_Prefixoid') or 'Composite' in token['SurfSlot']:
                token['deprel'] = 'dep'

            # root
            if token['head'] == 0:
                token['deprel'] = 'root'
                continue

            # aux, aux:pass
            if token['SurfSlot'].startswith('Aux') or token['SurfSlot'] in {'DoEmphatic', 'DoIndefinite'}:
                if token['SurfSlot'] == 'AuxPassive':
                    token['deprel'] = 'aux:pass'
                else:
                    token['deprel'] = 'aux'
            if token['form'].lower() == 'бы':
                token['deprel'] = 'aux'

            # discourse
            if token['lemma'] in self.discourse:
                token['deprel'] = 'discourse'

            # case 
            if token['pos'] == 'Preposition' or (token['SurfSlot'] in {'AsLike', 'Than', 'GenitiveS'} and head['pos'] in {'Noun', 'Pronoun'}): # посмотреть русское как
                token['deprel'] = 'case'
            ## HEAD SWAP ##
            if token['lemma'] == 'согласно':
                token['deprel'] = 'case'
                if head['pos'] == 'Noun': # lang spec - пока костыль
                    head['head'] = token['head']
                    token['head'] = head['id']
                elif head['pos'] == 'Verb':
                    deps = [t for t in sent['tokens'] if t['head'] == token['id'] and t['pos'] in {'Noun', 'Pronoun'}]
                    if deps:
                        deps[0]['head'] = token['head']
                        token['head'] = deps[0]['id']
                continue

            # as to why
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

            # obl - ? 
            # if head['pos'] in {'Verb', 'Adjective', 'Adverb'} and (token['grammemes'].get('ExtendedCaseTransformation') or case in {'Genitive', 'Locative', 'Instrumental', 'Prepositional'}) or head['lemma'] == 'согласно': # lang spec
            #     token['deprel'] = 'obl'
            # # if self.lang == 'En' and token['SurfSlot'] in self.obliques: # lang spec
            # #     token['deprel'] = 'obl'
            # if head['pos'] in {'Verb', 'Adjective', 'Adverb'} and token['grammemes'].get('SyntacticCase') == ['SyntIndirect']:
            #     token['deprel'] = 'obl'
            # if token['SurfSlot'] == 'Object_Indirect_As':
            #     token['deprel'] = 'obl'
            if token['SurfSlot'] in self.oblnmod and head['pos'] in {'Verb', 'Adjective', 'Adverb'} or head['lemma'] == 'согласно':
                token['deprel'] = 'obl'

            if token['SurfSlot'] in self.npmod and head['pos'] in {'Verb', 'Adjective', 'Adverb'}:
                token['deprel'] = 'obl:npmod'

            # obl:agent
            if token['SurfSlot'] == 'Object_Instrumental' and head['grammemes'].get('Voice') and 'Passive' in head['grammemes'].get('Voice'):
                token['deprel'] = 'obl:agent'

            # obj
            if token['SurfSlot'] in {'Object_Direct', 'Idiomatic_Object_Direct', 'Object_Grammatical'} and token['pos'] != 'Verb':
                token['deprel'] = 'obj'
            
            # iobj
            if token['SurfSlot'] == 'Object_Dative' or token['SurfSlot'] == 'Object_Indirect' and case == 'Dative':
                token['deprel'] = 'iobj'

            # amod
            if token['SurfSlot'] in self.amod and head['pos'] == 'Noun':
                token['deprel'] = 'amod'

            # nmod - ??
            # if head['pos'] == 'Noun' and (token['pos'] in {'Noun', 'Pronoun'} or 'Time' in token['SurfSlot']):
            #     token['deprel'] = 'nmod'
            if token['SurfSlot'] in {'PossessorPremodGenitiveS', 'PossessorPremod'}:
                token['deprel'] = 'nmod:poss'
            if token['SurfSlot'] in self.oblnmod and head['pos'] not in {'Verb', 'Adjective', 'Adverb'}:
                token['deprel'] = 'obl'

            # nummod 
            if token['SurfSlot'].startswith('CardNumeral'):
                if head['SemSlot'] == 'YEAR':
                    token['deprel'] = 'amod'
                    continue
                if head['grammemes'].get('Case') and 'Genitive' in head['grammemes'].get('Case') and case != 'Genitive':
                    token['deprel'] = 'nummod:gov'
                else:
                    token['deprel'] = 'nummod'
            if token['SurfSlot'] in {'QuantityForPseudoNumerals', 'Quantity_Adjective_AdjectivePronoun', 'Specification_NumericCharacteristicComma'}:
                token['deprel'] = 'nummod'

            # ru spec тысяча as token
            if token['lemma'] == 'тысяча':
                dgramtypes = [t['grammemes'].get('GrammaticalType') for t in sent['tokens'] if t['head'] == token['id'] and t.get('grammemes')]
                if 'GTNumeral' in dgramtypes:
                    token['deprel'] = 'nummod:gov'
                else:
                    token['deprel'] = 'nummod'

            # nummod:entity
            if token['SurfSlot'] == 'Modifier_Appositive_Numeral':
                if head['lemma'] == 'тысяча': # ru spec
                    token['deprel'] = 'compound' # check!
                token['deprel'] = 'nummod:entity'

            # cc 
            if token['SurfSlot'] in {'Coordinator', 'Coordinator_LeftBracket'}:
                token['deprel'] = 'cc'

            # mark
            if token['SurfSlot'] in {'Conjunction_DependentClause', 'Correlate_CondTemp', 'AsLike'} and head['pos'] not in {'Noun', 'Pronoun'}:
                token['deprel'] = 'mark'
            if token['SurfSlot'] == 'To' and (head['SurfSlot'] in self.advcl or 'Clause' in head['SurfSlot']):  # en spec
                token['deprel'] = 'mark'

            # ru det 
            if token['lemma'] in self.detlist or token['SurfSlot'] in {'Article', 'Demonstrative'}: # lang spec - check rus for demonstrative
                token['deprel'] = 'det'
            if self.lang == 'Ru' and token['pos'] == 'Pronoun' and token['grammemes'].get('Classifying_Possessiveness'):
                token['deprel'] = 'det'
            # en det 
            if self.lang == 'En'and token['SemSlot'] in {'Ch_Reference_IndefiniteAndQuantification'}: # any, all?
                token['deprel'] = 'det'


            # nsubj, nsubj:pass 
            if token['SurfSlot'] == 'Subject':
                if head['grammemes'].get('SyntVoice') and 'SyntPassive' in head['grammemes']['SyntVoice']:
                    token['deprel'] = 'nsubj:pass'
                else:
                    token['deprel'] = 'nsubj'

            # advmod 
            # if (token['SemClass'] == 'NEGATIVE_PARTICLES' or token['pos'] == 'Adverb' or token['SurfSlot'] in self.advmod or token['SurfSlot'] == 'И_AdditionLimitation'): 
            if token['SurfSlot'] in self.advmod:
                token['deprel'] = 'advmod'
            if token['lemma'] == 'all' and head['SurfSlot'] == 'Complement_Nominal': # какой-то костыль для all, lang spec
                token['deprel'] = 'advmod'

            # parataxis
            if token['deprel'] != 'cop': #copula
                if token['SemSlot'] in self.parataxis or token['SemSlot'] == 'DirectSpeech' and head['id'] < token['id']: 
                    token['deprel'] = 'parataxis'
            else:
                if head['SemSlot'] in self.parataxis or head['SemSlot'] == 'DirectSpeech':
                    token['deprel'] = 'parataxis'
            if token['SurfSlot'] in {'NominalPostMod_Dash', 'NominalPostModBracket', 'SpecificationClause_Brackets', 'NominalPostMod_Colon'}: 
                token['deprel'] = 'parataxis'
            # проверка для копулы
            deps = [t for t in sent['tokens'] if t['head'] == token['id'] and t['deprel'] == 'cop']
            if deps and 'SpecificationClause' in deps[0]['SurfSlot']: 
                token['deprel'] = 'parataxis'

            # advcl
            if token['SurfSlot'] in self.advcl and head['pos'] not in {'Noun', 'Pronoun'} and (token['pos'] not in {'Noun', 'Pronoun'} or token.get('copula')):
                token['deprel'] = 'advcl'

            # advcl, ccomp
            if token['SurfSlot'] in {'Adjunct_Purpose_FiniteForm'}:
                if token['SemSlot'] == 'Cause_Actant':
                    token['deprel'] = 'ccomp'
                else:
                    token['deprel'] = 'advcl'
            
            if token['SurfSlot'] == 'Clause_Participle_With_Movement':
                if token['SemSlot'] == 'Cause':
                    token['deprel'] = 'advcl'
                else:
                    token['deprel'] = 'xcomp'

            if token['SurfSlot'] == 'Clause_Infinitive_Raising':
                if token['SemSlot'] == 'Purpose_Goal':
                    token['deprel'] = 'advcl'
                else:
                    token['deprel'] = 'xcomp'

            # ccomp
            if token['SurfSlot'] == 'Clause_Finite' and head['pos'] not in {'Noun', 'Pronoun'}:
                    token['deprel'] = 'ccomp'
        
            # acl
            if head['pos'] in {'Noun', 'Pronoun'} and token['pos'] not in {'Noun', 'Pronoun'}:
                if token['SemSlot'] == 'ParticipleRelativeClause' or token['SurfSlot'] in self.acl or token.get('copulasc') and token['copulasc'] in self.acl:
                    token['deprel'] = 'acl'
                if token['SurfSlot'] in self.aclrel:
                    token['deprel'] = 'acl:relcl'
                if token['SurfSlot'] == 'Clause_Finite' and token['SemSlot'] == 'Relation_Correlative': # ??
                    token['deprel'] = 'acl:relcl'

            # acl:cleft
            if token['SurfSlot'] == 'Cleft_Group':
                token['deprel'] = 'acl:cleft'

            # xcomp
            if token['SurfSlot'] in self.xcomp:
                token['dep'] = 'xcomp'

            # xcomp, ccomp
            if token['SurfSlot'] in {'Clause_Infinitive_Control', 'Clause_Infinitive_Raising'} or token['SurfSlot'] == 'Object_Direct' and token['pos'] == 'Verb':
                token['deprel'] = 'xcomp'
            elif 'Clause' in token['SurfSlot'] and ('Object' in token['SemSlot'] or token['SemSlot'] == 'State' and not token.get('copula')) : # check
                token['deprel'] = 'ccomp'
            if token['SurfSlot'].startswith('Complement'): # check!
                token['deprel'] = 'xcomp'
            ## КОПУЛА - пока в XCOMP
            # dislo = token['SurfSlot'] == 'Dislocation_Right' and token['grammemes'].get('FiniteClass') == ['Infinitive']
            # if (token['SurfSlot'].startswith('Complement') or dislo or token['SurfSlot'] == 'Idiomatic_ParticipleComplement') and token['pos'] != 'Adverb': # and head['SemClass'] == 'BE' and head['SemSlot'] in {'Predicate', 'Relation_Correlative', 'Clause_Finite'}
            #     token['deprel'] = 'xcomp' 
            # Пока сущ-руты получают xcomp

            # vocative?
            if token['SurfSlot'] in {'Voc', 'Voc_NoComma'}:
                token['deprel'] = 'vocative'

            # compound 
            if token['SurfSlot'] in self.compound:
                token['deprel'] = 'compound'
            if self.lang == 'En':
                if token['SurfSlot'] == 'Modifier_Nominal' and token['grammemes'].get('Placement') == ['LeftPlacement']:
                    token['deprel'] = 'compound'
            compositeness = token['grammemes'].get('Compositeness')
            if compositeness and len(compositeness) == 1:
                if compositeness[0] in self.composite:
                    token['deprel'] = 'compound'
            if token['pos'] == 'Numeral' and head['lemma'] == 'тысяча' and token['id'] > head['id']: # ru spec
                token['deprel'] = 'compound'
            if token['SurfSlot'] == 'PhrasalParticle' and head['pos'] == 'Verb':
                token['deprel'] = 'compound:prt'

            # appos - в кавычках
            if token['SurfSlot'] == 'InternalNoun':
                token['deprel'] = 'appos'
            if token['SurfSlot'] in self.appos:
                token['deprel'] = 'appos'

            if token['grammemes'].get('Classifying_Temporal') == ['MonthName'] and head['SemClass'] == 'DAY_NUMBER': # ?
                token['deprel'] = 'flat'

            if token['grammemes'].get('Usage'):
                usage = token['grammemes'].get('Usage')
                # nsubj for cases like which
                if 'SubjectUsage' in usage and token['pos'] in {'Noun', 'Pronoun'}:
                    token['deprel'] = 'nsubj'
                # csubj, csubj:pass 
                if 'DependentUsage' in usage and token['pos'] == 'Verb' and head['grammemes'].get('ArgumentDiathesis') == ['DiaActive_EmptySubject'] and token['SurfSlot'] != 'Adjunct_Time_FiniteForm': # костыль - чекать
                    if head['pos'] != 'Predicative' and head['grammemes'].get('SyntVoice') == ['SyntPassive']:
                            token['deprel'] = 'csubj:pass'
                    else:
                        token['deprel'] = 'csubj'
                # appos, tmod
                if 'AppositiveUsage' in usage and token['SurfSlot'] != 'Modifier_Appositive_Numeral':
                    token['deprel'] = 'appos'
                if token['grammemes'].get('Classifying_Temporal') == ['Year_Digital'] and head['pos'] == 'Noun':
                    token['deprel'] = 'nmod:tmod'
                # flat:name
                if 'AnthroponymComponentUsage' in usage:
                    token['deprel'] = 'flat:name'

            # flat
            if head['grammemes'].get('ClassifyingTemporal') and head['grammemes']['ClassifyingTemporal'] == 'ЧислоМесяца':
                token['deprel'] == 'flat'
            
            # flat:name 
            if token['SurfSlot'] == 'Modifier_Appositive' and token['SemSlot'] == 'Classifier_Name' and head['grammemes'].get('ArticleUsage') == ['TitleAsAddressForm']:
                token['deprel'] = 'flat:name'
            appcore = token['grammemes'].get('Classifying_AppositiveCore')
            if appcore and 'ProperNamePrefix' in appcore and (not token['grammemes'].get('Usage') or token['grammemes'].get('Usage') != 'AnthroponymComponentUsage'):
                part = [t for t in sent['tokens'] if t['head'] == token['id'] and t['SurfSlot'] == 'ProperNamePrefix']
                ## HEAD SWAP ##
                if part:
                    part[0]['deprel'] = token['deprel']
                    token['deprel'] = 'flat:name'
                    part[0]['head'] = token['head']
                    token['head'] = part[0]['id']
            if token['SurfSlot'] == 'ProperNamePrefix' and head['grammemes'].get('Usage') and head['grammemes'].get('Usage') == 'AnthroponymComponentUsage':
                token['deprel'] = 'flat:name'
                token['head'] -= 2

            # flat:foreign
            if head['grammemes'].get('SpecialLexemes') == ['Lex_Foreign']:
                token['deprel'] == 'flat:foreign'

            # ru spec
            if token['form'].lower() == 'это' and not token['grammemes'].get('Usage'):
                token['deprel'] = 'expl'

            # Internal Finite Verb
            if token['SurfSlot'] == 'InternalFiniteVerb':
                if head['pos'] == 'Noun':
                    token['deprel'] = 'compound'
                else:
                    token['deprel'] = 'obl' # временная заглушка

            # expl
            # ru
            if token['form'].lower() == 'это' and not token['grammemes'].get('Usage'):
                token['deprel'] = 'expl'
            # en
            if 'EmptySubject' in token['SurfSlot']:
                token['deprel'] = 'expl'

            # including??
            ## HEAD SWAP ##
            if token['form'].lower() == 'including' and token['SurfSlot'] == 'ParticiplePostmodifier':
                token['deprel'] = 'case'
                deps = [t for t in sent['tokens'] if t['head'] == token['id']]
                newhead = deps[0]['id']
                for dep in deps:
                    dep['head'] = token['head']
                token['head'] = newhead

            # like
            if token['form'].lower() == 'like' and token['SurfSlot'] == 'Modifier_Attributive_Post':
                token['deprel'] = 'case'
                deps = [t for t in sent['tokens'] if t['head'] == token['id']]
                newhead = deps[0]['id']
                for dep in deps:
                    dep['head'] = token['head']
                token['head'] = newhead

            # DS parataxis
            headdeps = [t for t in sent['tokens'] if t['head'] == head['id'] and (t['grammemes'].get('Usage') == ['PredicativeUsage'] or t['grammemes'].get('Usage') == ['MainUsage'] or t['grammemes'].get('Usage') == ['IdiomaticUsage'])]
            if head['grammemes'].get('DirectSpeechDiathesis') and (token['deprel'] == 'cop' or not token['deprel']):
                if head['id'] < token['id']:
                    token['deprel'] = 'parataxis'
                    continue
                ### HEAD SWAP ###
                head['head'] = headdeps[0]['id']
                headdeps[0]['head'] = 0
                headdeps[0]['deprel'] = 'root'
                head['deprel'] = 'parataxis'
                if len(headdeps) > 1:
                    for t in headdeps[1:]:
                        t['deps'] = f"{headdeps[0]['id']}:conj|0:root"
                        t['deprel'] = 'conj'
                        t['head'] = headdeps[0]['id']
            if not token['deprel']:
                if token['SemSlot'] == 'DirectSpeech' and headdeps:
                    ### HEAD SWAP ### 
                    head['head'] = headdeps[0]['id']
                    headdeps[0]['head'] = 0
                    headdeps[0]['deprel'] = 'root'
                    head['deprel'] = 'parataxis'
                    if len(headdeps) > 0:
                        for h in headdeps[1:]:
                            h['head'] = headdeps[0]['id']
                            h['deprel'] = 'conj'
                            h['deps'] = f"{headdeps[0]['id']}:conj|0:root"
                copula = [t for t in sent['tokens'] if t['head'] == token['id'] and t['SemClass'] in {'BE', 'NEAREST_FUTURE'}]
                if copula and copula[0]['SemSlot'] == 'DirectSpeech':
                    token['deprel'] = 'parataxis'
