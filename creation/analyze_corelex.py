corelex_file = 'bak/corelex.tab'
corelex_file = 'corelex.tab'

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
