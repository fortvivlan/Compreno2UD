from collections import defaultdict

class EnhancedConverter:
    def __init__(self, lang):
        self.lang = lang 
        self.casedict = {'Nominative': 'nom', 'Genitive': 'gen', 'Accusative': 'acc', 'Instrumental': 'ins', 'Locative': 'loc', 'Prepositional': 'loc', 'Dative': 'dat', 'Vocative': 'voc'}

    def convert(self, sent):
        self.caseconv(sent)
        self.conjconv(sent)
        self.ellipsisconv(sent)
        self.rest(sent)
        self.reftag(sent)
            
    def conjconv(self, sent):
        conjs = [t for t in sent['tokens'] if t['grammemes'] != '_' and t['grammemes'].get('TypeOfCoordination')]
        if not conjs:
            return
        conjdict = defaultdict(list)
        for c in conjs:
            if c['deps'] and 'conj' in c['deps']:
                continue
            elif c['head'] != 0:
                conjdict[c['head']].append(c)
        for cluster in conjdict:
            if len(conjdict[cluster]) == 1:
                single = conjdict[cluster][0]
                potentials = [t for t in sent['tokens'] if t['SurfSlot'] == single['SurfSlot'] and t['id'] != single['id']]
                if potentials and potentials[0]['deprel'] == 'cop':
                    cophead = [t for t in sent['tokens'] if t['id'] == potentials[0]['head']][0]
                    single['deprel'] = 'conj'
                    single['deps'] = f"{cophead['id']}:conj|{single['head']}:{cophead['deprel']}"
                    single['head'] = cophead['id']
                continue
            conjdict[cluster][0]['deps'] = f"{conjdict[cluster][0]['head']}:{conjdict[cluster][0]['deprel']}"
            for c in conjdict[cluster][1:]:
                if not c['deps']:
                    c['deps'] = f"{conjdict[cluster][0]['id']}:conj|{c['head']}:{c['deprel']}"
                elif 'root' not in c['deps']:
                    c['deps'] = f"{conjdict[cluster][0]['id']}:conj|{c['deps']}"
                c['head'] = conjdict[cluster][0]['id']
                c['deprel'] = 'conj'

    def ellipsisconv(self, sent):
        elided = [t for t in sent['tokens'] if type(t['id']) == float]
        if not elided:
            return 
        for el in elided:
            if el['deprel'] == 'cop': # копула обычно зависит только от своего комплемента, а от нее ничего
                continue
            head = [idx for idx, t in enumerate(sent['tokens']) if t['id'] == el['head']]
            if head:
                head = sent['tokens'][head[0]]
            else:
                head = 0 
            newhead = None
            deps = [t for t in sent['tokens'] if t['head'] == el['id']]
            deprels = {t['deprel']: t for t in deps}
            if el['deprel'] not in {'nsubj', 'obj', 'iobj', 'obl', 'nmod', 'nummod'}:
                if self.lang != 'Ru':
                    for d in ('aux', 'cop', 'mark'):
                        if d in deprels:
                            newhead = deprels[d]
                            break 
                elif self.lang == 'Ru':
                    if el['deprel'] == 'root' and 'cop' in deprels:
                        for d in ('amod', 'nummod', 'det', 'nmod', 'case'):
                            if d in deprels:
                                newhead = [t for t in deps if t['deprel'] == d][0]
                                break 
                    else:
                        for d in ('aux','cop', 'mark', 'advmod', 'obl'):
                            if d in deprels:
                                # гребаный костыль потому что гребаный компрено считает в "совершенно ни при чем" вершиной "совершенно"
                                if deprels[d]['lemma'] == 'совершенно': 
                                    check = [t for t in sent['tokens'] if t['head'] == deprels[d]['id'] and t['form'].lower() == 'при чем']
                                    if check:
                                        newhead = check[0]
                                        newhead['deps'] = f"{el['head']}:{newhead['deprel']}"
                                        deprels[d]['head'] = newhead['id']
                                        deprels[d]['deps'] = f"{newhead['id']}:{deprels[d]['deprel']}"
                                        deps.remove(deprels[d])
                                        newhead['head'] = 0
                                        newhead['deprel'] = el['deprel']
                                        break
                                if not newhead:
                                    newhead = deprels[d]
                                    break 
                for dep in deps:
                    if dep['deps'] and 'conj' in dep['deps']:
                        dep['deps'] = f"0:root|{el['id']}:{dep['deprel']}" # порисерчить, как это правильно: когда conj с эллипсисом и одновременно рут
                    else:
                        dep['deps'] = f"{el['id']}:{dep['deprel']}"
                    if not newhead:
                        dep['deprel'] = 'orphan'
                        dep['head'] = el['head']
                    else: 
                        if dep is newhead:
                            dep['deprel'] = el['deprel']
                            dep['head'] = el['head']
                        else:
                            dep['head'] = newhead['id']
                            
            else:
                for d in ('amod', 'nummod', 'det', 'nmod', 'case'):
                    if d in deprels:
                        newhead = [t for t in deps if t['deprel'] == d][0]
                        break 
                if newhead:
                    for dep in deps: 
                        dep['deps'] = f"{el['id']}:{dep['deprel']}"
                        if dep is newhead:
                            dep['deprel'] = el['deprel']
                            dep['head'] = el['head']
                        else:
                            dep['head'] = newhead['id']

    def caseconv(self, sent):
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
            deps = {t['deprel']: t['lemma'] for t in sent['tokens'] if t['head'] == token['id']}
            # get case
            case = token['grammemes'].get('Case')
            if case and len(case) == 1:
                case = case[0]
            elif case and len(case) == 2 and 'Genitive' in case:
                case = 'Genitive'
            else:
                case = None
            #############################
        
            if token['deprel'] in {'obl', 'nmod'}:
                if case and 'case' in deps:
                    if deps['case'] == 'such':
                        deps['case'] = 'such_as'
                    if self.lang == 'Ru':
                        token['deps'] = f"{token['head']}:{token['deprel']}:{deps['case'].replace(' ', '_')}:{self.casedict[case]}"
                    else:
                        token['deps'] = f"{token['head']}:{token['deprel']}:{deps['case'].replace(' ', '_')}"
                elif case:
                    if self.lang == 'Ru':
                        token['deps'] = f"{token['head']}:{token['deprel']}:{self.casedict[case]}"
                    else:
                        token['deps'] = f"{token['head']}:{token['deprel']}"
            if token['deprel'] in {'advcl', 'acl'} and 'mark' in deps:
                token['deps'] = f"{token['head']}:{token['deprel']}:{deps['mark'].replace(' ', '_')}"

    def reftag(self, sent):
        corefs = [t for t in sent['tokens'] if t.get('IsCoref') and t['pos'] == 'Pronoun']
        if not corefs:
            return 
        for c in corefs:
            try:
                corefhead = [t for t in sent['tokens'] if t['id'] == c['IsCoref']][0]
                corefhead['deps'] += f"|{c['deps']}"
                c['deps'] = f"{c['IsCoref']}:ref"
            except IndexError:
                print(sent['text'])
                print([(t['form'], t['IsCoref']) for t in sent['tokens'] if t.get('IsCoref')])
                raise

    
    def rest(self, sent):
        for token in sent['tokens']:
            if token['grammemes'] == '_' or token['deps']:
                continue 
            token['deps'] = f"{token['head']}:{token['deprel']}"