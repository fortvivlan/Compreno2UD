import json
from syntax.internal import *


class Converter:
    def __init__(self, infile, output):
        self.infile = infile 
        self.output = output 
        self.punct = Punctuation()
        self.deprels = DeprelConverter() 
        self.deps = EnhancedConverter() 
        self.baseud = BaseConverter() 
        
    def convert(self):
        with open(self.infile, 'r', encoding='utf8') as inp, open(self.output, 'w', encoding='utf8') as out:
            for line in inp:
                sent = json.loads(line)
                self.twoheads(sent)
                self.punct.punctheads(sent)
                self.deprels.convert(sent)
                self.deps.convert(sent)
                self.baseud.convert(sent)
                print(json.dumps(sent, ensure_ascii=False), file=out)

    def twoheads(self, sent):
        """Not sure if we'll need it - for cases with more than one zero in heads, 
        usually conjunction of predicates"""
        heads = [(idx, token['id']) for idx, token in enumerate(sent['tokens']) if token['head'] == 0]
        headsnofloat = [(idx, t) for idx, t in heads if type(t) != float]
        if len(heads) > 1:
            head = heads[0][1]
            for h in heads[1:]:
                sent['tokens'][h[0]]['head'] = head
                sent['tokens'][h[0]]['deprel'] = 'conj'

if __name__ == '__main__':
    inputfile = 'data/smalltest.json'
    res = 'data/temp.json'
    syntax = Converter(inputfile, res)
    syntax.convert()