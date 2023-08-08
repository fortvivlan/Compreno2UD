class RuDeprelConverter:
    def __init__(self):
        self.detlist = {'весь', 'этот', 'такой', 'сей', 'любой', 'свой', 'никакой', 'некоторый'}
        self.conjlist = {'и', 'но', 'а', 'или'}
        self.discourse = {'увы', 'ох', 'тем не менее', 'в частности', 'вот', 'ну'} # надо все же тупо захардкодить всякие ох эй
        self.parataxis = {'Parenthetical_EmotionsBehaviour', 'Parenthetical_Secrecy', 'Parenthetical_ConcreteAbstract', 
                          'ParentheticalAccentuation', 'Addition', 'Parenthetical_Standpoint', 'SourceOfInformation_Parenthetical', 
                          'Modality', 'ParentheticalConcession',  'NonClauseModality', 'ParentheticalSalience', 'ParentheticalOrder', 
        'Coincidence_Parenthetic', 'Parenthetic_ResultOfSummation', 'ParentheticalCondition', 'SourceOfInformation_Parenthetical', 'ParentheticalSpecification', 
        'Specification_ParentheticalAttribution', 'TextStructure', 'Parenthetical_Habitualness', 'PragmaticDefinition'}
        self.advcl = {'Cause', 'ParticipleRelativeClause', 'Comparison', 'Comparison_Symmetrical', 'ComparisonBase_AsStandard', 
                      'Concession', 'ConcessiveCondition', 'Concurrent_Situative', 'Condition', 'Consequence', 'Evidence', 'Purpose_Goal', 'Time_Situation', 'DegreeCorrelative'}
        self.composite = {'Composite_cki', 'Composite_cko', 'Composite_ComplexNumeral', 'Composite_e', 'Composite_iko', 'Composite_null', 
                          'Composite_Numeral', 'Composite_NumeralFull', 'Composite_NumeralShort', 'Composite_o', 'Composite_ski', 'Composite_sko', 'Composite_usek'}
        self.advmods = {'именно', 'лишь', 'более', 'наиболее', 'менее', 'наименее', 'всего лишь'}
        self.objtypes = {'TypeOfAddressee', 'TypeOfIndirectActant', 'TypeOfAgent', 'TypeOfExperiencer', 'TypeOfContrObject', 'TypeOfObject', 
                         'TypeOfObject_CreationDestruction', 'TypeOfPossessor', 'TypeOfRelation_Correlative', 'TypeOfRelation_Relative', 'TypeOfSource', 'TypeOfSphereSpecial'}
        
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
            #############################

            # root
            if token['head'] == 0:
                token['deprel'] = 'root'
                continue

            # aux, aux:pass
            if token['SurfSlot'].startswith('Aux'):
                if token['SurfSlot'] == 'AuxPassive':
                    token['deprel'] = 'aux:pass'
                else:
                    token['deprel'] = 'aux'
                continue

            # cop
            if token['SemClass'] == 'BE' and token['SemSlot'] == 'Predicate':
                token['deprel'] = 'cop'

            # case 
            if token['pos'] == 'Preposition':
                token['deprel'] = 'case'
                continue

            # obj
            if token['SurfSlot'] == 'Object_Direct':
                token['deprel'] = 'obj'

            # obl - ? 
            if token['SurfSlot'].startswith('Adjunct') and token['pos'] == 'Noun':
                token['deprel'] = 'obl'
            if token['SurfSlot'] in {'Object_Indirect_C_Instr', 'Object_Indirect_Через'}:
                token['deprel'] = 'obl'

            # amod
            if token['SurfSlot'] in {'Modifier_Attributive', 'Ordinal'} and head['pos'] == 'Noun':
                token['deprel'] = 'amod'

            # nmod - ??
            if head['pos'] == 'Noun' and token['pos'] == 'Noun':
                token['deprel'] = 'nmod'

            # cc 
            if token['SurfSlot'] == 'Coordinator':
                token['deprel'] = 'cc'

            # prefixoid
            if token['SurfSlot'] == 'Modifier_Prefixoid':
                token['deprel'] = 'dep'

            # advmod 
            if (token['SemClass'] == 'NEGATIVE_PARTICLES' or token['pos'] == 'Adverb' or token['lemma'] in self.advmods) and head['pos'] in {'Verb', 'Adverb'}:
                token['deprel'] = 'advmod'

            # nsubj, nsubj:pass 
            if token['SurfSlot'] == 'Subject':
                if head['grammemes'].get('SyntVoice') and 'SyntPassive' in head['grammemes']['SyntVoice']:
                    token['deprel'] = 'nsubj:pass'
                else:
                    token['deprel'] = 'nsubj'

            # parataxis
            if token['SemSlot'] in self.parataxis:
                token['deprel'] = 'parataxis'
            if token['SemSlot'] == 'DirectSpeech' and head:
                token['deprel'] = 'parataxis'

            # acl
            if token['SemSlot'] == 'ParticipleRelativeClause':
                token['deprel'] = 'acl'
            if token['SurfSlot'] == 'RelativeClause':
                token['deprel'] = 'acl:relcl'

            # advcl
            if token['SurfSlot'] == 'Clause_Adverbial_ParticiplePhrase':
                token['deprel'] = 'advcl'

            # xcomp, ccomp
            if token['SurfSlot'] == 'Clause_Infinitive_Control':
                token['deprel'] = 'xcomp'
            elif 'Clause' in token['SurfSlot'] and 'Object' in token['SemSlot']:
                token['deprel'] = 'ccomp'

            # appos - в кавычках
            if token['SurfSlot'] == 'InternalNoun':
                token['deprel'] = 'appos'

            if token['grammemes'].get('Usage'):
                usage = token['grammemes'].get('Usage')
                # appos 
                if 'AppositiveUsage' in usage:
                    token['deprel'] = 'appos'
                # flat:name
                if 'AnthroponymComponentUsage' in usage:
                    token['deprel'] = 'flat:name'
