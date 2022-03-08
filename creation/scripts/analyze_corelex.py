"""

Script to analyze Corelex. Doesn't do a lot and is probably obsolete now.

"""

corelex_file = '../data/corelex-2.0-types-nouns.tab'

type_count = 0
polysemous_type_count = 0
filtered_polysemous_type_count = 0

for line in open(corelex_file):
    ptype, words = line.strip().split("\t")
    word_count = len(words.split())
    type_count += 1    
    if len(ptype.split()) > 1:
        polysemous_type_count += 1
        if word_count > 1:
            filtered_polysemous_type_count += 1

print(type_count)
print(polysemous_type_count)
print(filtered_polysemous_type_count)
