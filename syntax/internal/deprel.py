from syntax.internal.deprelru import RuDeprelConverter

class DeprelConverter:
    def chooselang(self, lang):
        try:
            return eval(f'{lang}DeprelConverter()')
        except NameError:
            print('No such language!')
            return None