from syntax.internal.eudru import RuEnhancedConverter

class EnhancedConverter:
    def chooselang(self, lang):
        try:
            return eval(f'{lang}EnhancedConverter()')
        except NameError:
            print('No such language!')
            return None