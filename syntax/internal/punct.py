class Punctuation:
    """Unfinished - raw alpha version. Needs to be tested and re-written"""
    
    def punctheads(self, sent):
        """Main method"""
        self.punctuation_quotes(sent)
        self.punctuation_brackets(sent)
        self.punctuation(sent, ',')
        self.punctuation(sent, '.,!?:;-', comma=True)

    def punctuation_quotes(self, sent):
        quotes = [token for token in sent['tokens'] if token['lemma'] == '"']
        if not len(quotes) % 2:
            for idx in range(1, len(quotes), 2):
                const = [token for token in sent['tokens'] if quotes[idx - 1]['id'] < token['id'] < quotes[idx]['id']]
                if const:
                    heads = [t['head'] for t in const]
                    if None in heads:
                        print(sent['text'])
                    headmax = max([t['head'] for t in const if t['head']])
                    headmin = min([t['head'] for t in const if t['head']])
                    if quotes[idx - 1]['id'] < headmax < quotes[idx]['id']:
                        head = [t['id'] for t in const if t['head'] == headmin][0]
                    elif headmax < quotes[idx - 1]['id'] or headmax > quotes[idx]['id']:
                        head = [t['id'] for t in const if t['head'] == headmax][0]
                else:
                    head = -1
                quotes[idx - 1]['head'] = head
                quotes[idx]['head'] = head

    def punctuation_brackets(self, sent):
        brackets = [token for token in sent['tokens'] if token['lemma'] in '()']
        count = 0
        prev = 0
        if not len(brackets) % 2:
            for idx in range(len(brackets)):
                if brackets[idx]['lemma'] == '(':
                    count += 1
                    prev = idx
                    continue
                if brackets[idx]['lemma'] == ')' and idx > 0:
                    const = [token for token in sent['tokens'] if brackets[prev]['id'] < token['id'] < brackets[idx]['id']]
                    if const:
                        headmin = min([t['head'] for t in const])
                        headmax = max([t['head'] for t in const])
                        if brackets[idx - 1]['id'] < headmax < brackets[idx]['id']:
                            head = [t['id'] for t in const if t['head'] == headmin][0]
                        elif headmax < brackets[idx - 1]['id'] or headmax > brackets[idx]['id']:
                            head = [t['id'] for t in const if t['head'] == headmax][0]
                    else:
                        head = -1
                    brackets[idx]['head'] = head
                    if brackets[prev]['lemma'] == '(':
                        brackets[prev]['head'] = head

    def punctuation(self, sent, punc, comma=False):
        punct = [token for token in sent['tokens'] if token['lemma'] in punc]
        prev = 0
        for i in range(len(punct)):
            if comma and punct[i]['lemma'] == ',':
                prev = punct[i]['id']
                continue
            # print('Mark:', punct[i]['form'], punct[i]['id'])
            if i < len(punct) - 1:
                nextpunc = punct[i + 1]['id']
            else:
                if punct[i]['id'] == len(sent['tokens']):
                    punct[i]['head'] = [token['id'] for token in sent['tokens'] if token['head'] == 0][0]
                    break
                nextpunc = sent['tokens'][-1]['id']
                endsent = True
            const_left = [token for token in sent['tokens'] if prev < token['id'] < punct[i]['id'] and token['pos'] != 'PUNCT']
            const_right = [token for token in sent['tokens'] if punct[i]['id'] < token['id'] < nextpunc and token['pos'] != 'PUNCT']
            # print('Left:', *[token['form'] for token in const_left])
            # print('Right:', *[token['form'] for token in const_right])
            heads = [token['head'] for token in const_left if token['head']]
            if const_left and heads:
                max_left = max(heads)
                min_left = min(heads)
            else:
                min_left = 0 
                max_left = 0
            if not const_right:
                punct[i]['head'] = [token['id'] for token in sent['tokens'] if token['head'] == max_left][0]
                # print('no right constituent\n')
                continue
            heads = [token['head'] for token in const_right if token['head']]
            if heads:
                max_right = max(heads)
                min_right = min(heads)
            else:
                max_right = 0 
                min_right = 0
            if min_left and min_right:
                if prev < min_right < punct[i]['id']:
                    punct[i]['head'] = [token['id'] for token in const_right if token['head'] == min_right][0]
                elif punct[i]['id'] < max_left < nextpunc:
                    punct[i]['head'] = [token['id'] for token in const_left if token['head'] == max_left][0]
                elif prev > min_right and punct[i]['id'] > min_right:
                    punct[i]['head'] = [token['id'] for token in const_left if token['head'] == min_left][0]
                elif punct[i]['id'] < max_left and nextpunc < max_left:
                    punct[i]['head'] = [token['id'] for token in const_right if token['head'] == max_right][0]
                elif prev > min_left and punct[i]['id'] > max_left:
                    punct[i]['head'] = [token['id'] for token in const_left if token['head'] == min_left][0]
            elif not min_left:
                punct[i]['head'] = [token['id'] for token in const_right if token['head'] == min_right][0]
            else:
                punct[i]['head'] = [token['id'] for token in const_left if token['head'] == max_left][0]

            # print()
            prev = punct[i]['id']
        # какой-то гребаный костыль
        if punct and punct[-1]['lemma'] == '.':
            senthead = [t['id'] for t in sent['tokens'] if t['head'] == 0][0]
            punct[-1]['head'] = senthead 