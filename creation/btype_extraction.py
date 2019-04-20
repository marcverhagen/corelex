from functools import reduce
import wordnet


SEMCOR_TYPES = '../../semcor/code/semcor-types.tab'


def load_lemmas():
    lemmas = []
    for line in open(SEMCOR_TYPES):
        lemmas.append(line.strip().split('\t'))
    print('Loaded', len(lemmas), 'lemmas from Semcor')
    return lemmas


def load_wordnet():
    wn = wordnet.WordNet('3.1')
    wn.add_basic_types()
    print('Loaded', wn)
    return wn


def run(wn, lemmas):
    correct = 0
    incorrect = 0
    noun_not_found = 0
    synset_not_found = 0
    number_of_nouns_with_one_synset = 0
    number_of_nouns_with_one_btype = 0
    for lemma, synset_id, btypes in lemmas[:10000000]:
        noun = wn.get_noun(lemma)
        #print("%s\t%s\t%s" % (lemma, synset_id, noun.synsets[0]))
        if noun is None:
            noun_not_found += 1
            incorrect += 1
            continue
        if synset_id is None:
            synset_not_found += 1
            continue
        if len(noun.synsets) == 1:
            number_of_nouns_with_one_synset += 1
        if len(get_basic_types(wn, noun.lemma)) == 1:
            number_of_nouns_with_one_btype += 1
        if synset_id == noun.synsets[0]:
            correct += 1
        else:
            incorrect += 1
    print('\nRunning baseline system...')
    print('\n   noun_not_found    ', noun_not_found)
    print('   synset_not_found  ', synset_not_found)
    print('   singleton synsets ', format(number_of_nouns_with_one_synset, ',d'))
    print('   singleton btypes  ', format(number_of_nouns_with_one_btype, ',d'))
    print('\n   correct:   %s' % format(correct, ',d'))
    print('   incorrect: %s' % format(incorrect, ',d'))
    accuracy = correct/(correct+incorrect)
    print('\n   accuracy = %.2f\n' % accuracy)


def _create_lemma_index(wn, lemmas):
    lemma_idx = {}
    # collect all information from the lemma list
    for lemma, synset, basic_type in lemmas:
        lemma_idx.setdefault(lemma, {'count': 0, 'wnsynsets': [],
                                     'synsets': set(), 'basic_types': set()})
        lemma_idx[lemma]['count'] += 1
        lemma_idx[lemma]['synsets'].add(synset)
        lemma_idx[lemma]['basic_types'].add(basic_type)
    # remove occurrences of 'None' and add WN synsets
    for lemma in lemma_idx:
        noun = wn.get_noun(lemma)
        if noun is not None:
            lemma_idx[lemma]['wnsynsets'] = noun.synsets
        lemma_idx[lemma]['synsets'].discard('None')
        lemma_idx[lemma]['basic_types'].discard('None')
    return lemma_idx


def _write_lemma_index(lemma_idx):
    fh = open('tmp.stats.tab', 'w')
    for lemma in lemma_idx:
        #print(lemma, lemma_idx[lemma])
        fh.write("%s\t%s\t%s\t%s\n" % (
            lemma,
            lemma_idx[lemma]['wnsynsets'],
            lemma_idx[lemma]['synsets'],
            lemma_idx[lemma]['basic_types']))

def stats(wn, lemmas):
    lemma_idx = _create_lemma_index(wn, lemmas)
    _write_lemma_index(lemma_idx)
    counts = {}
    for lemma in lemma_idx:
        count = (len(lemma_idx[lemma]['wnsynsets']),
                 len(lemma_idx[lemma]['synsets']),
                 lemma_idx[lemma]['count'])
        counts[count] = counts.get(count, 0) + 1
    all_synsets_in_semcor_tokens = 0
    not_all_synsets_in_semcor_tokens = 0
    all_synsets_in_semcor_types = 0
    not_all_synsets_in_semcor_types = 0
    for (c1, c2, multiplier), val in sorted(counts.items()):
        if c1 == c2:
            all_synsets_in_semcor_types += val 
            all_synsets_in_semcor_tokens += val * multiplier
        else:
            not_all_synsets_in_semcor_types += val
            not_all_synsets_in_semcor_tokens += val * multiplier
        #print(c1, c2, val)
    print('\nStatistics')
    print('\n   types:')
    total = all_synsets_in_semcor_types + not_all_synsets_in_semcor_types
    print('      all_synsets_in_semcor     ', all_synsets_in_semcor_types)
    print('      not_all_synsets_in_semcor ', not_all_synsets_in_semcor_types)
    print("      ratio of known synsets:    %.2f" % (all_synsets_in_semcor_types / total))
    print('\n   tokens:')
    total = all_synsets_in_semcor_tokens + not_all_synsets_in_semcor_tokens
    print('      all_synsets_in_semcor     ', all_synsets_in_semcor_tokens)
    print('      not_all_synsets_in_semcor ', not_all_synsets_in_semcor_tokens)
    print("      ratio of known synsets:    %.2f" % (all_synsets_in_semcor_tokens / total))


def union(x1, x2):
    return x1.union(x2)


def get_basic_types(wn, noun):
    synsets = wn.get_noun(noun).synsets
    sets = [wn.get_synset('noun', ss).basic_types for ss in synsets]
    return reduce(union, sets)


if __name__ == '__main__':

    wn = load_wordnet()
    lemmas = load_lemmas()
    stats(wn, lemmas)
    run(wn, lemmas)
