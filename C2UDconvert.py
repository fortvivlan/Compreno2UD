import os, argparse
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
        self.syntax = Syntax(lang, infile, temp)
        self.morph = Morph(lang, mwe, temp, outfile)

    def convert(self):
        self.syntax.convert() 
        self.morph.convert_wordlines()
        # os.remove(self.temp)

if __name__ == '__main__':

    mwe = 'morph/lwsplease.csv'
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
    infile = 'data/first.json' # если слеши ставить прямые, то питону пофиг на r и какая операционная система, он разберется, удобно для совместимости
    outfile = 'data/res.conllu'
    
    converter = Compreno2UD(lang, mwe, infile, temp, outfile)
    converter.convert()