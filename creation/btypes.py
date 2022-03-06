"""btypes.py

Contains a class to manage basic types and a baseline basic type extraction algorithm.

== BasicTypes

With the BasicTypes class you can
- remove a type
- add a type
- replace a type and build a new one from all hypernyms of the synsets of the type
- replace a type and build a new one from all hyponyms of the synsets of the type
- save new types to a file

Load with the default WordNet version and print a list of basic types

    >>> btm = BasicTypes()
    >>> print(btm)
    <BasicTypes with 37 types>

Remove the articaft type

    >>> btm.remove_type('art')

And put it back in again

    >>> btm.add_type('art',  [('00022119', 'artifact.03.0 artefact.03.0')])

Replace the spc type with its supertypes

    >>> btm.replace_type_with_supertype('spc')

And the replace that one with all daughters of that supertype

    >>> btm.replace_type_with_subtypes('spc.sup')

Write new basic types to disk

    >>> btm.write('new_basic_types.py')


== Basic type extraction

$ python3 btypes.py --extract

This runs a simple baseline basic type algorithm based on using the most likely
Wordnet synset.

This requires a file named semcor-types.tab which should live in <semcor>/code,
where <semcor> is the code from https://github.com/marcverhagen/semcor which is
assumed to have been cloned at the same level as the corelex code. This file has
a list of all tokens that were annotated, listing the lemma, wordnet synset and
basic type.

See <semcor>/code/semcor.py on how to create semcor-types.tab, basically you run

$  python3 semcor.py --export-nouns semcor-types.tab

If you decide to create a file with a different name or clone the semcor
reporitory in another location you may do so, but you should update the
SEMCOR_TYPES variable in the configuration.

This code also loads Wordnet.


"""

import sys
import pprint
from functools import reduce

import wordnet
import cltypes
from config import SEMCOR_TYPES


class BasicTypes(object):

    def __init__(self, types=None, wn=None):
        """Types and WordNet instance can be handed in, if not defaults will be used."""
        self.types = cltypes.BASIC_TYPES_3_1 if types is None else types
        self.types = self.types.copy()
        self.wn = wordnet.WordNet('3.1') if wn is None else wn

    def __str__(self):
        return "<BasicTypes with %s types>" % len(self.types)

    def print_types(self, verbose=True):
        """Pretty print types to the terminal."""
        for t in self.types:
            if verbose:
                print(t, self.types[t])
            else:
                print(t, end=' ')
        print()

    def remove_type(self, typename):
        """Remove basic type if it exists."""
        if typename in self.types:
            del(self.types[typename])

    def add_type(self, typename, synsets):
        self.types[typename] = synsets

    def replace_type_with_supertype(self, typename):
        new_typename = typename + '.sup'
        new_synsets = []
        for synset_id, synset_description in self.types[typename]:
            ss = self.wn.get_synset('noun', synset_id)
            hypernyms = ss.hypernyms()
            new_synsets.extend([(h.id, h.words_as_string()) for h in hypernyms])
        self.remove_type(typename)
        self.add_type(new_typename, new_synsets)

    def replace_type_with_subtypes(self, typename):
        new_typename = typename + '.sub'
        new_synsets = []
        for synset_id, synset_description in self.types[typename]:
            ss = self.wn.get_synset('noun', synset_id)
            hyponyms = ss.hyponyms()
            new_synsets.extend([(h.id, h.words_as_string()) for h in hyponyms])
        self.remove_type(typename)
        self.add_type(new_typename, new_synsets)

    def write(self, fname):
        with open(fname, 'w') as fh:
            pp = pprint.PrettyPrinter(stream=fh, indent=4)
            pp.pprint(self.types)


## Code for running the baseline extraction algorithm.

def load_lemmas():
    lemmas = []
    for line in open(SEMCOR_TYPES):
        lemmas.append(line.strip().split('\t'))
    print('Loaded', len(lemmas), 'lemmas from Semcor')
    return lemmas

def load_wordnet():
    wn = wordnet.WordNet('3.1', add_basic_types=True)
    print('Loaded', wn)
    return wn


class Statistics(object):

    """Statistics while running the baseline algorithm."""

    def __init__(self):
        self.correct = 0
        self.incorrect = 0
        self.noun_not_found = 0
        self.synset_not_found = 0
        self.number_of_nouns_with_one_synset = 0
        self.number_of_nouns_with_one_btype = 0

    def accuracy(self):
        return self.correct / (self.correct + self.incorrect)


class BaseLineAlgorithm(object):

    def __init__(self, wn, lemmas):
        self.wn = wn
        self.lemmas = lemmas

    def run(self):
        self.stats = Statistics()
        for lemma, synset_id, btypes in self.lemmas[:10000000]:
            noun = self.wn.get_noun(lemma)
            if noun is None:
                self.stats.noun_not_found += 1
                self.stats.incorrect += 1
                continue
            if synset_id is None:
                self.stats.synset_not_found += 1
                continue
            if len(noun.synsets) == 1:
                self.stats.number_of_nouns_with_one_synset += 1
            if len(self.wn.get_basic_types_for_noun(noun.lemma)) == 1:
                self.stats.number_of_nouns_with_one_btype += 1
            if synset_id == noun.synsets[0]:
                self.stats.correct += 1
            else:
                self.stats.incorrect += 1

    def print_results(self):
        print('\nBaseline system results:')
        print('\n   noun_not_found    ', self.stats.noun_not_found)
        print('   synset_not_found  ', self.stats.synset_not_found)
        print('   singleton synsets ', format(self.stats.number_of_nouns_with_one_synset, ',d'))
        print('   singleton btypes  ', format(self.stats.number_of_nouns_with_one_btype, ',d'))
        print('\n   correct:   %s' % format(self.stats.correct, ',d'))
        print('   incorrect: %s' % format(self.stats.incorrect, ',d'))
        accuracy = self.stats.accuracy()#correct/(self.stats.correct+self.stats.incorrect)
        print('\n   accuracy = %.2f\n' % accuracy)


class LemmaIndex(object):

    """Keep track of information about lemmas in SemCor, including total count, all
    synsets it was tagged with and all basic types. It also includes all synsets
    associated with the lemma in WordNet."""

    def __init__(self, wn, lemmas):
        self.idx = {}
        # collect all information from the lemma list
        for lemma, synset, basic_type in lemmas:
            self.idx.setdefault(lemma, {'count': 0, 'wnsynsets': [],
                                         'synsets': set(), 'basic_types': set()})
            self.idx[lemma]['count'] += 1
            self.idx[lemma]['synsets'].add(synset)
            self.idx[lemma]['basic_types'].add(basic_type)
        # remove occurrences of 'None' and add WN synsets
        for lemma in self.idx:
            noun = wn.get_noun(lemma)
            if noun is not None:
                self.idx[lemma]['wnsynsets'] = noun.synsets
            self.idx[lemma]['synsets'].discard('None')
            self.idx[lemma]['basic_types'].discard('None')

    def __iter__(self):
        return self.idx.__iter__()

    def __getitem__(self, i):
        return self.idx[i]

    def write(self):
        fh = open('tmp.stats.tab', 'w')
        for lemma in self.idx:
            fh.write("%s\t%s\t%s\t%s\n" % (
                lemma,
                self.idx[lemma]['wnsynsets'],
                self.idx[lemma]['synsets'],
                self.idx[lemma]['basic_types']))


class SemcorCoverageStatistics(object):

    """Collect some statistics on coverage of Semcor relative to Wordnet."""

    def __init__(self, wn, lemmas):
        self.lemma_idx = LemmaIndex(wn, lemmas)
        #self.lemma_idx.write()
        self.all_synsets_in_semcor_tokens = 0
        self.not_all_synsets_in_semcor_tokens = 0
        self.all_synsets_in_semcor_types = 0
        self.not_all_synsets_in_semcor_types = 0
        for lemma in self.lemma_idx:
            wnsynsets = len(self.lemma_idx[lemma]['wnsynsets'])
            synsets = len(self.lemma_idx[lemma]['synsets'])
            count = self.lemma_idx[lemma]['count']
            if wnsynsets == synsets:
                self.all_synsets_in_semcor_types += 1
                self.all_synsets_in_semcor_tokens += count
            else:
                self.not_all_synsets_in_semcor_types += 1
                self.not_all_synsets_in_semcor_tokens += count

    def write(self):
        print('\nSemcor coverage statistics')
        print('\n   types:')
        total = self.all_synsets_in_semcor_types + self.not_all_synsets_in_semcor_types
        print('      all_synsets_in_semcor     ', self.all_synsets_in_semcor_types)
        print('      not_all_synsets_in_semcor ', self.not_all_synsets_in_semcor_types)
        print("      ratio of known synsets:    %.2f" % (self.all_synsets_in_semcor_types / total))
        print('\n   tokens:')
        total = self.all_synsets_in_semcor_tokens + self.not_all_synsets_in_semcor_tokens
        print('      all_synsets_in_semcor     ', self.all_synsets_in_semcor_tokens)
        print('      not_all_synsets_in_semcor ', self.not_all_synsets_in_semcor_tokens)
        print("      ratio of known synsets:    %.2f" % (self.all_synsets_in_semcor_tokens / total))


if __name__ == '__main__':

    if len(sys.argv) > 1 and sys.argv[1] == '--extract':
        wn = load_wordnet()
        lemmas = load_lemmas()
        baseline = BaseLineAlgorithm(wn, lemmas)
        baseline.run()
        baseline.print_results()
        SemcorCoverageStatistics(wn, lemmas).write()
    else:
        btm = BasicTypes()
        print(btm)
        btm.remove_type('art')
        btm.remove_type('axe')   # does nothing, no error
        print(btm)               # should be less types now
        btm.replace_type_with_supertype('spc')
        btm.replace_type_with_subtypes('spc.sup')
        btm.print_types()



