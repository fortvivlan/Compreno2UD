### A Russian tagset for UD

Updated: 20 Jan 2023   
Based on [A Russian tagset for UD 2.x](https://github.com/dialogue-evaluation/GramEval2020/blob/master/UDtagset/UD-Russian_tagset.md)

## Parts of speech (UPOS)

|UPOS tag|Description (ru)|Description (en)|Examples|
|---|---|---|---|
|ADJ|прилагательное,порядковое числительное|adjective|второй, фактический, должен, полный|
|ADP|предлог|preposition|в, по, с, из-за, около|
|ADV|наречие, местоимение-наречие|adverb|также, где, более, можно, стремительно|
|AUX|вспомогательный грамматический показатель|auxiliary|быть, дать|
|VERB|глагол (вкл. причастие, деепричастие)|verb|мочь, закрыть, иметь, нет, стать|
|CCONJ|сочинительный союз|coordinating conjunction|и, а, но, или, либо|
|SCONJ|подчинительный союз|subordinating conjunction|что, как, хотя, ведь, тогда, ибо, если|
|DET|местоимение-прилагательное|determiner (adjectival pronoun)|наш, такой, какой, всякий, некоторый, весь|
|INTJ|междометие|iterjection|вот, ну, увы, черт, ох, ура|
|NOUN|существительное (нарицательное)|noun|объявление, пояс, мечта, вещь, край, официант|
|NUM|числительное|numeral|четыреста, сорок, семь, оба, 1,5, 17:45, 92|
|PART|частица|particle|не, да, ж, уж, мол, вот, так, хоть, лишь|
|PRON|местоимение-существительное|pronoun (nominal)|он, я, иной, кто, какой-то, всякий, этот, сам, свой|
|PROPN|существительное (собственное)|proper noun|Россия, Аркадий, Жуков, Масиас, РФ, Минобрнауки,YouTube|
|PUNCT|пунктуация|punctuation mark|,, ., ", -, :, ), (, ?, !, …|
|SYM|символ|symbol|%, $, №, °, €, +, =, №))|
|X|другое|foreign and non-words|the, of, Ear-It, MobilCom|

## Grammatical features (FEAT)

| Cat=Feat | Description (ru) | Description (en) | UPOS | Examples|
|---|---|---|---|---|
| Abbr=Yes | аббревиатура | abbreviation | ADJ,DET,NOUN,NUM,PRON,PROPN,VERB | РФ, FAO, CNN, тыс., Ту-134 |
| Animacy=Anim | одушевленное | animate | ADJ,DET,NOUN,NUM,PRON,PROPN,VERB* | актер, пчела, Александр, все, Путин, союзник |
| Animacy=Inan | неодушевленное | inanimate | ADJ,DET,NOUN,NUM,PRON,PROPN,VERB* | правда, крышка, это, сторона, Россия |
| Aspect=Imp | несовершенный вид | imperfective aspect | VERB | собирать, совершать, иметь, передавать, быть, появляться |
| Aspect=Perf | совершенный вид | perfective aspect | VERB | отпасть, составить, коснуться, расположить, увеличить |
| Case=Acc | винительный падеж | accusative case | ADJ,AUX*,DET,NOUN,NUM,PRON,PROPN,VERB* | организацию, безопасность, космический, серьёзную, субботу |
| Case=Dat | дательный падеж | dative case | ADJ,AUX*,DET,NOUN,NUM,PRON,PROPN,VERB* | словам, инициативе, времени, данным, Камчатке |
| Case=Gen | родительный падеж | genitive case | ADJ,AUX*,DET,NOUN,NUM,PRON,PROPN,VERB* | года, нас, группы, августа, города, полета |
| Case=Ins | творительный падеж | instrumental case | ADJ,AUX*,DET,NOUN,NUM,PRON,PROPN,VERB* | собой, помощью, ними, едиными, причиной, звучанием |
| Case=Loc | предложный падеж | locative case | ADJ,AUX*,DET,NOUN,NUM,PRON,PROPN,VERB* | том, этом, мире, тяжелом, Нью-Йорке, результате, пропуске |
| Case=Nom | именительный падеж | nominative case | ADJ,AUX*,DET,NOUN,NUM,PRON,PROPN,VERB | она, это, Москва, первый, президент, Игорь |
| Case=Par | партитив (2-ой родит.) | partitive case | NOUN | виду, спору, разу, толку, дому |
| Case=Voc | звательный падеж | vocative case | NOUN,PROPN | господи, Зин, Сереж, ба |
| Degree=Cmp | сравнительная степень | comparative | ADJ,ADV | более, позднее, дальше, лучше, строже, больше |
| Degree=Pos | позитивная степень | positive | ADJ,ADV | готовы, теплое, возможные, виновными, жестоко |
| Degree=Sup | превосходная степень | superlative | ADJ,ADV | важнейший, худшим, наибольший, лучшая, величайшее |
| Foreign=Yes | иностранное слово | foreign word | PROPN,X | Kia, G-RO, Terra, Buena, Club, YouTube, News |
| Gender=Fem | женский род | feminine gender | ADJ,AUX,DET,NOUN,NUM,PRON,PROPN,VERB | сторона, сильная, гололедица, сила, улицах, машина |
| Gender=Masc | мужской род | masculine gender | ADJ,AUX,DET,NOUN,NUM,PRON,PROPN,VERB | он, водомет, документ, сценарист, театр, родственник |
| Gender=Neut | средний род | neuter gender | ADJ,AUX,DET,NOUN,NUM,PRON,PROPN,VERB | это, горение, прощание, прошло, стало, изъятого|
| Mood=Cnd | условное наклонение | conditional | AUX,SCONJ | хотел, была, хотел, взяли|
| Mood=Imp | императив | imperative | AUX,VERB | ведите, поддержите, смотрите, убей, дай, будь, подавайте, вызывай |
| Mood=Ind | индикатив | indicative | AUX,VERB | делают, думаю, возлагается, имел, собирается, составило, сообщили |
| Number=Plur | множественное число | plural | ADJ,AUX,DET,NOUN,PRON,PROPN,VERB | мы, градусов, говорили, главы, времена, источников, близки |
| Number=Sing | единственное число | singular | ADJ,AUX,DET,NOUN,PRON,PROPN,VERB | он, работа, получилась, история, будь, вызывай, тем |
| Person=1 | 1-е лицо | first | AUX,PRON,VERB | я, мы, напомним, смотрим, хочу, понимаю |
| Person=2 | 2-е лицо | second | AUX,PRON,VERB | вы, ты, вас, можешь, понимаете, дайте, остаетесь, хотите, говоришь |
| Person=3 | 3-е лицо | third | AUX,PRON,VERB | он, они, может, устанавливаются, работает, оставляет, им |
| Polarity=Neg | отрицательная полярность | negative polarity | ADV,DET,PART,PRON,VERB("нет") | не, несмотря, ни, невзирая, нет, нет-нет, никто, никакой |
| Tense=Fut | будущее время | future | AUX,VERB | будет, примет, изменит, придется, сохранит, пройдут |
| Tense=Past | прошедшее время | past | AUX,VERB | было, отметил, разделила, добились, сорвали, подчеркнул |
| Tense=Pres | настоящее время | present | AUX,VERB | есть, склоняется, содержится, воздерживаясь, предупреждает, уменьшаются |
| Variant=Short | краткая форма | short form | ADJ,DET,VERB* | уверены, должен, удобно, актуально, известно |
| VerbForm=Conv | деепричастие | converb | AUX,VERB | опустившись, комментируя, подчеркнув, выиграв, ожидая, отметив |
| VerbForm=Fin | финитная форма | finite | AUX,VERB | стоило, был, являются, передавал, направил |
| VerbForm=Inf | инфинитив | infinitive | AUX,VERB | выработать, иметь, проводить, оплачивать, допустить |
| VerbForm=Part | причастие | participle | AUX,VERB | уходящего, данный, поврежден, затруднено, скопившихся |
| Voice=Act | активный залог | active | AUX,VERB | сообщили, отметив, предупредило, продолжал, оскорблять |
| Voice=Mid | средний залог | middle | VERB(reflexive) | является, отмечается, избавиться, обзавестись, находился |
| Voice=Pass | пассивный залог | passive | VERB* | вызванный, ранены, совершенные, убеждены, развернутой |

\* VERB*: participle forms

## SynTagRus tagset

| UPOS | Set of Vategories | Notes |
|---|---|---|
| ADJ | Animacy,Case,Degree,Gender,Number | if Case=Acc |
| ADJ | Animacy,Case,Degree,Number | if Number=Plur, Case=Acc, ordinal numerals |
| ADJ | Animacy,Case,Gender,Number |  |
| ADJ | Case,Degree,Gender,Number |  |
| ADJ | Case,Degree,Gender,Number,Variant |  |
| ADJ | Case,Degree,Number |  |
| ADJ | Case,Gender,Number |  |
| ADJ | Degree |  |
| ADJ | Degree,Gender,Number,Variant |  |
| ADJ | Degree,Number,Variant |  |
| ADJ | Foreign |  |
| ADJ | _ |  |
| ADP | _ |  |
| ADV | Degree |  |
| ADV | Polarity |  |
| AUX | Aspect,Case,Gender,Number,Tense,VerbForm,Voice |  |
| AUX | Aspect,Case,Number,Tense,VerbForm,Voice |  |
| AUX | Aspect,Gender,Mood,Number,Tense,VerbForm,Voice |  |
| AUX | Aspect,Mood,Number,Person,Tense,VerbForm,Voice |  |
| AUX | Aspect,Mood,Number,Person,VerbForm,Voice |  |
| AUX | Aspect,Mood,Number,Tense,VerbForm,Voice |  |
| AUX | Aspect,Tense,VerbForm,Voice |  |
| AUX | Aspect,VerbForm,Voice |  |
| AUX | _ |  |
| CCONJ | _ |  |
| DET | Animacy,Case,Degree,Gender,Number |  |
| DET | Animacy,Case,Degree,Number |  |
| DET | Animacy,Case,Gender,Number |  |
| DET | Case,Degree,Gender,Number |  |
| DET | Case,Degree,Number |  |
| DET | Case,Gender,Number |  |
| DET | Case,Number |  |
| DET | Gender,Number |  |
| DET | _ |  |
| INTJ | _ |  |
| NOUN | Animacy,Case,Gender,Number |  |
| NOUN | Animacy,Case,Number |  |
| NOUN | Animacy,Gender |  |
| NOUN | Case,Degree,Gender,Number |  |
| NOUN | _ |  |
| NUM | Animacy,Case |  |
| NUM | Animacy,Case,Gender |  |
| NUM | Case |  |
| NUM | Case,Gender |  |
| NUM | _ |  |
| PART | Mood |  |
| PART | Polarity |  |
| PART | _ |  |
| PRON | Animacy,Case,Gender,Number |  |
| PRON | Animacy,Case,Number |  |
| PRON | Animacy,Gender,Number |  |
| PRON | Case |  |
| PRON | Case,Gender,Number,Person |  |
| PRON | Case,Number,Person |  |
| PRON | Number,Person |  |
| PRON | _ |  |
| PROPN | Animacy,Case,Foreign,Gender,Number |  |
| PROPN | Animacy,Case,Gender |  |
| PROPN | Animacy,Case,Gender,Number |  |
| PROPN | Animacy,Case,Number |  |
| PROPN | Animacy,Gender |  |
| PROPN | Animacy,Gender,Number |  |
| PROPN | Case,Degree,Gender,Number |  |
| PROPN | Case,Degree,Number |  |
| PROPN | Foreign |  |
| PROPN | Number |  |
| PROPN | _ |  |
| PUNCT | _ |  |
| SCONJ | Mood |  |
| SCONJ | _ |  |
| SYM | _ |  |
| VERB | Animacy,Aspect,Case,Gender,Number,Tense,VerbForm,Voice |  |
| VERB | Animacy,Aspect,Case,Number,Tense,VerbForm,Voice |  |
| VERB | Aspect,Case,Gender,Number,Tense,VerbForm,Voice |  |
| VERB | Aspect,Case,Number,Tense,VerbForm,Voice |  |
| VERB | Aspect,Gender,Mood,Number,Tense,VerbForm,Voice |  |
| VERB | Aspect,Gender,Number,Tense,Variant,VerbForm,Voice |  |
| VERB | Aspect,Mood,Number,Person,Tense,VerbForm,Voice |  |
| VERB | Aspect,Mood,Number,Person,VerbForm,Voice |  |
| VERB | Aspect,Mood,Number,Tense,VerbForm,Voice |  |
| VERB | Aspect,Number,Tense,Variant,VerbForm,Voice |  |
| VERB | Aspect,Tense,VerbForm,Voice |  |
| VERB | Aspect,VerbForm,Voice |  |
| VERB | Voice |  |
| VERB | _ |  |
| X | Foreign |  |
| X | _ |  |