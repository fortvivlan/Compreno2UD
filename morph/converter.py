#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import re, csv, pickle, json

# для тестирования изнутри нужно morph в импортах убрать
from morph.morphology.pos_module import Pos_module
from morph.morphology.feats_module import Feats_module
from morph.morphology.fixes import Fixes

class Converter:
    '''основной класс конвертера'''
    def __init__(self, mwe, infile, outfile):
        self.feats_module = Feats_module()
        self.fixes = Fixes(r'C:\Users\пк\Desktop\converter Compreno2UDMorph\morphology\ImpToPerf.txt', r'C:\Users\пк\Desktop\converter Compreno2UDMorph\morphology\pos_invariable.txt')
        # полные пути лучше не делать, старайтесь относительные везде оставлять, и если получится без слешей, еще лучше, или ставить слеши прямые - для совместимости с unix-системами
        self.pos_module = Pos_module()
        #так, self сделала, у utils есть одна только одна функция - convert wordlines, нужно подумать стоит ли ее разбить
        self.wordline_pattern = re.compile(r'^.+?\t.+?[A-Za-z]+')
        self.foreign_bounded_token = re.compile(r'[A-za-z]+ [A-za-z]+')
        self.number_bounded = re.compile(r'\d+,?\d*?-\d+,?\d*?')
        self.hasch_number = re.compile(r'\d+#:\d+')
        self.mwe = mwe
        self.infile = infile
        self.outfile = outfile

    def convert_wordlines(self):
        bounded_token_list = []
        with open(self.mwe, 'r', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            csv_dict = {}  # {(old_token, pos): [{part1:v, pos:v...},{part2:v...}}
            parts = []
            word_find = 0
            for row in reader:
                if row[0][0].isalpha():
                    old_token = (f"{row[0]} | {row[1]}")
                    bounded_token_list.append(row[0])
                    word_find = 1
                if word_find:
                    if row[0] == '%':
                        parts.append({'id': None, 'form': row[1], 'lemma': row[2], 'pos': row[3], 'grammemes': row[4], 'head': row[5], 'deprel': row[6]})
                    if row[0] == '##':
                        word_find = 0
                        csv_dict[old_token] = parts
                        parts = []
        csvfile.close()
        data = []
        with open(self.infile, 'r') as f, open(self.outfile, 'w', encoding="utf8") as out: # 'rb' = read binary, json у нас не бинарник
            out.write(f"# global.columns =  ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC SEMSLOT SEMCLASS\n")
            for line in f:
                data.append(json.loads(line))
            sent_id = 0
            for i in range(len(data) - 1):
                print('Конвертация ...')
                print(data[i])#это зачем? непонятно... - принты часто кидают для дебага, возможно, это оно
                text = ''#это дроп (upd: уже нет...)
                word_counter = 0
                bounded = 0
                bounded_fgn = 0
                while word_counter != len(data[sent_id]['tokens']):
                    w = data[sent_id]['tokens'][word_counter]
                    if word_counter == 0 or word_counter == len(data[sent_id]['tokens']) - 1 \
                            or w['pos'] == 'NOUN' and w['grammemes'] != None and 'Case' in w['grammemes'] and w['grammemes']['Case'] == 'ZeroCase' \
                            or w['pos'] == 'Prefixoid' \
                            or w['pos'] in ('NOUN', 'ADJ') and w['grammemes'] != None and type(w['grammemes']) != str and 'Case' in w['grammemes'] and 'DativeSpecial' in w['grammemes']['Case']:
                        text += f"{w['form']}"
                    else:
                        text += f" {w['form']}"
                    word_counter += 1
                out.write(f"# sent_id = {sent_id + 1}\n")
                out.write(f"# text = {text}\n")


                for word in data[sent_id]['tokens']:

                    '''if word['grammemes'] == None:
                        word['grammemes'] = '_'''#в новом json теперь по дефолту стоят _ у граммем, если их нет!
                    
                    if re.compile(r'\w+- \w+').fullmatch(word['form']):
                        word['form'] = word['form'].replace(' ', '')#!убирает пробел из слова, которое пишется через дефис
                    word['pos'] = self.pos_module.convert_pos(word['form'], word['lemma'], word['pos'], word['grammemes'], word['deprel'], word['SemSlot'], word['SemClass'])
                    word['pos'] = self.fixes.pos_invariable_fix(word['form'], word['pos'])
                    if word['pos'] == 'VERB':#!мб Verb, а не VERB? - если мы уже сконвертировали чр, а это произошло в 79 строке, то VERB
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
                        new_feats = self.feats_module.filter_feats(word['form'], word['lemma'], word['pos'], word['grammemes'], word['SemSlot'], word['SemClass'])
                        if type(new_feats) == str:
                            ud_feats = new_feats
                        else:
                            ud_feats = '|'.join(new_feats)

                    out.write(f"{word['id']}\t{word['form']}\t{word['lemma']}\t{word['pos']}\t_\t{ud_feats}\t{word['head']}\t{word['deprel']}\tdeps\tmisc\t{word['SemSlot']}\t{word['SemClass']}\n")
                    word_counter -= 1
                    if word_counter == 0:
                        break
                sent_id += 1
                out.write('\n')
                print(f'Закончено: {sent_id}')
        out.close()
        f.close()

'''if __name__ == '__main__':
    print('Starting conversion')

    # args = parse()
    convert_wordlines(indir, outdir)

    print('DONE')'''
if __name__ == '__main__':
    mwe = r'morph\morphology\mwe.csv'
    indir = r'morph\morphology\first(new).json'
    outdir = r'morph\morphology\converted.conllu'
    f = Converter(mwe, indir, outdir)
    #Converter.convert_wordlines(indir, outdir)
    # f.convert_wordlines()
