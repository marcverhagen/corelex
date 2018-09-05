"""Basic types and Corelex types

Contains the synsets from WordNet that are used as basic types for CoreLex and
the definition of CoreLex types.


== Basic Types

Basic types used when creating CoreLex from WordNet 1.5 are the same as the ones
in Paul Buitelaar's dissertation, listed at

   http://www.cs.brandeis.edu/~paulb/CoreLex/corelex_nouns.basictypes.synset

For CoreLex 2, the same set of types was used. The reason for this is that when
we use the same basic types we can re-use the CoreLex types from the initial
CoreLex. These types are defined as unions of polysemous types, for example acr
is defined as:

	act atr rel     act human_action human_activity attribute relation
 	act evt rel     act human_action human_activity event relation
 	act rel sta     act human_action human_activity relation state
 	act rel	        act human_action human_activity relation

For all basic types, the mapping to synsets was changed. In most cases, the
mapping was to the same synset but the synset identifier (which is the byte
offset in the WordNet data) file had to be updated.

Strategy:
- do this on a case by case basis, looking at each top level type
- for each basic type, find the synset in WN3.1
   - use the number from the lexicographer file
   - for example, the frm basic type in WN1.5 maps to the
     {shape.03.0 form.03.0} synset
   - try to find the same one in WN3.1
- check the definition and the subtypes
   - if they are similar, just update the identifier
   - typically, in WN3.1 the synset(s) will have more hyponyms
   - if not similar, check for alternatives
   - if definition does not exist anymore (eg process.22.0):
      - find closest based on subtypes

From WordNet 1.5 to WordNet 3.1 the noun hierarchy has changed. For example,
there is not a set of 11 toptypes anymore, instead there is only one toptype in
entity.03.0. Almost all basic types from 1.5 were also in 3.1 but there were few
types that pointed to synsets that were split up and even one that did not exist
any more (process.22.0). In many case the synset was at a different position in
the hierarchy. Here is a list of remarks on the new basic types:

   abs: psy is new, gone are time.03.0 space.03.0
   act: similar, but many more subtypes
   art: deeper embedded
   atr: many new subs: sta, spc, tme, frm
   chm: first synset is deeper embedded
   com: is now directly under abstraction
   ent: is now the single top type
   evt: similar, but now includes act.03.0
   lfr: used to be 'life_form organism being living_thing'
        life_form was split off and made its own synset under
        {body.08.0, organic_structure.08.0}
        organism.03.0 being.03.0 are now under living_thing.03.0
   lme: used to be 'linear_measure long_measure', long_measure is a hyponym
        is now deeper in the hierarchy
   loc: similar, but imaginary_place was moved to psy
   mea: last member (quantum) is gone
   mic: expanded synset
   phm: similar, but issue with pro subtype
   pho: this is a new synset, the old 'object inanimate_object physical_object'
        is a hyponym
   pos: similar, but subtype ownership.21.0 is moved up to relation.03.0
   pro: process.22.0 does not exist anymore, process.03.0 seems closest
   spc: very different now
   sta: similar, but many more subtypes
   sub: used to be 'substance matter', but substance.03.0 is now a subtype


== Subsumption among basic types

Some basic types are subtypes of each other, for example 'prt' is a subtype of
'ent'. If a noun falls under two basic types that stand in an ISA relation than
only the most specific one will be taken. In the pairs as listed in
BASIC_TYPES_ISA_RELATIONS_1_5 and BASIC_TYPES_ISA_RELATIONS_3_1, the first type
is more specific than the second.

The pairs for 1.5 were created manually from the hierarchy pictures in Paul
Buitelaar's dissertations. The ones for 3.1 were created by a utility method in
the wordnet module: WordNet.display_basic_type_isa_relations().


== CoreLex Types

CoreLex types are defined as sets of polysemous types or basic types (where
polysemous types consist of two or more basic types). These were defined
manually back in 1998 by Paul Buitelaar and because the basic types are the same
for the new version of CoreLex we can reuse the CoreLex types. The types are
listed in ../legacy/data/corelex_nouns.classes.txt and the CORELEX_TYPES
variable is created from that file using the create_corelex_types_mapping()
function.

However, the CoreLex types were defined to encompass the polysemous types that
were generated from WordNet 1.5, and since the hierarchy changed the polysemous
types for WordNet 3.1 are different and not all of them are covered by the
CoreLex types.

TODO: need to semi-automatically deal with the polysemous types that are not
associated with a CoreLex type.

"""


BASIC_TYPES_1_5 = {

    'abs': [('00012670', 'abstraction')],
    'act': [('00016649', 'act human_action human_activity')],
    'agt': [('00004473', 'causal_agent cause causal_agency')],
    'anm': [('00008030', 'animal animate_being beast brute creature fauna')],
    'art': [('00011607', 'artifact artefact')],
    'atr': [('00017586', 'attribute')],
    'cel': [('00003711', 'cell')],
    'chm': [('08907331', 'compound chemical_compound'),
            ('08805286', 'chemical_element element')],
    'com': [('00018599', 'communication')],
    'con': [('06465491', 'consequence effect outcome result upshot')],
    'ent': [('00002403', 'entity')],
    'evt': [('00016459', 'event')],
    'fod': [('00011263', 'food nutrient')],
    'frm': [('00014558', 'shape form')],
    'grb': [('05115837', 'biological_group')],
    'grp': [('00017008', 'group grouping')],
    'grs': [('05119847', 'social_group'),
            ('05116476', 'people')],
    'hum': [('00004865', 'person individual someone mortal human soul')],
    'lfr': [('00002728', 'life_form organism being living_thing')],
    'lme': [('08322690', 'linear_measure long_measure')],
    'loc': [('00014314', 'location')],
    'log': [('05450515', 'region')],
    'mea': [('00018966', 'measure quantity amount quantum')],
    'mic': [('00740781', 'microorganism')],
    'nat': [('00009919', 'natural_object'),
            ('05715416', 'body_of_water water'),
            ('05720524', 'land dry_land earth ground solid_ground terra_firma')],
    'phm': [('00019295', 'phenomenon')],
    'pho': [('00009469', 'object inanimate_object physical_object')],
    'plt': [('00008894', 'plant flora plant_life')],
    'pos': [('00017394', 'possession')],
    'pro': [('08239006', 'process')],
    'prt': [('05650477', 'part piece')],
    'psy': [('00012517', 'psychological_feature')],
    'qud': [('08310215', 'definite_quantity')],
    'qui': [('08310433', 'indefinite_quantity')],
    'rel': [('00017862', 'relation')],
    'spc': [('00015245', 'space')],
    'sta': [('00015437', 'state')],
    'sub': [('00010368', 'substance matter')],
    'tme': [('09065837', 'time_period period period_of_time amount_of_time'),
            ('09092294', 'time_unit unit_of_time'),
            ('00014882', 'time')]
}


BASIC_TYPES_3_1 = {

    'abs': [('00002137', 'abstraction.03.0 abstract_entity.03.0')],
    'act': [('00030657', 'act.03.0 deed.03.0 human_action.03.0 human_activity.03.0')],
    'agt': [('00007347', 'causal_agent.03.0 cause.03.0 causal_agency.03.0')],
    'anm': [('00015568', 'animal.03.0 animate_being.03.0 beast.03.0 brute.03.0 creature.03.0 fauna.03.0')],
    'art': [('00022119', 'artifact.03.0 artefact.03.0')],
    'atr': [('00024444', 'attribute.03.0')],
    'cel': [('00006484', 'cell.03.0')],
    'chm': [('14842408', 'compound.27.0 chemical_compound.27.0'),
            ('14647071', 'chemical_element.27.0 element.27.0')],
    'com': [('00033319', 'communication.03.0')],
    'con': [('11430739', 'consequence.19.0 effect.19.0 outcome.19.0 result.19.0 event.19.1 issue.19.0 upshot.19.0')],
    'ent': [('00001740', 'entity.03.0')],
    'evt': [('00029677', 'event.03.0')],
    'fod': [('00021445', 'food.03.0 nutrient.03.0')],
    'frm': [('00028005', 'shape.03.0 form.03.0')],
    'grb': [('07957410', 'biological_group.14.0')],
    'grp': [('00031563', 'group.03.0 grouping.03.0')],
    'grs': [('07967506', 'social_group.14.0'),
            ('07958392', 'people.14.0')],
    'hum': [('00007846', 'person.03.0 individual.03.0 someone.03.0 somebody.03.0 mortal.03.0 soul.03.0')],
    'lfr': [('00004258', 'living_thing.03.0 animate_thing.03.0')],
    'lme': [('13624548', 'linear_unit23.0 linear__measure.23.0')],
    'loc': [('00027365', 'location.03.0')],
    'log': [('08648560', 'region.15.1')],
    'mea': [('00033914', 'measure.03.0 quantity.03.0 amount.03.0')],
    'mic': [('01328932', 'microorganism.05.0 micro-organism.05.0')],
    'nat': [('00019308', 'natural_object.03.0'),
            ('09248053', 'body_of_water.17.0 water.17.0'),
            ('09357302', 'land.17.0 dry_land.17.0 earth.17.1 ground.17.0 solid_ground.17.0 terra_firma.17.0')],
    'phm': [('00034512', 'phenomenon.03.0')  ],
    'pho': [('00001930', 'physical_entity.03.0')],
    'plt': [('00017402', 'plant.03.0 flora.03.0 plant_life.03.0')],
    'pos': [('00032912', 'possession.03.0')],
    'pro': [('00029976', 'process.03.0 physical_process.03.0')],
    'prt': [('09408804', 'part.17.0 piece.17.0')],
    'psy': [('00023280', 'psychological_feature.03.0')],
    'qud': [('13597304', 'definite_quantity.23.0')],
    'qui': [('13597558', 'indefinite_quantity.23.0')],
    'rel': [('00032220', 'relation.03.0')],
    'spc': [('00028950', 'space.03.0 infinite.03.0')],
    'sta': [('00024900', 'state.03.0')],
    'sub': [('00021007', 'matter.03.0')],
    'tme': [('15137796', 'time_period.28.0 period_of_time.28.0 period.28.0'), # amount_of_time is gone
            ('15179734', 'time_unit.28.0 unit_of_time.28.0'),
            ('00028468', 'time.03.0')]
}


BASIC_TYPES_ISA_RELATIONS_1_5 = [

    # entity
    ('prt', 'ent'), ('cel', 'ent'), ('agt', 'ent'),
    ('lfr', 'ent'), ('mic', 'ent'), ('hum', 'ent'), ('anm', 'ent'), ('plt', 'ent'),
    ('mic', 'lfr'), ('hum', 'lfr'), ('anm', 'lfr'), ('plt', 'lfr'),
    ('pho', 'ent'), ('art', 'ent'), ('nat', 'ent'),
    ('art', 'pho'), ('nat', 'pho'),
    ('sub', 'ent'), ('fod', 'ent'), ('chm', 'ent'),
    ('fod', 'sub'), ('chm', 'sub'),

    # abstraction
    ('spc', 'abs'), ('tme', 'abs'), ('atr', 'abs'),
    ('mea', 'abs'), ('lme', 'abs'), ('tme', 'abs'), ('qud', 'abs'), ('qui', 'abs'),
    ('lme', 'mea'), ('tme', 'mea'), ('qud', 'mea'), ('qui', 'mea'),
    ('rel', 'abs'), ('com', 'abs'),
    ('com', 'rel'),
    
    ('grb', 'grp'), ('grs', 'grp'),
    ('con', 'phm'), ('pro', 'phm'),
    ('log', 'loc'),

]


BASIC_TYPES_ISA_RELATIONS_3_1 = [

    ('abs', 'ent'),
    ('act', 'abs'), ('act', 'ent'), ('act', 'evt'), ('act', 'psy'),
    ('agt', 'ent'), ('agt', 'pho'),
    ('anm', 'ent'), ('anm', 'lfr'), ('anm', 'pho'),
    ('art', 'ent'), ('art', 'pho'), ('atr', 'abs'),
    ('atr', 'ent'),
    ('cel', 'ent'), ('cel', 'lfr'), ('cel', 'pho'),
    ('chm', 'abs'), ('chm', 'ent'), ('chm', 'pho'), ('chm', 'rel'), ('chm', 'sub'),
    ('com', 'abs'), ('com', 'ent'),
    ('con', 'ent'), ('con', 'phm'), ('con', 'pho'), ('con', 'pro'),
    ('evt', 'abs'), ('evt', 'ent'), ('evt', 'psy'),
    ('fod', 'ent'), ('fod', 'pho'), ('fod', 'sub'),
    ('frm', 'abs'), ('frm', 'atr'), ('frm', 'ent'),
    ('grb', 'abs'), ('grb', 'ent'), ('grb', 'grp'),
    ('grp', 'abs'), ('grp', 'ent'),
    ('grs', 'abs'), ('grs', 'ent'), ('grs', 'grp'),
    ('hum', 'agt'), ('hum', 'ent'), ('hum', 'lfr'), ('hum', 'pho'),
    ('lfr', 'ent'), ('lfr', 'pho'),
    ('lme', 'abs'), ('lme', 'ent'), ('lme', 'mea'), ('lme', 'qud'),
    ('loc', 'ent'), ('loc', 'pho'),
    ('log', 'ent'), ('log', 'loc'), ('log', 'pho'),
    ('mea', 'abs'), ('mea', 'ent'),
    ('mic', 'ent'), ('mic', 'lfr'), ('mic', 'pho'),
    ('nat', 'ent'), ('nat', 'pho'),
    ('phm', 'ent'), ('phm', 'pho'), ('phm', 'pro'),
    ('pho', 'ent'),
    ('plt', 'ent'), ('plt', 'lfr'), ('plt', 'pho'),
    ('pos', 'abs'), ('pos', 'ent'), ('pos', 'rel'),
    ('pro', 'ent'), ('pro', 'pho'),
    ('prt', 'ent'), ('prt', 'pho'),
    ('psy', 'abs'), ('psy', 'ent'),
    ('qud', 'abs'), ('qud', 'ent'), ('qud', 'mea'),
    ('qui', 'abs'), ('qui', 'ent'), ('qui', 'mea'),
    ('rel', 'abs'), ('rel', 'ent'),
    ('spc', 'abs'), ('spc', 'atr'), ('spc', 'ent'),
    ('sta', 'abs'), ('sta', 'atr'), ('sta', 'ent'),
    ('sub', 'ent'), ('sub', 'pho'),
    ('tme', 'abs'), ('tme', 'atr'), ('tme', 'ent'), ('tme', 'mea')
]


CORELEX_TYPES = {

    'abs': ['abs'],
    'acp': ['act atr pro', 'act atr pro sta', 'act pro', 'act pro psy',
            'act pro psy sta', 'act pro sta', 'pro psy', 'pro sta'],
    'acr': ['act atr rel', 'act evt rel', 'act rel', 'act rel sta'],
    'acs': ['act sta'],
    'act': ['act'],
    'aes': ['act evt sta'],
    'aev': ['act evt'],
    'age': ['act agt'],
    'agh': ['agt hum'],
    'agl': ['agt loc'],
    'agm': ['agt anm'],
    'agp': ['agt psy'],
    'agt': ['agt'],
    'anf': ['anm fod'],
    'anm': ['anm'],
    'ann': ['anm art nat', 'anm nat'],
    'anp': ['anm psy'],
    'aqu': ['art qud', 'art qui'],
    'ara': ['act art atr psy', 'art atr', 'art atr psy', 'art atr sta'],
    'arg': ['art grp'],
    'arh': ['art hum'],
    'arp': ['art psy', 'art psy sta'],
    'art': ['art', 'art sta'],
    'atc': ['atr com', 'atr com phm psy', 'atr com psy', 'atr com psy sta',
            'atr com sta'],
    'ate': ['act atr', 'act atr evt', 'act atr evt sta', 'act atr sta', 'atr evt',
            'atr evt psy', 'atr evt sta'],
    'atg': ['atr grp'],
    'atl': ['atr loc', 'atr loc psy', 'atr loc psy sta', 'atr loc sta'],
    'atp': ['atr psy', 'atr psy sta'],
    'atr': ['atr', 'atr pro', 'atr pro sta', 'atr sta'],
    'avf': ['act art frm'],
    'avl': ['act art loc', 'act art log'],
    'avr': ['act art evt rel', 'art rel'],
    'avt': ['act art', 'act art atr', 'act art evt', 'act art pro', 'act art sta',
            'act atr pho', 'art evt', 'art evt sta', 'art pro'],
    'caa': ['art atr com'],
    'cae': ['act art com', 'act art com psy', 'act art psy', 'act art psy sta',
            'art com', 'art com psy', 'art com psy sta'],
    'cea': ['act atr com', 'act atr com evt', 'act atr com psy', 'act atr com psy sta',
            'act atr evt psy', 'act atr psy', 'act atr psy sta'],
    'cel': ['cel'],
    'cha': ['art chm', 'art chm sub'],
    'chf': ['chm fod'],
    'chm': ['chm', 'chm sta'],
    'chp': ['chm plt'],
    'coa': ['act com', 'act com evt', 'act com evt', 'act com evt psy',
            'act com pro', 'act com psy', 'act com psy sta', 'act com rel',
            'act com sta', 'com evt', 'com pro'],
    'coh': ['com hum'],
    'col': ['com log'],
    'com': ['com', 'com psy', 'com psy sta', 'com rel', 'com sta'],
    'con': ['act con evt', 'con evt', 'con'],
    'ent': ['ent'],
    'evs': ['evt pro', 'evt pro sta', 'evt sta'],
    'evt': ['evt'],
    'fac': ['act art fod', 'act fod'],
    'fev': ['fod grs'],
    'fod': ['atr fod', 'fod', 'fod frm', 'fod nat', 'fod qui', 'fod sta', 'fod sub'],
    'frc': ['com frm', 'frm psy'],
    'fre': ['act evt frm', 'act frm', 'act frm sta'],
    'frm': ['atr frm', 'atr frm sta', 'frm', 'frm sta'],
    'frt': ['art atr frm', 'art frm', 'art frm loc', 'art frm nat', 'art frm sta'],
    'ftp': ['atr fod plt', 'atr fod plt sub'],
    'gas': ['act grs', 'act com grs', 'act evt grs', 'act grs psy', 'act grs sta'],
    'gbp': ['grb psy'],
    'gbs': ['grb grs'],
    'grb': ['grb'],
    'grp': ['grp'],
    'grq': ['grs qud'],
    'grs': ['grp grs', 'grs', 'grs sta'],
    'gsa': ['act art com grs', 'act art grs', 'act atr grs', 'act grp',
            'art grs', 'art grs sub'],
    'gsl': ['grs log'],
    'gsp': ['grs psy', 'grs psy sta'],
    'hue': ['act evt hum sta', 'act hum', 'evt hum', 'hum sta'],
    'hum': ['grp hum', 'grp hum nat', 'grs hum', 'hum'],
    'hup': ['hum psy'],
    'lac': ['act loc', 'act log'],
    'lap': ['art loc', 'art loc psy', 'art loc sta', 'com loc', 'com loc psy',
            'loc psy', 'loc sta'],
    'lfr': ['lfr'],
    'lgg': ['grp log'],
    'lme': ['lme', 'lme qud'],
    'loc': ['art log sta', 'loc', 'log pos sta', 'log sta'],
    'log': ['art log', 'log', 'log nat'],
    'lon': ['loc nat'],
    'lor': ['log rel'],
    'mea': ['mea'],
    'mic': ['mic'],
    'naa': ['art nat'],
    'nac': ['act art nat', 'art evt nat'],
    'naf': ['frm nat'],
    'naq': ['nat qui'],
    'nat': ['nat', 'nat sub'],
    'pan': ['art nat plt', 'art plt', 'art plt sub', 'plt sub'],
    'pap': ['act atr pos psy'],
    'pas': ['act atr pos', 'atr pos', 'atr pos rel', 'atr pos sta'],
    'pgb': ['grb plt'],
    'phm': ['act evt phm', 'act evt phm sta', 'act phm', 'act phm sta', 'evt phm',
            'phm', 'phm pro', 'phm rel', 'phm sta'],
    'pho': ['pho'],
    'php': ['evt phm psy', 'phm psy'],
    'phs': ['phm sub'],
    'pht': ['atr phm'],
    'plf': ['fod plt'],
    'plt': ['fod nat plt', 'nat plt', 'nat plt sub', 'plt'],
    'poa': ['act com evt pos', 'act evt pos', 'act pos', 'act pos psy',
            'act pos psy sta', 'evt pos'],
    'pom': ['com pos', 'act com pos', 'art com pos', 'atr com pos'],
    'poq': ['pos qud'],
    'pos': ['pos', 'pos pro', 'pos psy', 'pos sta'],
    'prn': ['nat pro'],
    'pro': ['pro'],
    'prt': ['art fod prt', 'art frm prt', 'art prt', 'atr prt', 'atr prt sub',
            'fod prt', 'frm prt',
            'hum prt', 'nat prt', 'prt', 'prt qui', 'prt sta'],
    'psa': ['act art pos', 'art pos'],
    'psg': ['act grp psy', 'grp psy'],
    'psr': ['pos rel'],
    'psy': ['evt psy', 'evt psy sta', 'psy', 'psy sta'],
    'pya': ['act evt psy', 'act evt psy sta', 'act psy', 'act psy rel',
            'act psy sta'],
    'qcc': ['qud sta'],
    'qcs': ['com qud sta'],
    'qde': ['act qud'],
    'qie': ['act evt qui', 'act qui'],
    'qud': ['qud'],
    'qui': ['qui'],
    'reg': ['grp rel'],
    'rel': ['atr rel', 'atr psy rel', 'hum rel', 'psy rel', 'rel', 'rel sta'],
    'saa': ['art sub', 'art atr sub', 'atr sub'],
    'sas': ['act sta sub', 'act sub', 'sta sub'],
    'spc': ['spc'],
    'spe': ['act spc'],
    'sta': ['sta'],
    'sub': ['sub'],
    'tme': ['sta tme', 'grp tme', 'phm tme', 'qud tme', 'tme'],
    'tmt': ['atr tme'],
    'tmv': ['act evt tme', 'act tme', 'evt tme']

}


def create_corelex_types_mapping():
    mapping = {}
    source_file = '../legacy/data/corelex_nouns.classes.txt'
    for line in open(source_file):
        line = line.strip()
        if line.startswith('#') or not line:
            continue
        cltype, ptype = line.split("   ")
        mapping.setdefault(cltype, []).append(ptype)
    for cltype in sorted(mapping):
        print("    '%s': %s," % (cltype, mapping[cltype]))


def get_basic_types(version):
    if version == '1.5':
        return BASIC_TYPES_1_5
    elif version == '3.1':
        return BASIC_TYPES_3_1
    else:
        print("WARNING: no basic types available for version", version)
        exit()


def get_type_relations(version):
    if version == '1.5':
        return BASIC_TYPES_ISA_RELATIONS_1_5
    elif version == '3.1':
        return BASIC_TYPES_ISA_RELATIONS_3_1
    else:
        print("WARNING: no type relations available for version", version)
        exit()


def pp_basic_types(version):
    btypes = get_basic_types(version)
    for btype in sorted(btypes):
        for ss in btypes[btype]:
            print("%s\t%s\t%s" % (btype, ss[0], ss[1]))


if __name__ == '__main__':

    #create_corelex_types_mapping()
    pp_basic_types('3.1')
