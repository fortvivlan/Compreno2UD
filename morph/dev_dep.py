# mwe
import re
def dev_deps(sent, dot_number, stop, number_csv, dw):
    for i in range(len(sent)):
    # поменяли головы
        if '_' not in str(sent[i]['head']) and int(sent[i]['head']) >= (stop - number_csv) and '.' not in str(sent[i]['head']) and '__' not in str(sent[i]['SemClass']):
            sent[i]['head'] = int(sent[i]['head']) + dw
        # меняем депс


        # депс с точкой
        if dot_number.match(str(sent[i]['deps'])):
            s = re.compile(r'((\d+\.\d+\.\d+|\d+\.\d+))').match(sent[i]["deps"]).group(0)


            # депс с точкой и РАЗДЕЛИТЕЛЕМ
            if '|' in sent[i]['deps']:
                d = re.match(r'.+:.+\|(\d+)', sent[i]['deps']).group(1)
                
                # ДО 1-ГО РАЗДЕЛИТЕЛЯ
                if '_' not in str(sent[i]['deps']) and float(s) >= (stop - number_csv):
                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+))', f'{float(s) + 1}', sent[i]['deps'])
                # ПОСЛЕ 1-ГО РАЗДЕЛИТЕЛЯ
                if '_' not in str(sent[i]['deps']) and float(d) >= (stop - number_csv) and '.' not in str(sent[i]['deps']):
                    sent[i]['deps'] = re.sub(r'(\|\d+)', f'|{int(d) + 1}', sent[i]['deps'])
                
            # депс с точкой и без разделителя
            else:
                if '_' not in str(sent[i]['deps']) and float(s) >= (stop - number_csv):
                    sent[i]['deps'] = re.sub(r'((\d+\.\d+\.\d+|\d+\.\d+|\d+))', f'{float(s) + 1}', sent[i]['deps'])
        
        
        # депс без точки
        else:

            # депс без точки с РАЗДЕЛИТЕЛЕМ
            if '|' in sent[i]['deps']:
                s = re.match(r'(\d+):.+\|\d+', sent[i]['deps']).group(1)
                d = re.match(r'\d+:.+\|(\d+)', sent[i]['deps']).group(1)
                
                # ДО 1-ГО РАЗДЕЛИТЕЛЯ
                if '_' not in str(sent[i]['deps']) and int(s) >= (stop - number_csv):
                    sent[i]['deps'] = re.sub(s, f'{int(s) + 1}', sent[i]['deps'])

                # ПОСЛЕ ПЕРВОГО РАЗДЕЛИТЕЛЯ
                if '_' not in str(sent[i]['deps']) and int(d) >= (stop - number_csv):
                    sent[i]['deps'] = re.sub(r'(\|\d+)', f'|{int(d) + 1}', sent[i]['deps'])


            # депс без точки и без разделителя
            s = re.compile(r'(\d+)\:(\w+|\w+:\w+|\w+:\w+:\w+)')
            if s.fullmatch(sent[i]["deps"]):
                a = int(s.fullmatch(sent[i]["deps"]).group(1))
                if '_' not in str(sent[i]['deps']) and a > (stop - number_csv) and '__' not in str(sent[i]['SemClass']):
                    sent[i]['deps'] = re.sub(r'(\d+\:)', f'{a + dw}:', sent[i]['deps'])

            if sent[i]['SemClass'] == '__':
                sent[i]['SemClass'] = '_'