import pickle

EN = {}

with open('syntax/internal/sslots/acl.txt', encoding='utf8') as f:
    EN['acl'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/aclrelcl.txt', encoding='utf8') as f:
    EN['aclrel'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/advcl.txt', encoding='utf8') as f:
    EN['advcl'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/advmod.txt', encoding='utf8') as f:
    EN['advmod'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/amod.txt', encoding='utf8') as f:
    EN['amod'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/appos.txt', encoding='utf8') as f:
    EN['appos'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/case.txt', encoding='utf8') as f:
    EN['case'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/cc.txt', encoding='utf8') as f:
    EN['cc'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/ccomp.txt', encoding='utf8') as f:
    EN['ccomp'] = {x.strip() for x in f.readlines()}
EN['conj'] = {'Modifier_HyphenoidCore', 'Modifier_HyphenoidNonCore', 'ModifierSlash_Second', 
                'ModifierSlashNum_Second', 'NominalPostModOr_And', 'Specification_ElliptedVerb', 
                'Specification_PseudoCommonChild', 'SpecificationClause_Comma'}
with open('syntax/internal/sslots/compound.txt', encoding='utf8') as f:
    EN['compound'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/csubj.txt', encoding='utf8') as f:
    EN['csubj'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/det.txt', encoding='utf8') as f:
    EN['det'] = {x.strip() for x in f.readlines()}
EN['discoursePP'] = {'Situative_Introductory_ForInterjectionLikeParticle', 'TagLexical', 'Invariable'}
EN['iobj'] = {'Object_Dative'}
with open('syntax/internal/sslots/mark.txt', encoding='utf8') as f:
    EN['mark'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/npmod.txt', encoding='utf8') as f:
    EN['npmod'] = {x.strip() for x in f.readlines()}
EN['poss'] = {'PossessorPremodGenitiveS', 'PossessorPremod', 'GenitiveS', 'Idiomatic_NominalPremodifier_Possessive', 
                'Idiomatic_PossesorPremod', 'PossessorPostmodGenitiveS', 'PossessorPremodGenitiveS_Numeral'}
with open('syntax/internal/sslots/nummod.txt', encoding='utf8') as f:
    EN['nummod'] = {x.strip() for x in f.readlines()}
EN['nummodent'] = {'Interval_From', 'Interval_NeutralEC', 'Interval_StartingLimit_Hyphen', 'Proportion_Number'}
with open('syntax/internal/sslots/obj.txt', encoding='utf8') as f:
    EN['obj'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/oblnmod.txt', encoding='utf8') as f:
    EN['oblnmod'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/parataxis.txt', encoding='utf8') as f:
    EN['parataxis'] = {x.strip() for x in f.readlines()}
with open('syntax/internal/sslots/xcomp.txt', encoding='utf8') as f:
    EN['xcomp'] = {x.strip() for x in f.readlines()}
EN['detlist'] = {'any', 'another'} 
EN['discourse'] = {'yes', 'yeah'}
EN['composite'] = set()

pickle.dump(EN, open('syntax/internal/en.slots', 'wb'))