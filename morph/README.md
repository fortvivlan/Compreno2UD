## Короткий гайд по конвертеру (только для морфологии)

Наша задача - сконвертировать части речи (ЧР, PoS, pos_tags) и грамматические категории с граммемами (feats) из формата Компрено в UD.
В компрено больше ЧР и система грам. категорий более сложная и подробная.
Однако, есть и неприятные вещи: некоторые ЧР в UD нельзя напрямую сконвертировать из компрено (например, DET).
Подробнее это дело надо изучать, сверяясь с [тагсетом UD](https://github.com/dialogue-evaluation/GramEval2020/blob/master/UDtagset/UD-Russian_tagset.md).
К сожалению, я не нашла нигде готового тагсета компрено, но по моим наблюдениям, для русского есть следующие ЧР:
```
compreno_pos_labels = ['Adjective',
 'Adverb',
 'Article',
 'Conjunction',
 'Interjection',
 'Noun',
 'Numeral',
 'Particle',
 'Predicative',
 'Prefixoid',
 'Preposition',
 'Pronoun',
 'Verb']
```

Еще сложнее с feats: этого добра больше, для каждой ЧР надо прописывать список нужных, подумать, как быть с теми ЧР, которые не симметричны между форматами.
Над конвертацией как ЧР, так и feats я только начала работу. Уже найденные проблемки описаны [здесь](https://docs.google.com/document/d/1tXWvyMLJ_T8w0Xi8h8KOrlnsfaAiALS_LVpKHSY8j7s/edit?usp=sharing).

UDP: [Здесь](GramEval2020-SynTagRus-train-v2.txt), грубо говоря, образец корпуса в UD, который должен получиться (GramEval2020-SynTagRus-train-v2.txt). Это результат [автоконвертации](https://github.com/Kira-D/SynTagRus_convertor) Синтагруса с некоторыми ручными исправлениями.

### Как запустить

В консоли из этой директории
```
python3 convertor.py --indir путь_к_compreno_text.txt --outdir файл_куда_записать.txt
```
Но я настоятельно советую захардкодить директории (коммент про это есть в коде), чтобы не вызывать из консоли каждый раз, когда хочется потестировать код.

Соответственно, разбор в формате компрено лежит [здесь](https://github.com/moshemm/SEMarkup_project/blob/main/compreno_text.txt).
