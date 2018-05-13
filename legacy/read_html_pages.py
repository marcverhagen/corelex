"""Printing a table of all nouns with their types, using three colomns.

Example lines:

tmv	act evt tme	ascension
tmv	act evt tme	interruption

This is assuming that the polysemous types (column two) are unique. But note
that in the database there are 318 rows in corelex_types, but the following
query returns 317 rows:

SELECT DISTINCT `basic_types` FROM `corelex_types` WHERE 1

Turns out there was a duplicate polysemous type in 'act com evt' both with the
same corelex type. Rewrote the code for generating the table to filter it out.

"""


import os, glob

WWW_DIR = 'data/CoreLex'

NAME_PREFIX = ' <DT> <A NAME='
NOUN_LIST_PREFIX = '<DT> '

def process_instance_file(fname):
    corelex_type = os.path.basename(fname)[:3]
    #print '\n', corelex_type, fname
    polysemous_type = None
    for line in open(fname):
        if line.startswith(NAME_PREFIX):
            polysemous_type = line[len(NAME_PREFIX)+2:-6]
            #print polysemous_type
        elif line.startswith(NOUN_LIST_PREFIX):
            nouns = line[len(NOUN_LIST_PREFIX):-7]
            nouns = nouns.strip().split()
            for noun in nouns:
                print "%s\t%s\t%s" % (corelex_type, polysemous_type, noun)
            

instance_files = glob.glob(os.path.join(WWW_DIR, '*.instance.html'))
for fname in instance_files:
    process_instance_file(fname)

                           
