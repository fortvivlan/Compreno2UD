import json
from syntax.internal import *
from syntax.semantics.semantics import Semconverter


class Converter:
    """Main Syntax converter class"""
    def __init__(self, lang, infile, output):
        self.xcompslots = {'Complement_Clausal', 'Complement_Clausal_Comma', 
                           'Complement_Clausal_NoControl', 'Complement_DirectSpeech', 
                           'Complement_Infinitive', 'Complement_SpQuClause',
                           'Complement_SpQuClause', 'Complement_ThatClause'}
        self.infile = infile 
        self.output = output 
        self.punct = Punctuation()
        self.deprels = DeprelConverter(lang)
        self.deps = EnhancedConverter(lang)
        self.semconv = Semconverter()
        
    def convert(self):
        """Main method"""
        with open(self.infile, 'r', encoding='utf8') as inp, open(self.output, 'w', encoding='utf8') as out:
            for line in inp:
                sent = json.loads(line)
                self.copulaswap(sent) #test
                self.twoheads(sent)
                self.deprels.convert(sent)
                self.wayfixes(sent)
                self.moreless(sent)
                self.deps.convert(sent)
                # for t in sent['tokens']:
                #     print(t['id'], t['form'], t['head'], t['deprel'], t['deps'])
                self.punct.punctheads(sent)
                self.eudclean(sent)
                self.semconv.convert(sent)
                print(json.dumps(sent, ensure_ascii=False), file=out)

    def twoheads(self, sent):
        """Not sure if we'll need it - for cases with more than one zero in heads, 
        usually conjunction of predicates"""
        c = 0
        heads = [token for token in sent['tokens'] if token['head'] == 0]
        if len(heads) > 1:
            ihead = 0
            while True:
                head = heads[ihead]['id']
                headdeps = [t['SurfSlot'] for t in sent['tokens'] if t['head'] == head]
                if 'Conjunction_DependentClause' not in headdeps:
                    break
                ihead += 1
                if ihead >= len(heads):
                    raise Exception('Something bad with multiple heads happened')
            heads[ihead]['head'] = 0
            for h in heads:
                if h['id'] == head:
                    continue
                h['head'] = head
                h['deprel'] = 'conj'
                h['deps'] = f"0:root|{head}:conj"

    def copulaswap(self, sent):
        copulas = [t for t in sent['tokens'] if t['SemClass'] in {'BE', 'NEAREST_FUTURE'} and t['lemma'] not in {'about', 'находиться'}] # check EXTERNAL_NECESSITY
        if not copulas:
            return 
        for cop in copulas:
            deps = [t for t in sent['tokens'] if t['head'] == cop['id']]

            depbetter = [t for t in deps if t['SurfSlot'] == 'ComparisonTargetInitial'] # the better
            if depbetter:
                continue

            if len(deps) < 1:
                continue
            
            depintensity = [t for t in deps if 'DegreeIntensitySlot' in t['SurfSlot']]
            depcompl = [t for t in deps if 'Complement' in t['SurfSlot'] or t['lemma'] == 'out of']
            if depcompl:
                if depcompl[0]['SurfSlot'] == 'Complement_NominalNP' and depcompl[0]['grammemes'].get('ExtendedCase') == ['ECabout']:
                    continue
                if depcompl[0]['SemSlot'] == 'Relation_Correlative' and depcompl[0]['pos'] != 'Noun':
                    continue
                if depintensity and depintensity[0]['id'] < depcompl[0]['id']:
                    head = depintensity[0]
                    depintensity[0]['deprel'] = cop['deprel']
                    depintensity[0]['SurfSlot'] = cop['SurfSlot']
                    depintensity[0]['copula'] = True 
                    depintensity[0]['copulasc'] = cop['SemSlot']
                else:
                    head = depcompl[0]
                    depcompl[0]['deprel'] = cop['deprel']
                    depcompl[0]['SurfSlot'] = cop['SurfSlot']
                    depcompl[0]['copula'] = True 
                    depcompl[0]['copulasc'] = cop['SemSlot']
                if depcompl[0]['lemma'] == 'out of': # out of
                    depdep = [t for t in sent['tokens'] if t['head'] == depcompl[0]['id'] and t['SurfSlot'] == 'Object_Indirect']
                    if depdep:
                        head = depdep[0]
                        depcompl[0]['head'] = head['id']
                        depcompl[0]['deprel'] = 'case'
                        depdep[0]['deprel'] = cop['deprel']
                        depdep[0]['SurfSlot'] = cop['SurfSlot']
                        depdep[0]['copula'] = True
                        depdep[0]['copulasc'] = cop['SemSlot']
                # the question[nsubj:outer] is where to go[root]
                if depcompl[0]['SurfSlot'] in self.xcompslots:
                    nsubj = [t for t in sent['tokens'] if t['head'] == cop['head'] and t['SurfSlot'] == 'Subject']
                    if nsubj:
                        nsubj[0]['deprel'] = 'nsubj:outer'
                # conj with copula
                if len(depcompl) > 1:
                    for d in depcompl[1:]:
                        d['deprel'] = head['deprel']
                        d['SurfSlot'] = head['SurfSlot']
                        d['copula'] = True 
                        d['copulasc'] = cop['SemSlot']

            else:
                depinternal = [t for t in deps if t['SurfSlot'] == 'InternalNoun'] # seen as being "Old Labour"
                if depinternal:
                    depinternal[0]['head'] = cop['head']
                    cop['deprel'] = 'cop'
                    cop['head'] = depinternal[0]['id']
                    depinternal[0]['copula'] = True
                    for d in deps:
                        if d is depinternal[0]:
                            continue 
                        d['head'] = depinternal[0]['id']
                    continue
                semslots = [t for t in deps if t['SemSlot'] == 'Predicate']
                if semslots:
                    head = semslots[0]
                    head['nsubjouter'] = True
                else:
                    head = [dep for dep in deps if dep['pos'] != 'PUNCT' and dep['form'].lower() != 'это'][0] # костыль хаха
            head['head'] = cop['head'] 
            cop['head'] = head['id']
            for token in sent['tokens']:
                if token['head'] == cop['id']:
                    if token.get('copula') and token is not head:
                        token['head'] = head['head']
                    else:
                        token['head'] = head['id']
            cop['deprel'] = 'cop'
    
    def eudclean(self, sent):
        for token in sent['tokens']:
            if token['misc'] == None:
                token['misc'] = '_'
            if token['form'] == '#NULL':
                token['deprel'], token['head'] = '_', '_'

    def wayfixes(self, sent):
        """Костыльный метод ради way - nsubj и way to get is to obtain"""
        adjuncts = [t for t in sent['tokens'] if t['SurfSlot'] == 'Adjunct_Manner_Modifier']
        for token in adjuncts:
            #############################
            # get head of token
            head = [idx for idx, t in enumerate(sent['tokens']) if t['id'] == token['head']]
            if not head:
                raise Exception('No head')
            head = sent['tokens'][head[0]]

            # Adjunct_Manner_Modifier
            if token['SurfSlot'] == 'Adjunct_Manner_Modifier' and head['pos'] == 'Verb':
                headdeps = [t for t in sent['tokens'] if t['head'] == head['id'] and t['deprel'] == 'nsubj']
                if not headdeps:
                    deps = [t['pos'] for t in sent['tokens'] if t['head'] == token['id']]
                    if 'Preposition' not in deps:
                        token['deprel'] = 'nsubj'
        clausalinfnones = [t for t in sent['tokens'] if t['SurfSlot'] == 'Subject_Clausal_Infinitive' and t['deprel'] is None]
        for token in clausalinfnones:
            # print(token['form'], head['form'])
            headeps = [t for t in sent['tokens'] if t['head'] == head['id'] and t['deprel'] == 'nsubj']
            if headeps:
                token['head'] = headeps[0]['id']
                token['deprel'] = 'acl'

        for token in sent['tokens']:
            if token['deprel'] != 'xcomp':
                continue 
            # if token['grammemes'].get('GrammaticalType') != ['GTInfinitive']:
            #     continue
            head = [t for t in sent['tokens'] if t['id'] == token['head']][0]
            if head['pos'] == 'Verb' or head.get('copula'):
                if token['grammemes'].get('SubjectRealization') == ['SubjControlledPRO']:
                    nsubj = [t for t in sent['tokens'] if t['head'] == head['id'] and t['deprel'] == 'nsubj']
                    if nsubj and not nsubj[0]['deps']:
                        nsubj[0]['deps'] = f"{head['id']}:{nsubj[0]['deprel']}|{token['id']}:nsubj:xsubj"
                    elif nsubj and nsubj[0]['deps']:
                        nsubj[0]['deps'] += f"|{token['id']}:nsubj:xsubj"

    def moreless(self, sent):
        for token in sent['tokens']:
            if token['lemma'] not in {'more than', 'less than'}:
                continue 
            head = [t for t in sent['tokens'] if t['id'] == token['head']][0]
            if head['SurfSlot'] != 'AdjunctTime':
                continue
            headdeps = [t for t in sent['tokens'] if t['head'] == head['id'] and t['deprel'] == 'nummod']
            if headdeps:
                token['head'] = headdeps[0]['id']
                token['deprel'] = 'advmod'
                token['deps'] = f"{token['head']}:{token['deprel']}"
    
if __name__ == '__main__':
    inputfile = 'data/smalltest.json'
    res = 'data/temp.json'
    lang = 'ru'
    syntax = Converter(lang.capitalize(), inputfile, res)
    syntax.convert()