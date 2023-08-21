class DeprelConverter:
    def __init__(self, lang):
        self.lang = lang
        #####################
        ## Language specific
        if lang == 'Ru':
            self.detlist = {'весь', 'этот', 'такой', 'сей', 'любой', 'свой', 'никакой', 'некоторый', 'каждый'}
            self.discourse = {'увы', 'ох', 'тем не менее', 'в частности', 'вот', 'ну'} # надо все же тупо захардкодить всякие ох эй
            self.advmods = {'именно', 'лишь', 'более', 'наиболее', 'менее', 'наименее', 'всего лишь', 'в общей сложности'}
            self.composite = {'Composite_cki', 'Composite_cko', 'Composite_ComplexNumeral', 'Composite_e', 'Composite_iko', 'Composite_null', 
                            'Composite_Numeral', 'Composite_NumeralFull', 'Composite_NumeralShort', 'Composite_o', 'Composite_ski', 'Composite_sko', 'Composite_usek'}

        if lang == 'En':
            self.detlist = {'any'} # dunno if I'll need that
            self.discourse = set()
            self.advmods = {'most'} 
            self.composite = set()

        # non lang spec
        self.amods = {'Modifier_Attributive', 'Ordinal', 'Modifier_Numeral', 'Modifier_Attributive_UnitOfMeasure', 'Quantifier', 
                      'Another_Other', 'Idiomatic_ParticiplePremodifier', 'Idiomatic_AdjectivePremodifier', 'Such'}
        self.parataxis = {'Parenthetical_EmotionsBehaviour', 'Parenthetical_Secrecy', 'Parenthetical_ConcreteAbstract', 
                          'ParentheticalAccentuation', 'Parenthetical_Standpoint', 'SourceOfInformation_Parenthetical', 
                          'ParentheticalConcession',  'NonClauseModality', 'ParentheticalSalience', 'ParentheticalOrder', 
        'Coincidence_Parenthetic', 'Parenthetic_ResultOfSummation', 'ParentheticalCondition', 'SourceOfInformation_Parenthetical', 'ParentheticalSpecification', 
        'Specification_ParentheticalAttribution', 'TextStructure', 'Parenthetical_Habitualness', 'PragmaticDefinition'} # semslots: replace with surfslots?
        self.advcl = {'Clause_Adverbial_ParticiplePhrase', 'Adjunct_Purpose_ЧтобыInfinitive', 'Adjunct_Time_FiniteForm', 
                      'Adjunct_Condition_ParticipleClause', 'Adjunct_Time_Clause', 'Adjunct_Purpose_Infinitive', 'Adjunct_Condition_Clause', 
                      'OfPostmodifier', 'Adjunct_Condition_Clause', 'Clause_Finite', 'Clause_Infinitive_NoControl', 'Adjunct_Concession_Clause'} # surfslots
        self.objtypes = {'TypeOfAddressee', 'TypeOfIndirectActant', 'TypeOfAgent', 'TypeOfExperiencer', 'TypeOfContrObject', 'TypeOfObject', 
                         'TypeOfObject_CreationDestruction', 'TypeOfPossessor', 'TypeOfRelation_Correlative', 'TypeOfRelation_Relative', 'TypeOfSource', 'TypeOfSphereSpecial'} # old
        
    def convert(self, sent):
        for token in sent['tokens']:
            # punct
            if token['grammemes'] == '_':
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

            # cop
            if token['SemClass'] == 'BE' and token['SemSlot'] == 'Predicate':
                token['deprel'] = 'cop'

            # case 
            if token['pos'] == 'Preposition' or token['SurfSlot'] in {'AsLike', 'Than', 'GenitiveS'}: # посмотреть русское как
                token['deprel'] = 'case'
            ## HEAD SWAP ##
            if token['lemma'] == 'согласно': # lang spec
                head['head'] = token['head']
                token['head'] = head['id']
                token['deprel'] = 'case'
                continue

            # obl - ? 
            if head['pos'] in {'Verb', 'Adjective', 'Adverb'} and (token['grammemes'].get('ExtendedCaseTransformation') or case in {'Genitive', 'Locative', 'Instrumental', 'Prepositional'} or head['lemma'] == 'согласно'): # lang spec
                token['deprel'] = 'obl'
            # if self.lang == 'En' and token['SurfSlot'] in self.obliques: # lang spec
            #     token['deprel'] = 'obl'
            if head['pos'] in {'Verb', 'Adjective', 'Adverb'} and token['grammemes'].get('SyntacticCase') == ['SyntIndirect']:
                token['deprel'] = 'obl'
            if token['SurfSlot'] == 'Object_Indirect_As':
                token['deprel'] = 'obl'

            # obl:agent
            if token['SurfSlot'] == 'Object_Instrumental' and head['grammemes'].get('Voice') and 'Passive' in head['grammemes'].get('Voice'):
                token['deprel'] = 'obl:agent'

            # obj
            if token['SurfSlot'] in {'Object_Direct', 'Idiomatic_Object_Direct'} and token['pos'] != 'Verb':
                token['deprel'] = 'obj'
            
            # iobj
            if token['SurfSlot'] == 'Object_Dative' or token['SurfSlot'] == 'Object_Indirect' and case == 'Dative':
                token['deprel'] = 'iobj'

            # amod
            if token['SurfSlot'] in self.amods and head['pos'] == 'Noun':
                token['deprel'] = 'amod'

            # nmod - ??
            if head['pos'] == 'Noun' and (token['pos'] in {'Noun', 'Pronoun'} or 'Time' in token['SurfSlot']):
                token['deprel'] = 'nmod'
            if token['SurfSlot'] in {'PossessorPremodGenitiveS', 'PossessorPremod'}:
                token['deprel'] = 'nmod:poss'

            # nummod 
            if token['SurfSlot'].startswith('CardNumeral'):
                if head['SemSlot'] == 'YEAR':
                    token['deprel'] = 'amod'
                    continue
                if head['grammemes'].get('Case') and 'Genitive' in head['grammemes'].get('Case') and case != 'Genitive':
                    token['deprel'] = 'nummod:gov'
                else:
                    token['deprel'] = 'nummod'
            if token['SurfSlot'] in {'QuantityForPseudoNumerals', 'Quantity_Adjective_AdjectivePronoun'}:
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
            if token['SurfSlot'] in {'Conjunction_DependentClause', 'Correlate_CondTemp'}:
                token['deprel'] = 'mark'
            if token['SurfSlot'] == 'To' and (head['SurfSlot'] in self.advcl or 'Clause' in head['SurfSlot']):  # en spec
                token['deprel'] = 'mark'

            # prefixoid, N - летний
            if token['SurfSlot'].startswith('Modifier_Prefixoid') or token['SurfSlot'] == 'Quantity_Composite':
                token['deprel'] = 'dep'

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

            # parataxis
            if token['deprel'] != 'cop': #copula
                if token['SemSlot'] in self.parataxis or token['SemSlot'] == 'DirectSpeech' and head['id'] < token['id']: 
                    token['deprel'] = 'parataxis'
            else:
                if head['SemSlot'] in self.parataxis or head['SemSlot'] == 'DirectSpeech':
                    token['deprel'] = 'parataxis'
            if token['SurfSlot'] in {'NominalPostMod_Dash', 'NominalPostModBracket', 'SpecificationClause_Brackets'}: 
                token['deprel'] = 'parataxis'

            # advmod 
            if (token['SemClass'] == 'NEGATIVE_PARTICLES' or token['pos'] == 'Adverb' or token['form'].lower() in self.advmods or token['SurfSlot'] == 'И_AdditionLimitation'): 
                token['deprel'] = 'advmod'
            if token['lemma'] == 'all' and head['SurfSlot'] == 'Complement_Nominal': # какой-то костыль для all, lang spec
                token['deprel'] = 'advmod'
            if token['SurfSlot'] == 'Modifier_HyphenoidNonCore':
                token['deprel'] = 'advmod'

            # advcl
            if token['SurfSlot'] in self.advcl and token['pos'] not in {'Noun', 'Pronoun'}: 
                token['deprel'] = 'advcl'

            # acl
            if head['pos'] in {'Noun', 'Pronoun'} and token['pos'] not in {'Noun', 'Pronoun'}:
                if token['SemSlot'] == 'ParticipleRelativeClause' or token['SurfSlot'] in self.advcl:
                    token['deprel'] = 'acl'
                if token['SurfSlot'] in {'RelativeClause', 'RelativeClause_DirectFiniteThat'}:
                    token['deprel'] = 'acl:relcl'
                if token['SurfSlot'] == 'Clause_Finite' and token['SemSlot'] == 'Relation_Correlative': # ??
                    token['deprel'] = 'acl:relcl'

            # xcomp, ccomp
            if token['SurfSlot'] in {'Clause_Infinitive_Control', 'Clause_Infinitive_Raising'} or token['SurfSlot'] == 'Object_Direct' and token['pos'] == 'Verb':
                token['deprel'] = 'xcomp'
            elif 'Clause' in token['SurfSlot'] and ('Object' in token['SemSlot'] or token['SemSlot'] == 'State'): # check
                token['deprel'] = 'ccomp'
            ## КОПУЛА - пока в XCOMP
            # dislo = token['SurfSlot'] == 'Dislocation_Right' and token['grammemes'].get('FiniteClass') == ['Infinitive']
            # if (token['SurfSlot'].startswith('Complement') or dislo or token['SurfSlot'] == 'Idiomatic_ParticipleComplement') and token['pos'] != 'Adverb': # and head['SemClass'] == 'BE' and head['SemSlot'] in {'Predicate', 'Relation_Correlative', 'Clause_Finite'}
            #     token['deprel'] = 'xcomp' 
            # Пока сущ-руты получают xcomp

            # vocative?
            if token['SurfSlot'] == 'Vocative':
                token['deprel'] = 'vocative'

            # compound 
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

            # ru spec
            if token['form'].lower() == 'это' and not token['grammemes'].get('Usage'):
                token['deprel'] = 'expl'

            # Internal Finite Verb
            if token['SurfSlot'] == 'InternalFiniteVerb':
                if head['pos'] == 'Noun':
                    token['deprel'] = 'compound'
                else:
                    token['deprel'] = 'obl' # временная заглушка

            # including??
            ## HEAD SWAP ##
            if token['form'].lower() == 'including' and token['SurfSlot'] == 'ParticiplePostmodifier':
                token['deprel'] = 'case'
                deps = [t for t in sent['tokens'] if t['head'] == token['id']]
                depheads = [t for t in deps if t['pos'] != 'PUNCT'] # если пунктуация переезжает вниз, redundant
                if not depheads:
                    continue # маловероятно 
                newhead = depheads[0]['id']
                for dep in deps:
                    dep['head'] = token['head']
                token['head'] = newhead

            # DS parataxis
            try:
                if head['grammemes'].get('DirectSpeechDiathesis') and not token['deprel']:
                    token['deprel'] = 'parataxis'
                if not token['deprel']:
                    if token['SemSlot'] == 'DirectSpeech':
                        ### HEAD SWAP ### 
                        head['head'] = token['id']
                        token['head'] = 0
                        token['deprel'] = 'root'
                        head['deprel'] = 'parataxis'
                    copula = [t for t in sent['tokens'] if t['head'] == token['id'] and t['SemClass'] in {'BE', 'NEAREST_FUTURE'}]
                    if copula and copula[0]['SemSlot'] == 'DirectSpeech':
                        token['deprel'] = 'parataxis'
            except AttributeError:
                print(sent['text'])
                raise
