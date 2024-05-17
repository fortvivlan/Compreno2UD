from collections import defaultdict
import re

class EnhancedConverter:
    def __init__(self, lang):
        self.lang = lang 
        self.casedict = {'Nominative': 'nom', 'Genitive': 'gen', 'Accusative': 'acc', 'Instrumental': 'ins', 'Locative': 'loc', 'Prepositional': 'loc', 'Dative': 'dat', 'Vocative': 'voc', 'Partitive': 'gen'}

    def convert(self, sent):
        self.caseconv(sent)
        self.conjconv(sent)
        # for t in sent['tokens']:
        #     print(t['id'], t['form'], t['head'], t['deprel'], t['deps'])
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
            # conj with copula
            if len(conjdict[cluster]) == 1:
                single = conjdict[cluster][0]
                potentials = [t for t in sent['tokens'] if t['SurfSlot'] == single['SurfSlot'] and t['id'] != single['id']]
                if potentials and potentials[0]['deprel'] == 'cop':
                    cophead = [t for t in sent['tokens'] if t['id'] == potentials[0]['head']][0]
                    if single['id'] > cophead['id']:
                        single['deprel'] = 'conj'
                        single['deps'] = f"{cophead['id']}:conj|{single['head']}:{cophead['deprel']}"
                        single['head'] = cophead['id']
                continue
            if not conjdict[cluster][0]['deps']:
                conjdict[cluster][0]['deps'] = f"{conjdict[cluster][0]['head']}:{conjdict[cluster][0]['deprel']}"
            # if the first conj is copula, then it's really a remnant from copulaswap and the real cluster is [1:]
            if conjdict[cluster][0]['deprel'] == 'cop':
                headid = conjdict[cluster][1]['id'] # second element is the head for conj then
                depstext = conjdict[cluster][1]['deps']
                if not depstext:
                    depstext = f"{conjdict[cluster][1]['head']}:{conjdict[cluster][1]['deprel']}"
                startidx = 2
            else:
                headid = conjdict[cluster][0]['id']
                depstext = conjdict[cluster][0]['deps'] or f"{conjdict[cluster][0]['head']}:{conjdict[cluster][0]['deprel']}"
                startidx = 1
            depreltype = conjdict[cluster][0]['deprel']
            for c in conjdict[cluster][startidx:]:
                if c['deprel'] == 'cop':
                    continue
                # if 'xsubj' in depreltype and 'nsubj' in c['deprel']:
                #     c['deprel']
                if depreltype != c['deprel']:
                    headid = c['id']
                    depstext = c['deps'] or f"{c['head']}:{c['deprel']}"
                    depreltype = c['deprel']
                    continue
                if not c['deps']:
                    c['deps'] = f"{headid}:conj|{depstext}"
                elif 'root' not in c['deps']:
                    c['deps'] = f"{headid}:conj|{depstext}"
                c['head'] = headid
                c['deprel'] = 'conj'

    def ellipsisconv(self, sent):
        elided = [t for t in sent['tokens'] if type(t['id']) == float]
        if not elided:
            return 
        for el in elided:
            if el['deprel'] == 'cop': # копула обычно зависит только от своего комплемента, а от нее ничего
                continue
            # добываем вершину эллипсиса
            head = [idx for idx, t in enumerate(sent['tokens']) if t['id'] == el['head']]
            if head:
                head = sent['tokens'][head[0]]
            else:
                head = 0 
            newhead = None
            parataxis = None
            # собираем зависимости эллипсиса
            deps = [t for t in sent['tokens'] if t['head'] == el['id']]
            deprels = {t['deprel']: t for t in deps}
            if el['deprel'] in {'xcomp', 'ccomp'}:
                for d in deps:
                    d['head'] = el['head']
                continue
            # the sooner the better
            depbetter = [t for t in deps if t['SurfSlot'] == 'ComparisonTargetInitial']
            if depbetter:
                newhead = depbetter[0]
                for dep in deps:
                    dep['deps'] = f"{el['id']}:xcomp"
                    if dep is newhead:
                        dep['deprel'] = el['deprel']
                        dep['head'] = el['head']
                    else:
                        dep['head'] = newhead['id']

            elif el['deprel'] not in {'nsubj', 'obj', 'iobj', 'obl', 'nmod', 'nummod', 'nmod:poss'} and el['pos'] not in {'Noun', 'Pronoun'}:
                if self.lang != 'Ru':
                    # If the main predicate is elided, we use simple promotion only if there is an aux or cop, or a mark in the case of an infinitival marker.
                    if 'parataxis' in deprels and deprels['parataxis']['lemma'] in {'yes', 'no'}:
                        parataxis = deprels['parataxis']
                    for d in ('aux', 'cop', 'advmod', 'mark', 'conj', 'nsubj', 'obj', 'acl', 'acl:relcl', 'obl', 'advcl'):
                        if d in deprels:
                            current = [t for t in deps if t['deprel'] == d]
                            if parataxis is not None and parataxis['id'] > current[-1]['id']:
                                newhead = parataxis
                                break
                            if d == 'advcl':
                                advcldeps = {t['deprel']: t for t in sent['tokens'] if t['head'] == deprels[d]['id']}
                                if 'mark' in advcldeps and 'conj' in advcldeps:
                                    advclconjs = [t for t in sent['tokens'] if t['deprel'] == 'conj' and t['head'] == deprels[d]['id'] and t['form'] != '#NULL']
                                    for a in advclconjs:
                                        adeps = {t['deprel']: t for t in sent['tokens'] if t['head'] == a['id']}
                                        if 'mark' not in adeps and 'cc' not in adeps:
                                            newhead = a
                                            break
                                    if newhead == a:
                                        for adv in advclconjs:
                                            if adv is a:
                                                continue
                                            adv['deprel'] = 'conj'
                                            adv['deps'] = f"{deprels[d]['id']}:conj|{a['id']}:advcl"
                                        deps.append(a)
                                        break
                            # костыль для then fine
                            if d == 'advmod' and len(current) > 1 and current[0]['lemma'] == 'then':
                                newhead = current[1]
                                break
                            newhead = current[0]
                            break 
                elif self.lang == 'Ru':
                    if el['deprel'] == 'root' and 'cop' in deprels:
                        for d in ('amod', 'nummod', 'det', 'nmod', 'case', 'nmod:poss'):
                            if d in deprels:
                                newhead = deprels[d]
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
                        dep['deps'] = f"0:root|{el['id']}:{dep['deprel']}" # root|conj
                    else:
                        if not dep.get('ellmoved'):
                            dep['deps'] = f"{el['id']}:{dep['deprel']}"
                    if newhead is None:
                        dep['deprel'] = 'orphan'
                        dep['head'] = el['head']
                    else: 
                        if dep is newhead:
                            if dep['SurfSlot'] == 'Ellipted_Left' and el['deprel'] == 'conj':
                                if head['deprel'] == 'ccomp':
                                    dep['deps'] = f"{dep['head']}:nsubj"
                                    dep['head'] = el['head']
                                    dep['deprel'] = 'conj'
                                    dep['deps'] = f"{dep['head']}:conj|" + dep['deps']
                                else:
                                    headdeps = {t['deprel']: t for t in sent['tokens'] if t['head'] == head['id'] and isinstance(t['id'], int)}
                                    for d in {'obj', 'nsubj', 'nsubj:pass'}:
                                        if d in headdeps: # очень сомнительно
                                            dep['deps'] = f"{headdeps[d]['id']}:conj|{dep['head']}:nsubj"
                                            dep['deprel'] = 'conj'
                                            dep['head'] = headdeps[d]['id']
                                            break
                            else:
                                dep['deprel'] = el['deprel']
                                dep['head'] = el['head']
                        else:
                            if not dep.get('ellmoved'):
                                dep['head'] = newhead['id']
                            
            else:
                # If the head nominal is elided, we promote dependents in the following order: amod > nummod > det > nmod > case.
                if el['deprel'] == 'conj':
                    if isinstance(el['head'], float):
                        headhead = [t for t in sent['tokens'] if t['id'] == head['id']]
                        if headhead:
                            newhead = headhead[0]
                    else:
                        newhead = head
                for d in ('amod', 'nummod', 'det', 'nmod', 'nmod:poss', 'case', 'conj'):
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
                            if el['deprel'] == 'conj' and dep['deprel'] == 'acl':
                                dep['deprel'] = 'conj' # костыль только для acl
                                dep['deps'] = f"{dep['head']}:conj|" + dep['deps']
                        if isinstance(dep['head'], int):
                            dep['ellmoved'] = True

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
            if case and len(case) == 1 and case != ['ZeroCase']:
                case = case[0]
            elif case and len(case) == 2 and ('Genitive' in case or 'Partitive' in case):
                case = 'Genitive'
            elif case and 'Partitive' in case:
                case = 'Genitive'
            else:
                case = None
            #############################
        
            if token['deprel'] in {'obl', 'nmod'}:
                if 'case' in deps:
                    if deps['case'] == 'as':
                        token['deps'] = f"{token['head']}:{token['deprel']}:{deps['case']}"
                    if deps['case'] == 'such':
                        deps['case'] = 'such_as'
                    if self.lang == 'Ru' and case:
                        token['deps'] = f"{token['head']}:{token['deprel']}:{deps['case'].replace(' ', '_')}:{self.casedict[case]}"
                    else:
                        token['deps'] = f"{token['head']}:{token['deprel']}:{deps['case'].replace(' ', '_')}"
                elif case:
                    if self.lang == 'Ru' and case:
                        token['deps'] = f"{token['head']}:{token['deprel']}:{self.casedict[case]}"
                    else:
                        token['deps'] = f"{token['head']}:{token['deprel']}"
            if token['deprel'] in {'advcl', 'acl'} and 'mark' in deps:
                token['deps'] = f"{token['head']}:{token['deprel']}:{deps['mark'].replace(' ', '_')}"

    def reftag(self, sent):
        corefs = [t for t in sent['tokens'] if t.get('IsCoref') and t['lemma'] in {'which', 'that'}]
        if not corefs:
            return 
        for c in corefs:
            try:
                corefhead = [t for t in sent['tokens'] if t['id'] == c['IsCoref']][0]
                initial = re.match(r'[\d.]+', corefhead['deps'])
                new = re.match(r'[\d.]+', c['deps'])
                if (initial or new) and initial.group() != new.group():
                    corefhead['deps'] += f"|{c['deps']}"
                    c['deps'] = f"{c['IsCoref']}:ref"
            except IndexError:
                print(sent['text'])
                print([(t['form'], t['IsCoref']) for t in sent['tokens'] if t.get('IsCoref')])
                raise

    
    def rest(self, sent):
        for token in sent['tokens']:
            if token['grammemes'] == '_':
                continue 
            # conj:and, conj:but
            if token['lemma'] in {'and', 'but', 'or'} and token['head'] != 0:
                head = [t for t in sent['tokens'] if t['id'] == token['head']][0]
                if  head['deprel'] == 'conj' and head['deps'] and f"conj:{token['lemma']}" not in head['deps']:
                    head['deps'] = head['deps'].replace('conj', f"conj:{token['lemma']}")
            if token['deps']:
                continue
            token['deps'] = f"{token['head']}:{token['deprel']}"
            if 'cop' in token['deps'] and token['deprel'] == None: # я заколебалась
                token['deprel'] = 'cop'