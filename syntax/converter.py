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
        self.baseud = BaseConverter(lang)
        
    def convert(self):
        """Main method"""
        with open(self.infile, 'r', encoding='utf8') as inp, open(self.output, 'w', encoding='utf8') as out:
            for line in inp:
                sent = json.loads(line)
                self.twoheads(sent)
                self.punct.punctheads(sent)
                ## TODO ##
                # copula swap?
                self.copulaswap(sent) #test
                # direct speech swap
                self.deprels.convert(sent)
                self.deps.convert(sent)
                self.baseud.convert(sent)
                print(json.dumps(sent, ensure_ascii=False), file=out)

    def twoheads(self, sent):
        """Not sure if we'll need it - for cases with more than one zero in heads, 
        usually conjunction of predicates"""
        ## TODO - check Direct Speech
        c = 0
        heads = [token for token in sent['tokens'] if token['head'] == 0]
        headsnofloat = [token for token in heads if type(token['id']) == int]
        if len(headsnofloat) > 1:
            head = headsnofloat[0]['id']
            if len(heads) > 1:
                for h in heads:
                    if not c and type(h['id'] == int):
                        c = 1
                        continue 
                    h['head'] = head
                    h['deprel'] = 'conj'
                    h['deps'] = f'{head}:conj|0:root' # посмотреть синтагрус
        elif len(headsnofloat) == 1:
            head = headsnofloat[0]['id']
            for h in heads:
                if type(h['id'] == float) and h['id'] > headsnofloat[0]['id']:
                    h['head'] = head 
                    h['deprel'] = 'conj'
                    h['deps'] = f'{head}:conj|0:root' # посмотреть синтагрус

    def copulaswap(self, sent):
        copulas = [t for t in sent['tokens'] if t['SemClass'] in {'BE', 'NEAREST_FUTURE'}]
        if not copulas:
            return 
        for cop in copulas:
            deps = [t for t in sent['tokens'] if t['head'] == cop['id']]
            if len(deps) < 1:
                raise Exception 
            cop['deprel'] = 'cop'
            depcompl = [t for t in deps if 'Complement' in t['SurfSlot']]
            if depcompl:
                head = depcompl[0]
            else:
                head = [dep for dep in deps if dep['pos'] != 'PUNCT' and dep['form'].lower() != 'это'][0] # костыль хаха
            head['head'] = cop['head'] 
            cop['head'] = head['id']
            for token in sent['tokens']:
                if token['head'] == cop['id']:
                    token['head'] = head['id']

if __name__ == '__main__':
    inputfile = 'data/smalltest.json'
    res = 'data/temp.json'
    lang = 'ru'
    syntax = Converter(lang.capitalize(), inputfile, res)
    syntax.convert()