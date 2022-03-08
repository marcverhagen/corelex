"""

Script to print number of synsets and pointers in wordnet.

"""

INDEX_FILE = '/Users/Shared/data/resources/lexicons/wordnet/WordNet-3.1/dict/index.noun'
DATA_FILE = '/Users/Shared/data/resources/lexicons/wordnet/WordNet-3.1/dict/data.noun'


lengths = {}
categories = {}
synsets = {}
pointers = {}

c = 0
for line in open(INDEX_FILE):
    c += 1
    #if c > 100: break
    if line.startswith('  '):
        continue
    fields = line.strip().split()
    synset_cnt = int(fields[2])
    p_cnt = int(fields[3])
    if p_cnt == 0:
        print('p_cnt is 0 ', line)
    synsets[synset_cnt] = synsets.get(synset_cnt, 0) + 1
    pointers[p_cnt] = pointers.get(p_cnt, 0) + 1
    
print('SYNSETS', synsets)
print('POINTERS', pointers)
