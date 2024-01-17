import re

class QuoteException(Exception):
    def __init__(self, sent, cat):
        print(sent)
        self.message = f'Uneven {cat} count'
        super().__init__(self.message)

class Punctuation:
    """Unfinished - raw alpha version. Needs to be tested and re-written"""
    
    def punctheads(self, sent):
        """Main method"""
        try:
            self.senthead = [token['id'] for token in sent['tokens'] if token['head'] == 0][0] # если 0 вершин, вывалится
        except IndexError:
            for token in sent['tokens']:
                print(token['id'], token['form'], token['head'], sep='\t')
            raise
        self.tokens = [token for token in sent['tokens'] if token['pos'] != 'PUNCT' and '.' not in str(token['id'])]
        # set heads to quotes
        self.punctuation_quotes(sent)
        # set heads to brackets
        self.punctuation_brackets(sent)
        # set heads to commas
        self.punctuation(sent, ',')
        # set heads to the rest
        self.punctuation(sent, '.,!?:;-', comma=True)
        # merge ' s, ' ve and so on
        self.apocheck(sent)
        self.emergencyhead(sent)

    def punctuation_quotes(self, sent):
        """Quote head setting"""

        ## logs ##
        # print()
        # print(sent['text'])
        ##########
        quotes = [(idx, token) for idx, token in enumerate(sent['tokens']) if token['lemma'] == '"']
        if len(quotes) % 2: # если кавычек нечетное количество и больше одной, вывалится ошибка
            if len(quotes) == 1:
                quotes[0][1]['head'] = self.senthead
                return
            raise QuoteException(sent['text'], 'quote')
        ## logs ##
        # for idx, q in quotes:
        #     print('id:', idx, 'quote:', q['misc'])
        ##########
        pair = [] 
        count = 0
        for idx, q in enumerate(quotes):
            if q[0] == len(sent['tokens']) - 1:
                break
            if pair == [] and q[1]['misc'] == 'SpaceAfter=No' and sent['tokens'][q[0] + 1]['pos'] != 'PUNCT': 
                pair.append(q[1])
                count += 1
                for i, quote in quotes[idx + 1:]:
                    if len(pair) == 1 and i == len(sent['tokens']) - 1:
                        pair.append(quote)
                        break
                    if i == 0 or i > 0 and sent['tokens'][i - 1]['misc'] not in {'SpaceAfter=No', 'ellipsis'}:
                        ## logs ##
                        # print('current:', i)
                        # print('prev token misc:', sent['tokens'][i - 1]['misc'], 'quote misc:', quote['misc'])
                        ##########
                        count += 1
                    elif i > 0 and sent['tokens'][i - 1]['misc'] in {'SpaceAfter=No', 'ellipsis'}:
                        if count == 1:
                            pair.append(quote)
                            # print('Pair complete:', pair[0]['id'], pair[1]['id'])
                            break
                        else:
                            count -= 1
                try:
                    const = [t for t in sent['tokens'] if pair[0]['id'] < t['id'] < pair[1]['id'] and '.' not in str(t['id'])]
                except IndexError:
                    print(sent['text'])
                    print('pair', len(pair), 'count', count)
                    raise
                headconst = [t['head'] for t in const if t['head'] != None]
                if const and headconst:
                    headmin = min(headconst)
                    headmax = max(headconst)
                    if headmin == 0:
                        head = self.senthead
                    elif pair[0]['id'] < headmax < pair[1]['id']:
                        head = [t['id'] for t in const if t['head'] == headmin][0] 
                    elif headmax < pair[0]['id'] or headmax > pair[1]['id']:
                        head = [t['id'] for t in const if t['head'] == headmax][0]
                else:
                    head = -1 
                pair[0]['head'] = pair[1]['head'] = head
                pair = []
                count = 0

    def punctuation_brackets(self, sent):
        """Bracket head setting"""
        brackets = [t for t in sent['tokens'] if t['lemma'] in '()']
        ## logs ##
        # for b in brackets:
        #     print(b['id'], b['form'])
        ##########
        if len(brackets) % 2:
            raise QuoteException(sent['text'], 'bracket')
        count = 0 
        pair = [] 
        for i in range(len(brackets)):
            if pair == [] and brackets[i]['lemma'] == '(':
                count += 1
                pair.append(brackets[i])
                # print('Pair add (')
                for j in range(len(brackets[i + 1:])):
                    if brackets[j + i + 1]['lemma'] == '(':
                        count += 1 
                    elif brackets[j + i + 1]['lemma'] == ')':
                        if count == 1:
                            pair.append(brackets[j + i + 1])
                            # print('Pair add )')
                            break 
                        else:
                            count -= 1
            if len(pair) == 2:
                const = [t for t in sent['tokens'] if pair[0]['id'] < t['id'] < pair[1]['id'] and '.' not in str(t['id'])]
                headconst = [t['head'] for t in const if t['head'] != None]
                if const and headconst:
                    headmin = min(headconst)
                    headmax = max(headconst)
                    if headmin == 0:
                        head = self.senthead
                    elif pair[0]['id'] < headmax < pair[1]['id']:
                        head = [t['id'] for t in const if t['head'] == headmin][0] 
                    elif headmax < pair[0]['id'] or headmax > pair[1]['id']:
                        head = [t['id'] for t in const if t['head'] == headmax][0]
                else:
                    head = -1 
                pair[0]['head'] = pair[1]['head'] = head
                pair = []
                count = 0

    def punctuation(self, sent, punc, comma=False):
        # cases where dash - use SurfSlots
        punct = [token for token in sent['tokens'] if token['lemma'] in punc]

        ## logs ##
        # print()
        # if comma:
        #     print('AFTER COMMA')
        # else:
        #     print('COMMA')
        # print(sent['text'])
        # print('Sentence length:', len(sent['tokens']))
        # print(' '.join([t['form'] for t in self.tokens]))
        # print('Sent head:', self.senthead)
        # for p in punct:
        #     print(f"MARK: `{p['lemma']}` ID: {p['id']}")
        ##########

        prev = 0 # left border
        for i in range(len(punct)):
            # если comma, запятые мы уже проставили, но они должны учитываться
            if comma and punct[i]['lemma'] == ',':
                prev = punct[i]['id']
                continue
            if i < len(punct) - 1:
                nextpunc = punct[i + 1]['id'] # right border
            elif punct[i] == sent['tokens'][-1] or punct[i] == sent['tokens'][-2] and sent['tokens'][-1]['pos'] == 'PUNCT': # last pm = always to senthead
                    punct[i]['head'] = self.senthead
                    break
            else:
                nextpunc = sent['tokens'][-1]['id'] # если знак препинания только один? 

            ## logs ##
            # print()
            # print(f"Mark: {punct[i]['id']} `{punct[i]['lemma']}` PREV: {prev} NEXT: {nextpunc}")
            ##########

            const_left = [token for token in self.tokens if prev < token['id'] < punct[i]['id']]
            const_right = [token for token in self.tokens if punct[i]['id'] < token['id'] < nextpunc]

            ## logs ##
            # print('Left:', *[token['form'] for token in const_left])
            # print('Right:', *[token['form'] for token in const_right])
            ##########

            heads = [token['head'] for token in const_left if token['head']] # heads in left part
            # headsentInL = const_left[0]['id'] < self.senthead < const_left[-1]['id']
            if const_left and heads:
                max_left = max(heads)
                min_left = min(heads)
            else:
                min_left = 0 
                max_left = 0
            if not const_right: # нет правого контекста
                punct[i]['head'] = [token['id'] for token in self.tokens if token['head'] == min_left][0] # check!
                continue
            heads = [token['head'] for token in const_right if token['head']] # heads in right part
            if heads:
                max_right = max(heads)
                min_right = min(heads)
            else:
                max_right = 0 
                min_right = 0

            ## logs ##
            # print(f"LEFT:\nmin: {min_left} max: {max_left}\nRIGHT:\nmin: {min_right} max: {max_right}")
            ##########

            if min_left and min_right: # если они не равны нулю
                if prev < min_right < punct[i]['id']:
                    # print(f"CASE 1: dependent in right between: prev {prev} < min_right {min_right} < current {punct[i]['id']}")
                    punct[i]['head'] = [token['id'] for token in const_right if token['head'] == min_right][0]
                    # print('HEAD: ', punct[i]['head'])
                elif punct[i]['id'] < max_left < nextpunc:
                    # print(f"CASE 2: dependent in left between: current {punct[i]['id']} < max_left {max_left} < next {nextpunc}")
                    punct[i]['head'] = [token['id'] for token in const_left if token['head'] == max_left][0]
                    # print('HEAD: ', punct[i]['head'])
                elif prev > min_right: # prev в любом случае меньше current
                    # print(f"CASE 3: dependent right with head before prev: prev {prev} > min_right {min_right}, punct id {punct[i]['id']} > min_right {min_right}")
                    if max_left < prev:
                        # print('CASE 3.1: max_left < prev')
                        punct[i]['head'] = [token['id'] for token in const_left if token['head'] == max_left][0]
                        # print('HEAD: ', punct[i]['head'])
                    elif max_left > punct[i]['id']:
                        # print('CASE 3.2: max_left > current')
                        punct[i]['head'] = [token['id'] for token in const_left if token['head'] == min_left][0]
                        # print('HEAD: ', punct[i]['head'])
                    elif min_left < prev:
                        # print('CASE 3.3: left dependent with head before prev')
                        punct[i]['head'] = [token['id'] for token in const_left if token['head'] == min_left][0]
                        # print('HEAD: ', punct[i]['head'])
                elif nextpunc < max_left: # next в любом случае больше current
                    # print(f"CASE 4: dependent left with head after next: current {punct[i]['id']} < max_left {max_left}, next {nextpunc} < max_left {max_left}")
                    if min_right < punct[i]['id']:
                        # print('CASE 4.1: min right < current')
                        punct[i]['head'] = [token['id'] for token in const_right if token['head'] == min_right][0]
                        # print('HEAD: ', punct[i]['head'])
                    elif max_right > nextpunc:
                        # print('CASE 4.2: max_right > nextpunc')
                        punct[i]['head'] = [token['id'] for token in const_right if token['head'] == max_right][0]
                        # print('HEAD: ', punct[i]['head'])
                elif prev > min_left and punct[i]['id'] > max_left:
                    # print(f"CASE 5 DUBIOUS: left part contains dependencies both: prev {prev} > min_left {min_left}, current {punct[i]['id']} > max_left {max_left}")
                    punct[i]['head'] = [token['id'] for token in const_left if token['head'] == min_left][0]
                    # print('HEAD: ', punct[i]['head'])
                elif prev < min_left and punct[i]['id'] > max_left and nextpunc < min_right:
                    # print(f"CASE 6 DUBIOUS: left part contains dependencies both: prev {prev} > min_left {min_left}, current {punct[i]['id']} > max_left {max_left}")
                    punct[i]['head'] = max_right
                    # print('HEAD: ', punct[i]['head'])
                elif prev < min_left and nextpunc < max_right:
                    # print("CASE 7.1 DUBIOUS: right dependent split by another mark")
                    punct[i]['head'] = max_right 
                    # print('HEAD: ', punct[i]['head'])
                # elif nextpunc > min_right and prev < min_left:
                #     print(f"CASE 7.2 DUBIOUS: left dependent split")
                #     punct[i]['head'] = min_left
                
            elif not min_left:
                # print('not min_left:', min_left)
                punct[i]['head'] = [token['id'] for token in const_right if token['head'] == min_right][0]
                # print('HEAD: ', punct[i]['head'])
            else:
                # print('not min left and right:', min_left, min_right)
                punct[i]['head'] = [token['id'] for token in const_left if token['head'] == max_left][0]
                # print('HEAD: ', punct[i]['head'])

            prev = punct[i]['id']

    def apocheck(self, sent):
        """For cases like he ' ll """
        if "'" not in sent['text']:
            return 
        apos = [(idx, token) for idx, token in enumerate(sent['tokens']) if token['form'] == "'"]
        fordel = []
        for idx, a in apos:
            try:
                if sent['tokens'][idx + 1]['form'].lower() == 's' and sent['tokens'][idx + 1]['SemClass'] != 'AUXILIARY_VERBS' and sent['tokens'][idx - 1]['form'] != '#NULL':
                    sent['tokens'][idx - 1]['form'] = f"{sent['tokens'][idx - 1]['form']}'{sent['tokens'][idx + 1]['form']}"
                    fordel.append(a)
                    fordel.append(sent['tokens'][idx + 1])
                elif sent['tokens'][idx + 1]['form'].lower() == 's' and sent['tokens'][idx + 1]['SemClass'] != 'AUXILIARY_VERBS' and sent['tokens'][idx - 1]['form'] == '#NULL':
                    sent['tokens'][idx + 1]['form'] = f"'{sent['tokens'][idx + 1]['form']}"
                    try:
                        sent['tokens'][idx - 2]['misc'] = 'SpaceAfter=No'
                    except IndexError:
                        pass
                    fordel.append(a)
                elif sent['tokens'][idx + 1]['form'].lower() in {'ll', 's', 've', 'd', 're', 'm'} and sent['tokens'][idx - 1]['form'] != '#NULL':
                    sent['tokens'][idx + 1]['form'] = f"'{sent['tokens'][idx + 1]['form']}"
                    sent['tokens'][idx - 1]['misc'] = 'SpaceAfter=No'
                    fordel.append(a)
                    
            except IndexError:
                a['head'] = self.senthead
        if fordel:
            self.shiftheads(sent, fordel)

    def shiftheads(self, sent, fordel):
        """For shifting heads and idx in case of merging"""
        for delt in fordel:
            idx = delt['id']
            # we change heads for all possible tokens which have our markfordelete as head
            for token in sent['tokens']:
                if token['head'] == delt['id']:
                    token['head'] = delt['head']
            # we move token heads for tokens with id > markfordelete id
            for token in sent['tokens']:
                if token['id'] > idx:
                    if type(token['id']) == float:
                        f = True 
                        sid = re.compile('\\b' + str(token['id']).replace('.', '\.') + '(?=:)')
                    else:
                        f = False 
                        sid = re.compile('\\b' + str(token['id']) + '(?=:)')
                    deps = [t for t in sent['tokens'] if t['head'] == token['id']]
                    depseud = [t for t in sent['tokens'] if sid.search(t['deps'])]
                    # print(token['form'], [(t['form'], t['deps']) for t in depseud])
                    token['id'] -= 1
                    for dep in deps:
                        dep['head'] = token['id']
                    for dep in depseud:
                        dep['deps'] = sid.sub(lambda x: str((float(x.group()) if f else int(x.group())) - 1), dep['deps'])
            coref = [t for t in sent['tokens'] if t.get('IsCoref')]
            for c in coref:
                if c['IsCoref'] > idx:
                    c['IsCoref'] -= 1
            sent['tokens'].remove(delt) # check
        sent['text'] = ''
        for token in sent['tokens']:
            if token['misc'] == 'SpaceAfter=No':
                sent['text'] += token['form']
            elif token['misc'] == 'ellipsis':
                continue
            else:
                sent['text'] += token['form'] + ' '

    def emergencyhead(self, sent):
        '''Shouldn't be used normally'''
        heads = [t for t in sent['tokens'] if t['head'] is None]
        if heads:
            for t in heads:
                t['head'] = self.senthead
