# -*- coding: utf-8 -*-

import pickle
import re
import csv

# cheker = []
# with open('D:\Compreno\converted_full_notest.bin', 'rb') as file:
#     data = pickle.load(file)
#     for i in range(len(data)):
#         if i == 11155:
#             for word in data[i]:
#                 print(word)
#             # print(data[i])
# # print(set(cheker))
# file.close()

import conllu
from conllu import parse_incr

# bounded_token_list = []
# with open('D:\Compreno\SEMarkup_project\compreno2UD\morphology\mwe.csv', 'r', encoding='utf-8') as csvfile:
#     reader = csv.reader(csvfile)
#     for row in reader:
#         if row[0][0].isalpha():
#             bounded_token_list.append(row[0])
# csvfile.close()

data_file = open("D:\\UD_text_full_notest.conllu", "r", encoding="utf-8")
for sentence in parse_incr(data_file):
    for word in sentence:
        if ' ' in word['form']:
            print(word, word['upos'])

