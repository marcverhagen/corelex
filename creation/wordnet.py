"""wordnet.py

Module that provides access to WordNet 1.5 and WordNet 3.1 data.

It assumes that the two WordNet versions can be found using the directory
template in WORDNET_DIR. It also assumes that the WordNet-3.1 distribution is as
downloaded from the WordNet website. Dowloading WordNet 1.5 gives you a
directory wn14 and this directory should be immediately under the WordNet-1.5
directory.

Loading WordNet requires a version (1.5 or 3.1) and a category (noun or verb):

   >>> wn = WordNet('1.5', NOUN)
   Loading /DATA/resources/lexicons/wordnet/WordNet-1.5/wn15/DICT/NOUN.IDX ...
   Loading /DATA/resources/lexicons/wordnet/WordNet-1.5/wn15/DICT/NOUN.DAT ...
   Loaded 87511 noun lemmas and 60557 noun synsets
   Loaded 0 verb lemmas and 0 verb synsets

   >>> print(wn)
   <WordNet cat=noun lemma-count=87511>

Searching for a lemma gives you a list of synset identifiers, which can be empty:

   >>> wn.get_noun('door')
   ['02432728', '02435375', '03588923', '02433420', '02433281', '02433101']

   >>> wn.get_noun('doorx')
   []

Getting the synset object given a synset identifier:

   >>> door_synset = wn.get_noun_synset('02432728')
   >>> print(door_synset)
   <Synset 02432728 n door.06.0>

"""


import sys
import textwrap

import cltypes
from utils import flatten, blue, green, bold, boldgreen, index_file, data_file

WORDNET_DIR = '/DATA/resources/lexicons/wordnet/WordNet-%s/'

NOUN = 'noun'
VERB = 'verb'

if sys.version_info.major < 3:
    raise Exception("Python 3 is required.")


class WordNet(object):

    def __init__(self, wn_version, category):

        self.version = wn_version
        self.category = category
        self._lemma_idx = { NOUN: {}, VERB: {} }
        self._synset_idx = { NOUN: {}, VERB: {} }

        wn_dir = WORDNET_DIR % wn_version
        noun_index_file = index_file(wn_dir, wn_version, 'noun')
        noun_data_file = data_file(wn_dir, wn_version, 'noun')
        verb_index_file = index_file(wn_dir, wn_version, 'verb')
        verb_data_file = data_file(wn_dir, wn_version, 'verb')

        if category == NOUN:
            self._load_lemmas(NOUN, noun_index_file)
            self._load_synsets(NOUN, noun_data_file)
        elif category == VERB:
            self._load_lemmas(VERB, verb_index_file)
            self._load_synsets(VERB, verb_data_file)
        print("Loaded %d noun lemmas and %d noun synsets" %
              (len(self._lemma_idx[NOUN]), len(self._synset_idx[NOUN])))
        print("Loaded %d verb lemmas and %d verb synsets" %
              (len(self._lemma_idx[VERB]), len(self._synset_idx[VERB])))

    def __str__(self):
        return "<WordNet cat=%s lemma-count=%d>" % (self.category, len(self._lemma_idx[self.category]))

    def _load_lemmas(self, cat, index_file):
        print('Loading %s ...' % index_file)
        for line in open(index_file):
            if line.startswith('  ') or len(line) < 25:
                continue
            word = Word(line.strip())
            self._lemma_idx[cat][word.lemma] = word.synsets

    def _load_synsets(self, cat, data_file):
        print('Loading %s ...' % data_file)
        c = 0
        for line in open(data_file):
            c += 1
            #if c > 50: break
            if line.startswith('  ') or len(line) < 25:
                continue
            #print(line)
            synset = Synset(self, line.strip(), cat)
            self._synset_idx[cat][synset.id] = synset

    def lemma_index(self):
        return self._lemma_idx
    
    def synset_index(self):
        return self._synset_idx
    
    def get_noun(self, lemma):
        """Return a list of synset identifiers for the noun."""
        return self._lemma_idx[NOUN].get(lemma, [])

    def get_verb(self, lemma):
        """Return a list of synset identifiers for the verb."""
        return self._lemma_idx[VERB].get(lemma, [])

    def get_lemma(self, lemma):
        """Return a dictionary with NOUN and VERB keys. The value of each key is a list
        of synset identifiers for the lemma."""
        return { NOUN: self.get_noun(lemma), VERB: self.get_verb(lemma) }

    def get_noun_synset(self, synset_offset):
        """Return the synset obkect for the synset identifier."""
        return self.get_synset(NOUN, synset_offset)

    def get_verb_synset(self, synset_offset):
        return self.get_synset(VERB, synset_offset)

    def get_synset(self, category, synset_offset):
        return self._synset_idx[category].get(synset_offset)

    def get_basic_types(self, cat):
        return [ss for ss in self.get_all_synsets(cat) if ss.basic_type]
    
    def add_basic_types(self, cat):
        if self.version == '1.5':
            btypes = cltypes.BASIC_TYPES_1_5
        elif self.version == '3.1':
            btypes = cltypes.BASIC_TYPES_3_1
        for name in btypes:
            for synset, members in btypes[name]:
                #print(name, '-', synset, '-', members)
                self.get_synset(cat, synset).make_basic_type(name)

    def set_verbal_basic_types(self):
        for synset in self.get_all_synsets(VERB):
            if not synset.has_hypernyms():
                words = ["%s.%s.%s" % (word_lex[0], synset.lex_filenum, word_lex[1])
                         for word_lex in synset.words]
                synset.basic_type = ' '.join(words)

    def toptypes(self, cat):
        toptypes = []
        for synset in self._synset_idx[cat].values():
            if not synset.has_hypernyms():
                toptypes.append(synset)
        return toptypes

    def pp_toplevel(self, cat):
        toptypes = self.toptypes(cat)
        for tt in toptypes:
            tt.pp_tree(4)
            print()

    def pp_basic_types(self, cat):
        basic_types = self.get_basic_types(cat)
        for bt in basic_types:
            synsets = [ss for ss in flatten(bt.paths_to_top()) if ss.basic_type]
            super_types = set([ss.basic_type for ss in synsets])
            super_types.remove(bt.basic_type)
            print(bt, ' '.join(super_types))
        print("\nNumber of basic types: %d\n" % len(basic_types))

    def get_all_noun_synsets(self):
        return self.get_all_synsets(NOUN)

    def get_all_synsets(self, cat):
        """Return a list of all synsets for the category."""
        return self._synset_idx[cat].values()

    def get_all_terminal_synsets(self, cat):
        """Return a list of all terminal synsets for the category."""
        synsets = get_all_synsets(cat)
        synsets = [ss for ss in synsets if not ss.has_hyponyms]
        return synsets

    def display_basic_type_relations(self):
        """Utility method to generate all subtype-supertype pairs amongst basic
        types. Results from this can be hand-fed into the basic_types module."""
        pairs = []
        for bt in self.get_basic_types():
            synsets = [ss for ss in flatten(bt.paths_to_top()) if ss.basic_type]
            super_types = set([ss.basic_type for ss in synsets])
            super_types.remove(bt.basic_type)
            for st in super_types:
                pairs.append((bt.basic_type, st))
        for pair in sorted(set(pairs)):
            print("%s," % str(pair), end='')
        print(len(pairs), len(set(pairs)))


class Word(object):

    def __init__(self, line):
        self.fields = line.split()
        self.lemma = self.fields[0]
        # this is more general since WordNet 1.5 and 3.1 differ in where the
        # synset count is specified
        self.synsets = [f for f in self.fields if len(f) == 8 and f.isdigit()]


class Synset(object):

    # TODO: for verb synsets not all data are loaded. In particular, it could
    # have something like '01 + 09 00' following the pointers.

    def __init__(self, wordnet, line, cat):
        """Initialize a synset by parsing the line in the data file. We are using the
        byte offset of the line as the synset identifier."""
        self.wn = wordnet
        self.cat = cat
        self.line = line
        self.basic_type = False
        try:
            fields, gloss = line.split('|')
            self.gloss = gloss.strip()
        except ValueError:
            fields = line
            self.gloss = None
        fields = fields.strip().split()
        self.id = fields.pop(0)
        self.lex_filenum = fields.pop(0)
        self.ss_type = fields.pop(0)
        self._parse_words(fields)
        self._parse_pointers(fields)
        self.fields = fields
        self.validate()

    def __str__(self):
        words = ' '.join(["%s.%s.%s" % (word_lex[0], self.lex_filenum, word_lex[1])
                          for word_lex in self.words])
        basic_type = ' %s' % self.basic_type if self.basic_type else ''
        return "<Synset %s %s %s%s>" % (self.id, self.ss_type, words, basic_type)

    def as_formatted_string(self):
        words = ' '.join(["%s.%s.%s" % (blue(word_lex[0]), self.lex_filenum, word_lex[1])
                          for word_lex in self.words])
        basic_type = ' %s' % green(self.basic_type) if self.basic_type else ''
        #return "%s %s" % (self.id, words)
        return "<Synset %s %s %s%s>" % (self.id, self.ss_type, words, basic_type)

    @staticmethod
    def _validate_w_cnt(field):
        if len(field) != 2:
            return False
        try:
            int(field, 16)
            return True
        except ValueError:
            return False
        return False

    @staticmethod
    def _validate_p_cnt(field, line):
        if len(field) != 3 or not field.isdigit():
            print("WARNING: '%s' is not a correct p_cnt" % self.p_cnt)
            print(self.line)

    def validate(self):
        if self.fields:
            if self.fields[1] != '+':
                print('WARNING: unparsed fields for', self)
                print(self.line)
                print(self.fields)
        self._validate_pointers()

    def make_basic_type(self, name):
        """Make the synset a basic type by changing the value of the basic_type instance
        variable from False to the name of the type."""
        self.basic_type = name

    def _parse_words(self, fields):
        # this first field should be a hexadecimal string of length 2
        self._validate_w_cnt(fields[0])
        self.w_cnt = int(fields.pop(0), 16)
        self.words = []
        for i in range(self.w_cnt):
            self.words.append([fields.pop(0), fields.pop(0)])

    def _parse_pointers(self, fields):
        self._validate_p_cnt(fields[0], self.line)
        self.p_cnt = int(fields.pop(0))
        self.pointers = {}
        for i in range(self.p_cnt):
            pointer = Pointer(fields)         
            if not pointer.symbol in self.pointers:
                self.pointers[pointer.symbol] = []
            self.pointers[pointer.symbol].append(pointer)

    def _validate_pointers(self):
        c = int(self.p_cnt)
        if c != len(self.pointer_list()):
            print("WARNING: wrong pointer count in", self)
            print(self.line)

    def pointer_list(self):
        answer = []
        for pointers in self.pointers.values():
            answer.extend(pointers)
        return answer

    def has_hypernyms(self):
         return self.pointers.get('@') is not None \
            or self.pointers.get('@i') is not None
    
    def has_hyponyms(self):
        return self.pointers.get('~') is not None

    def hypernyms(self):
        pointers = self.pointers.get('@', [])
        pointers.extend(self.pointers.get('@i', []))
        return [self.wn.get_synset(self.cat, p.target_synset) for p in pointers]

    def hyponyms(self):
        pointers = self.pointers.get('~', [])
        return [self.wn.get_synset(self.cat, p.target_synset) for p in pointers]

    def paths_to_top(self):
        hypernyms = self.hypernyms()
        if not hypernyms:
            return [self]
        else:
            return [self] + [hyper.paths_to_top() for hyper in hypernyms]

    def pp(self):
        self.count = 0
        self.mappings = {}
        tw = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
        print("%s" % self.as_formatted_string())
        if self.gloss is not None:
            print()
            for line in tw.wrap(self.gloss):
                print(line)
        if self.hypernyms():
            print()
            self.pp_paths_to_top('  ')
        self.pp_hypernyms()
        self.pp_hyponyms()

    def pp_short(self):
        tw = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
        print("  %s" % self)
        if self.gloss is not None:
            for line in tw.wrap(self.gloss):
                print("    " + line)

    def pp_paths_to_top(self, indent=''):
        print('%s%s' % (indent, self.as_formatted_string()))
        for hyper in self.hypernyms():
            hyper.pp_paths_to_top(indent + '  ')

    def pp_hypernyms(self):
        if self.has_hypernyms():
            print('\n  %s' % blue('hypernyms'))
            for synset in self.hypernyms():
                print('    [%d] %s' % (self.count, synset.as_formatted_string()))
                self.mappings[self.count] = synset
                self.count +=1

    def pp_hyponyms(self):
        if self.has_hyponyms():
            print('\n  %s' % blue('hyponyms'))
            for synset in self.hyponyms():
                print('    [%d] %s' % (self.count, synset.as_formatted_string()))
                self.mappings[self.count] = synset
                self.count +=1

    def pp_tree(self, levels, indent=''):
        if levels == 0:
            return
        print("%s%s" % (indent, self))
        for hypo in self.hyponyms():
            hypo.pp_tree(levels - 1, indent + '  ')


class Pointer(object):

    def __init__(self, fields):
        """Initialize a pointer from the first four elements of the fields list. This
        removes the first four elements of fields."""
        self.symbol = fields.pop(0)
        self.target_synset = fields.pop(0)
        self.pos = fields.pop(0)
        self.pointer_type = fields.pop(0)

    def __str__(self):
        return "<Pointer %s %s %s %s>" % (self.pos, self.symbol, self.target_synset, self.pointer_type)


if __name__ == '__main__':

    import doctest
    doctest.testmod()
