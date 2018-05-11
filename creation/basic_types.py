"""Contains the synsets from WordNet that are used as basic types for CoreLex.

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

For all basic types, the mapping to synsets was changed. In most cases (TO BE
DETERMINED), the mapping was to the same synset but the synset identifier (which
is the byte offset in the WordNet data) file had to be updated.

Strategy:
- do this on a case by case basis, looking at each top level type
- for each basic type, find the synset in WN3.1
   - use the number from the lexicographer file
   - for example, the frm basic type in WN1.5 maps to the {shape.03.0 form.03.0} synset
   - try to find the same one in WN3.1
- check the definition and the subtypes
   - if they are similar, just update the identifier
   - typically, in WN3.1 the synset(s) will have more hyponyms
   - if not similar, check for alternatives
   - if definition does not exist anymore (eg process.22.0):
      - find closest based on subtypes

From WordNet 1.5 to WordNet 3.1 the noun hierarchy has changed. For example,
there is no a set of 11 toptypes anymore, instead there is only one toptype in
entity.03.0. Almost all basic types from 1.5 were also in 3.1 but there were few
types that pointed to synsets that were split up and even one that did not exist
any more (process.22.0). In many case the synset was at a different position in
the hierarchy.

== subsumption among basic types

Some basic types are subtypes of each other, for example 'prt' is a subtype of
'ent'. If a noun falls under two basic types that stand in an ISA relation than
only the most specific one will be taken. In the pairs as listed in
BASIC_TYPES_ISA_RELATIONS_1_5 and BASIC_TYPES_ISA_RELATIONS_3_1, the first type
is more specific than the second.

The pairs for 1.5 were created manually from the hierarchy pictures in Paul
Buitelaar's dissertations. The ones for 3.1 were created by a utility method in
the wordnet module: WordNet.display_basic_type_relations().

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

    'abs': [('00002137', 'abstraction')],                      # new: psy; gone: time.03.0 space.03.0 
    'act': [('00030657', 'act human_action human_activity')],  # similar, but many more subtypes
    'agt': [('00007347', 'causal_agent.03.0 cause.03.0 causal_agency.03.0')],
    'anm': [('00015568', 'animal.03.0 animate_being.03.0 beast.03.0 brute.03.0 creature.03.0 fauna.03.0')],
    'art': [('00022119', 'artifact artefact')],                # deeper embedded
    'atr': [('00024444', 'attribute')],                        # many new subs: sta, spc, tme, frm 
    'cel': [('00006484', 'cell.03.0')],
    'chm': [('14842408', 'compound chemical_compound'),        # deeper embedded
            ('14647071', 'chemical_element element')],   
    'com': [('00033319', 'communication')],                    # is now directly under abstraction
    'con': [('11430739', 'consequence effect outcome result upshot')],
    'ent': [('00001740', 'entity')],                           # is now the single top type
    'evt': [('00029677', 'event')],                            # similar, but now includes act.03.0
    'fod': [('00021445', 'food nutrient')],
    'frm': [('00028005', 'shape form')],
    'grb': [('07957410', 'biological_group')],
    'grp': [('00031563', 'group grouping')],
    'grs': [('07967506', 'social_group'),
            ('07958392', 'people')],
    'hum': [('00007846', 'person.03.0 individual.03.0 someone.03.0 somebody.03.0 mortal.03.0 soul.03.0')],
    'lfr': [('00004258', 'living_thing.03.0 animate_thing.03.0')],
       # used to be 'life_form organism being living_thing'
       # life_form was split off and made its own synset under {body.08.0, organic_structure.08.0}
       # organism.03.0 being.03.0 are now under living_thing.03.0
    'lme': [('13624548', 'linear_unit linear__measure')],
       # lme used to be 'linear_measure long_measure', long_measure is a hyponym
       # lme is now deeper in the hierarchy 
    'loc': [('00027365', 'location')],                         # similar, but imaginary_place was moved to psy
    'log': [('08648560', 'region')],                           # similar
    'mea': [('00033914', 'measure quantity amount quantum')],  # last member is gone
    'mic': [('01328932', 'microorganism.05.0 micro-organism.05.0')], # expanded synset
    'nat': [('00019308', 'natural_object'),
            ('09248053', 'body_of_water water'),
            ('09357302', 'land dry_land earth ground solid_ground terra_firma')],
    'phm': [('00034512', 'phenomenon')],                       # similar, but issue with pro subtype
    'pho': [('00001930', 'physical_entity.03.0')],
       # this is a new synset, the old 'object inanimate_object physical_object' is a hyponym
    'plt': [('00017402', 'plant.03.0 flora.03.0 plant_life.03.0')],
    'pos': [('00032912', 'possession')],
       # similar, but subtype ownership.21.0 is moved up to relation.03.0
    'pro': [('00029976', 'process')],
       # process.22.0 does not exist anymore, process.03.0 seems closest
    'prt': [('09408804', 'part.17.0 piece.17.0')],
    'psy': [('00023280', 'psychological_feature')],
    'qud': [('13597304', 'definite_quantity')],
    'qui': [('13597558', 'indefinite_quantity')],
    'rel': [('00032220', 'relation')],  
    'spc': [('00028950', 'space')],                                           # very different now
    'sta': [('00024900', 'state')],                                           # similar, but many more subtypes
    'sub': [('00021007', 'matter.03.0')],
       # used to be 'substance matter', but substance.03.0 is now a subtype
    'tme': [('15137796', 'time_period period period_of_time amount_of_time'), # last member is gone
            ('15179734', 'time_unit unit_of_time'),
            ('00028468', 'time')]
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

