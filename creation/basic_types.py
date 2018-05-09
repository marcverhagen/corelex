"""

Contains the synsets from WordNet that are used as basic types for CoreLex.

"""


# These are the basic types from WordNet 1.5, taken from the original CoreLex as
# listed at
#
#    http://batcaves.org/corelex/browser/view_basic_types.php

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
    'grs': [('05119847', 'social_group'), ('05116476', 'people')],
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

#    'abs': [('-00012670', 'abstraction')],
    'act': [('00030657', 'act human_action human_activity')],
#    'agt': [('-00004473', 'causal_agent cause causal_agency')],
#    'anm': [('-00008030', 'animal animate_being beast brute creature fauna')],
#    'art': [('-00011607', 'artifact artefact')],
#    'atr': [('-00017586', 'attribute')],
    'cel': [('00006484', 'cell')],
    'chm': [('14842408', 'compound chemical_compound'),
            ('14647071', 'chemical_element element')],
#    'com': [('-00018599', 'communication')],
#    'con': [('-06465491', 'consequence effect outcome result upshot')],
    'ent': [('00001930', 'physical_entity')],  # takes the place of entity
#    'evt': [('-00016459', 'event')],
    'fod': [('00021445', 'food nutrient')],
#    'frm': [('-00014558', 'shape form')],
#    'grb': [('-05115837', 'biological_group')],
#    'grp': [('-00017008', 'group grouping')],
#    'grs': [('-05119847', 'social_group'), ('05116476', 'people')],
#    'hum': [('-00004865', 'person individual someone mortal human soul')],
#    'lfr': [('-00002728', 'life_form organism being living_thing')],
#    'lme': [('-08322690', 'linear_measure long_measure')],
#    'loc': [('-00014314', 'location')],
#    'log': [('-05450515', 'region')],
#    'mea': [('-00018966', 'measure quantity amount quantum')],
#    'mic': [('-00740781', 'microorganism')],
#    'nat': [('-00009919', 'natural_object'),
#            ('-05715416', 'body_of_water water'),
#            ('-05720524', 'land dry_land earth ground solid_ground terra_firma')],
#    'phm': [('-00019295', 'phenomenon')],
#    'pho': [('-00009469', 'object inanimate_object physical_object')],
#    'plt': [('-00008894', 'plant flora plant_life')],
#    'pos': [('-00017394', 'possession')],
#    'pro': [('-08239006', 'process')],
#    'prt': [('-05650477', 'part piece')],
#    'psy': [('-00012517', 'psychological_feature')],
#    'qud': [('-08310215', 'definite_quantity')],
#    'qui': [('-08310433', 'indefinite_quantity')],
#    'rel': [('-00017862', 'relation')],
#    'spc': [('-00015245', 'space')],
    'sta': [('00024900', 'state')],
#    'sub': [('-00010368', 'substance matter')],
#    'tme': [('-09065837', 'time_period period period_of_time amount_of_time'),
#            ('-09092294', 'time_unit unit_of_time'),
#            ('-00014882', 'time')]
}


# Some basic types are subtypes of each other, for example 'prt' is a subtype of
# 'ent'. If a noun falls under two basic types that stand in an ISA relation
# than only the most specific one will be taken. In the pairs below, the first
# type is more specific than the second.

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

    ('sta', 'ent')
]

