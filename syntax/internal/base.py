from syntax.internal.baseru import RuBaseConverter

class BaseConverter:
    def chooselang(self, lang):
        try:
            return eval(f'{lang}BaseConverter()')
        except NameError:
            print('No such language!')
            return None