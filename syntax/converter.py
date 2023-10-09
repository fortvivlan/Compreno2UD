import json
from syntax.internal import *


class Converter:
    """Main Syntax converter class"""
    def __init__(self, lang, infile, output):
        self.infile = infile 
        self.output = output 
        self.punct = Punctuation()
        self.deprels = DeprelConverter(lang)
        self.deps = EnhancedConverter(lang)
        #self.baseud = BaseConverter(lang)
        
    def convert(self):
        """Main method"""
        with open(self.infile, 'r', encoding='utf8') as inp, open(self.output, 'w', encoding='utf8') as out:
            for line in inp:
                sent = json.loads(line)
                self.copulaswap(sent) #test
                self.twoheads(sent)
                self.deprels.convert(sent)
                # for t in sent['tokens']:
                #     print(t['id'], t['form'], t['head'], t['deprel'])
                self.deps.convert(sent)
                self.punct.punctheads(sent)
                self.eudclean(sent)
                print(json.dumps(sent, ensure_ascii=False), file=out)

    def twoheads(self, sent):
        """Not sure if we'll need it - for cases with more than one zero in heads, 
        usually conjunction of predicates"""
        c = 0
        heads = [token for token in sent['tokens'] if token['head'] == 0]
        if len(heads) > 1:
            head = heads[0]['id']
            heads[0]['head'] = 0
            for h in heads[1:]:
                h['head'] = head
                h['deprel'] = 'conj'
                h['deps'] = f"0:root|{head}:conj"

    def copulaswap(self, sent):
        copulas = [t for t in sent['tokens'] if t['SemClass'] in {'BE', 'NEAREST_FUTURE'}] # check EXTERNAL_NECESSITY
        if not copulas:
            return 
        for cop in copulas:
            deps = [t for t in sent['tokens'] if t['head'] == cop['id']]
            if len(deps) < 1:
                raise Exception 
            depcompl = [t for t in deps if 'Complement' in t['SurfSlot']]
            if depcompl:
                if depcompl[0]['SurfSlot'] == 'Complement_NominalNP' and depcompl[0]['grammemes'].get('ExtendedCase') == ['ECabout']:
                    continue
                head = depcompl[0]
                depcompl[0]['deprel'] = cop['deprel']
                depcompl[0]['SurfSlot'] = cop['SurfSlot']
                depcompl[0]['copula'] = True 
                depcompl[0]['copulasc'] = cop['SemSlot']

            else:
                head = [dep for dep in deps if dep['pos'] != 'PUNCT' and dep['form'].lower() != 'это'][0] # костыль хаха
            head['head'] = cop['head'] 
            cop['head'] = head['id']
            for token in sent['tokens']:
                if token['head'] == cop['id']:
                    token['head'] = head['id']
            cop['deprel'] = 'cop'
    
    def eudclean(self, sent):
        for token in sent['tokens']:
            if token['misc'] == None:
                token['misc'] = '_'
            if token['form'] == '#NULL':
                token['deprel'], token['head'] = '_', '_'

if __name__ == '__main__':
    inputfile = 'data/smalltest.json'
    res = 'data/temp.json'
    lang = 'ru'
    syntax = Converter(lang.capitalize(), inputfile, res)
    syntax.convert()