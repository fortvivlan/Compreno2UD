import os, argparse, mmap
from morph.converter import Converter as Morph
from syntax.converter import Converter as Syntax 

class Compreno2UD:
    """
    The main class for Compreno2UD conversion. Runs syntax conversion first, 
    then morphology conversion. Required arguments:
    mwe - .csv file with multiword expressions (internal)
    infile - path to input .json file from Compreno API
    temp - path for temporary .json file with the results of syntax conversion
    outfile - path for resulting .conllu file
    """
    def __init__(self, lang, mwe, infile, temp, outfile):
        self.temp = temp
        numlines = self.get_num_lines(infile) # for tqdm
        self.syntax = Syntax(lang, infile, temp, numlines)
        self.morph = Morph(lang, mwe, temp, outfile)

    def convert(self):
        self.syntax.convert() 
        # self.morph.convert_wordlines()
        # os.remove(self.temp)

    def get_num_lines(self, file_path):
        fp = open(file_path, "r+", encoding='utf8')
        buf = mmap.mmap(fp.fileno(), 0)
        lines = 0
        while buf.readline():
            lines += 1
        return lines

if __name__ == '__main__':

    mwe = 'morph/total_ru.csv'
    temp = 'data/temp.json'
 
    ## to run in command line:
    ##########################

    # parser = argparse.ArgumentParser(description='Compreno2UD Converter')
    # parser.add_argument('lang', type=str, help='Language of conversion, example: Ru, En')
    # parser.add_argument('infile', type=str, help='Input file for conversion')
    # parser.add_argument('outfile', type=str, help='Output path for result')
    # args = parser.parse_args()
    # converter = Compreno2UD(lang, mwe, args.infile, temp, args.outfile)

    ## to run in IDE:
    #################

    lang = 'Ru'
    infile = 'data/Russian_full.json'
    outfile = 'data/res.conllu'
    # infile = 'data/test_ru.json'
    # outfile = 'data/res_ru.conllu'   
    converter = Compreno2UD(lang, mwe, infile, temp, outfile)
    converter.convert()
