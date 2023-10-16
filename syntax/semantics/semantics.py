import pandas as pd

class Semconverter:
    def __init__(self):
        data = pd.read_excel('syntax/semantics/GP.xlsx')
        self.semslots = dict(zip(data['INP'], data['OUT']))
        data = pd.read_csv('syntax/semantics/SC.csv')
        data.out = data.apply(lambda row: row['in'] if not isinstance(row['out'], str) else row['out'], axis=1)
        data.dropna(inplace=True)
        self.semclasses = dict(zip(data['in'], data['out']))
        self.fordel = {'Coordinator',
                       'Idiomatic_AdjectivePostmodifier',
                       'Idiomatic_AdjectivePremodifier',
                       'Idiomatic_AdjectivePremodifier_A',
                       'Idiomatic_AdjectivePremodifier_B',
                       'Idiomatic_Adverbial',
                       'Idiomatic_CommunicativeParticle',
                       'Idiomatic_Nominal_Appositive_Indeclin',
                       'Idiomatic_Nominal_GenitivePostmodifier',
                       'Idiomatic_Nominal_PrepositionalPostmodifier',
                       'Idiomatic_Object_Direct',
                       'Idiomatic_Object_Indirect_Prepositional',
                       'Idiomatic_Object_Indirect_Prepositional_AfterObject',
                       'Idiomatic_Object_Indirect_Prepositional_BeforeObject',
                       'Idiomatic_Object_Indirect_WithoutPreposition',
                       'Idiomatic_ParticipleModifier',
                       'Idiomatic_Precore_Invariable',
                       'Idiomatic_ReflexiveParticle_Accusative',
                       'Idiomatic_ReflexiveParticle_Dative',
                       'Idiomatic_ReflexiveParticle_EC',
                       'Idiomatic_ReflexiveParticle_Instrumental',
                       'Neg_Ellipted',
                       'Preposition',
                       'AuxPassive'}

        self.surfslots = {'Dislocation_Left',
                          'Dislocation_Left_Comma',
                          'Dislocation_Quantity',
                          'Dislocation_Right',
                          'Dislocation_Right_Comma',
                          'LexicalDislocation_Right',
                          'MovedActant',
                          'RelativeGroup',
                          'ExternalPossessor_ForVerb'}
        
    def convert(self, sent):
        for token in sent['tokens']:
            if token['SemSlot'] in self.semslots:
                token['SemSlot'] = self.semslots[token['SemSlot']]
            if token['SemClass'] in self.semclasses:
                token['SemClass'] = self.semclasses[token['SemClass']]
            if token['SemClass'] in self.fordel:
                token['SemClass'] = '_'
            if token['SurfSlot'] in self.surfslots:
                token['SemSlot'] = '$Dislocation'