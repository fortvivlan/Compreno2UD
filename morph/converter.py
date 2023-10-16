import re, csv, pickle, json

from morph.feats_module_en import Feats_module_en
from morph.pos_module_en import Pos_module_en
from morph.fix_lemmas_en import Fixes_en

from morph.pos_module import Pos_module
from morph.feats_module import Feats_module
from morph.fixes import Fixes

class Converter:
    '''основной класс конвертера'''
    def __init__(self, lang, mwe, infile, outfile):
        self.feats_module_en = Feats_module_en()
        self.pos_module_en = Pos_module_en()
        self.fix_lemmas_en = Fixes_en()
        self.lang = lang
        self.feats_module = Feats_module()
        self.fixes = Fixes('morph/ImpToPerf.txt', 'morph/pos_invariable.txt')
        self.pos_module = Pos_module()
        self.wordline_pattern = re.compile(r'^.+?\t.+?[A-Za-z]+')
        self.foreign_bounded_token = re.compile(r'[A-za-z]+ [A-za-z]+')
        self.number_bounded = re.compile(r'\d+,?\d*?-\d+,?\d*?')
        self.s_bounded = re.compile(r'[A-za-z]+\'s')
        self.s1_bounded = re.compile(r'[A-za-z]+s\'')
        self.hasch_number = re.compile(r'\d+#:\d+')
        self.neg_bounded = re.compile(r'[A-za-z]+n\'t')
        self.mwe = mwe
        self.infile = infile
        self.outfile = outfile

    def convert_wordlines(self):
        if self.lang == 'Ru':
            bounded_token_list = []
            with open(self.mwe, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                csv_dict = {}  # {(old_token, pos): [{part1:v, pos:v...},{part2:v...}}
                parts = []
                word_find = 0
                for row in reader:
                    if row[0][0].isalpha():
                        old_token = (f"{row[0]}")
                        bounded_token_list.append(row[0])
                        word_find = 1
                    if word_find:
                        if row[0] == '%':
                            parts.append({'id': None, 'form': row[1], 'lemma': row[2], 'pos': row[3], 'grammemes': row[4], 'head': row[6], 'deprel': row[5]})
                        if row[0] == '##':
                            word_find = 0
                            csv_dict[old_token] = parts
                            parts = []
            csvfile.close()
            data = []
            with open(self.infile, 'rb') as f, open(self.outfile, 'w', encoding="utf8") as out:
                out.write(f"# global.columns =  ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC SEMSLOT SEMCLASS\n")
                for line in f:
                    data.append(json.loads(line))
                sent_id = 0
                for i in range(len(data)):
                    print('Конвертация ...')
                    print(data[i]['text'])
                    bounded = 0
                    bounded_fgn = 0
                    out.write(f"# sent_id = {sent_id + 1}\n")
                    out.write(f"# text = {data[sent_id]['text']}\n")

                    for word in data[sent_id]['tokens']:
                        word['p0s'] = word['pos']#это чтобы сохранить старые посы
                        
                        if re.compile(r'\w+- \w+').fullmatch(word['form']):
                            word['form'] = word['form'].replace(' ', '')#!убирает пробел из слова, которое пишется через дефис
                        word['pos'] = self.pos_module.convert_pos(word['form'], word['lemma'], word['pos'], word['grammemes'], word['deprel'], word['SemSlot'], word['SemClass'])
                        word['pos'] = self.fixes.pos_invariable_fix(word['form'], word['pos'])
                        if word['pos'] == 'VERB':
                            word['lemma'] = self.fixes.imp_and_perf(word['lemma'], word['grammemes'])
                        if word['lemma'] == '#Expression':
                            word['pos'] = 'PROPN'
                        if word['lemma'] == '#ForeignWord':
                            word['pos'] = 'X'
                        word['lemma'] = self.fixes.fix_lemmas(word['form'], word['lemma'], word['grammemes'])
                        if self.hasch_number.search(word['form']):
                            word['form'] = word['form'].replace('#', '')
                            word['lemma'] = word['form']
                        if word['form'].lower() in bounded_token_list:
                            bounded = 1
                        if self.foreign_bounded_token.search(word['form']) or self.number_bounded.fullmatch(word['form']):
                            bounded_fgn = 1
                    if bounded:
                        self.fixes.indexation_bounded_csv(data[sent_id]['tokens'], csv_dict, bounded_token_list)
                    if bounded_fgn:
                        self.fixes.bounded_foreign(data[sent_id]['tokens'])
                    self.fixes.merge(data[sent_id]['tokens'])

                    for word in data[sent_id]['tokens']:
                        word_counter = len(data[sent_id]['tokens'])
                        if type(word['grammemes']) == str:
                            ud_feats = word['grammemes']
                        else:
                            new_feats = self.feats_module.filter_feats(word['form'], word['lemma'], word['pos'], word['p0s'], word['grammemes'], word['SemSlot'], word['SemClass'])
                            if word['misc'] == None:
                                word['misc'] = '_'
                            if type(new_feats) == str:
                                ud_feats = new_feats
                            else:
                                ud_feats = '|'.join(new_feats)
                        if word['misc'] == 'None':
                            word['misc'] = '_'
                        else:
                            word['misc'] = word['misc']

                        out.write(f"{word['id']}\t{word['form']}\t{word['lemma']}\t{word['pos']}\t{word['p0s']}\t{ud_feats}\t{word['head']}\t{word['deprel']}\t{word['deps']}\t{word['misc']}\t{word['SemSlot']}\t{word['SemClass']}\n")
                        word_counter -= 1
                        if word_counter == 0:
                            break
                    sent_id += 1
                    out.write('\n')
                    print(f'Закончено: {sent_id}')
            out.close()
            f.close()



        elif self.lang == 'En':
            bounded_token_list = []
            with open(self.mwe, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                csv_dict = {}  # {(old_token, pos): [{part1:v, pos:v...},{part2:v...}}
                parts = []
                word_find = 0
                for row in reader:
                    if row[0][0].isalpha():
                        old_token = (f"{row[0]}")
                        bounded_token_list.append(row[0].lower())
                        word_find = 1
                    if word_find:
                        if row[0] == '%':
                            parts.append({'id': None, 'form': row[1], 'lemma': row[2], 'pos': row[3], 'grammemes': row[4], 'head': row[6], 'deprel': row[5]})
                        if row[0] == '##':
                            word_find = 0
                            csv_dict[old_token] = parts
                            parts = []
            csvfile.close()
            data = []
            with open(self.infile, 'rb') as f, open(self.outfile, 'w', encoding="utf8") as out:
                out.write(f"# global.columns =  ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC SEMSLOT SEMCLASS\n")
                for line in f:
                    data.append(json.loads(line))
                sent_id = 0
                for i in range(len(data)):
                    print('Конвертация ...')
                    print(data[i]['text'])
                    bounded = 0
                    bounded_fgn = 0
                    bounded_neg = 0
                    null = 0
                    out.write(f"# sent_id = {sent_id + 1}\n")
                    out.write(f"# text = {data[sent_id]['text']}\n")

                    for word in data[sent_id]['tokens']:
                        word['p0s'] = word['pos']#это чтобы сохранить старые посы
                        word['pos'] = self.pos_module_en.convert_pos_en(word['form'], word['lemma'], word['pos'], word['grammemes'], word['deprel'], word['SemClass'])
                        word['lemma'] = self.fix_lemmas_en.fix_lemmas_en(word['form'], word['lemma'], word['pos'], word['grammemes'], word['SemSlot'])
                    
                        if word['form'].lower() in bounded_token_list:
                            bounded = 1
                        if self.neg_bounded.search(word['form']):
                            bounded_neg = 1
                        if self.s_bounded.fullmatch(word['form']):
                            bounded_fgn = 1
                        if self.s1_bounded.fullmatch(word['form']):
                            bounded_fgn = 1
                        if word['form'] == "#NULL's" or word['form'] == '#NULL':

                            null = 1
                    

                    if bounded:
                        self.fix_lemmas_en.csv_div(data[sent_id]['tokens'], csv_dict, bounded_token_list)
                    if bounded_fgn:
                        self.fix_lemmas_en.bounded_s(data[sent_id]['tokens'])
                    #while bounded_neg > 0:
                    if bounded_neg:
                        self.fix_lemmas_en.bounded_neg(data[sent_id]['tokens'], data[sent_id]['text'])
                    if null:
                        self.fix_lemmas_en.null_check(data[sent_id]['tokens'])
                        
                    self.fix_lemmas_en.new_line1(data[sent_id]['tokens'])

                    

                    for word in data[sent_id]['tokens']:
                        word_counter = len(data[sent_id]['tokens'])
                        if type(word['grammemes']) == str:
                            ud_feats = word['grammemes']
                        else:
                            new_feats = self.feats_module_en.filter_feats_en(word['form'], word['lemma'], word['pos'], word['grammemes'], word['deprel'], word['SemClass'], word['SemSlot'])
                            if word['lemma'] == '#RomanNumber':
                                word['lemma'] = word['form']
                            if word['misc'] == None:
                                word['misc'] = '_'
                            else:
                                word['misc'] = word['misc']
                            if type(new_feats) == str:
                                ud_feats = new_feats
                            else:
                                
                                ud_feats = '|'.join(new_feats)
                        if word['pos'] == 'VERB' or word['pos'] == 'AUX':
                            if 'Type' in word['grammemes'] and word['grammemes']['Type'][0] == 'ParticipleOne':
                                for word1 in data[sent_id]['tokens']:
                                    if word['id'] == word1['head'] and word1['pos'] == 'AUX' and 'TypeOfVerb' in word1['grammemes'] and word1['grammemes']['TypeOfVerb'][0] == 'Be':
                                        ud_feats = 'Tense=Pres|VerbForm=Part'

                        if 'ReferenceClass' in word['grammemes'] and word['grammemes']['ReferenceClass'][0] == 'RCRelative':
                            for word1 in data[sent_id]['tokens']:
                                if word1['id'] == word['head'] and word1['deprel'] == 'acl:relcl':
                                    ud_feats = 'PronType=Rel'


                        if word['misc'] == 'None':
                            word['misc'] = '_'
                        else:
                            word['misc'] = word['misc']
                        
                        out.write(f"{word['id']}\t{word['form']}\t{word['lemma']}\t{word['pos']}\t{word['p0s']}\t{ud_feats}\t{word['head']}\t{word['deprel']}\t{word['deps']}\t{word['misc']}\t{word['SemSlot']}\t{word['SemClass']}\n")
                        word_counter -= 1
                        if word_counter == 0:
                            break
                    sent_id += 1
                    out.write('\n')
                    print(f'Закончено: {sent_id}')                                    
            out.close()
            f.close()


'''if __name__ == '__main__':

    mwe = r'morphology\mwe.csv'
    lang = 'ru'
    if lang == 'ru':
        indir = r'first(new).json'
        outdir = r'convertedrus.conllu'
    elif lang == 'en':
        indir = r'\Compreno2UD\morph\english.json'
        outdir = r'\data\res.conllu'

    morph = Converter_en(mwe, lang.capitalize(), indir, outdir)
    morph.convert_wordlines()'''