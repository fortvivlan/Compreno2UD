import re, csv, pickle, json
mwe = 'morph/lwsplease.csv'
bounded_token_list = []
with open(mwe, 'r', encoding='utf-8') as csvfile:
    reader = csv.reader(csvfile)
    for row in reader:
        a = ','.join(row).count(',')
        if a != 8:
            print(row)

csvfile.close()

