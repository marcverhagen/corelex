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
import copy
import textwrap

import cltypes
from utils import flatten, blue, green, bold, boldgreen, index_file, data_file, sense_file
from config import WORDNET_DIR

import pdb

NOUN = 'noun'
VERB = 'verb'


POINTER_SYMBOL_LIST = [

    '!', '@', '@i', '~', '~i', '#m', '#s', '#p', '%m', '%s', '%p', '=', '+',
    ';c', ';r', ';u', '-c', '-r', '-u',
    '*', '>', '^', '$', '+',
    '&', '<', '\\', '='
]


POINTER_SYMBOLS = {

    '!': 'Antonym',
    '@': 'Hypernym',
    '@i': 'Instance Hypernym',
    '~': 'Hyponym',
    '~i': 'Instance Hyponym',
    '#m': 'Member holonym',
    '#s': 'Substance holonym',
    '#p': 'Part holonym',
    '%m': 'Member meronym',
    '%s': 'Substance meronym',
    '%p': 'Part meronym',
    '=': 'Attribute',
    '+': 'Derivationally related form',
    ';c': 'Domain of synset - TOPIC',
    ';r': 'Domain of synset - REGION',
    ';u': 'Domain of synset - USAGE',
    '-c': 'Member of this domain - TOPIC',
    '-r': 'Member of this domain - REGION',
    '-u': 'Member of this domain - USAGE',

    '*': 'Entailment',
    '>': 'Cause',
    '^': 'Also see',
    '$': 'Verb Group',
    '+': 'Derivationally related form',

    '&': 'Similar to',
    '<': 'Participle of verb',
    '\\': 'Pertainym (pertains to noun)',
    '=': 'Attribute'
}


if sys.version_info.major < 3:
    raise Exception("Python 3 is required.")


def expand(category):
    """Mapping from abbreviations to category name."""
    if category == 'n': return NOUN
    if category == 'v': return VERB
    return category


class WordNet(object):

    def __init__(self, wn_version, category=None):

        if not wn_version in ('1.5', '3.1'):
            exit("ERROR: unsupported wordnet version")

        self.version = wn_version
        self.category = expand(category)

        # store Word instances indexed on the lemmas and Synset instances on the
        # synset identifiers
        self._lemma_idx = { NOUN: {}, VERB: {} }
        self._synset_idx = { NOUN: {}, VERB: {} }

        # PGA
        # map sense_id to synset_offset 
        # and (lemma synset_offset) to synset number
        self._sense_idx = {}
        self._synset_no_idx = {}

        # a list of all relations where a relation is a pair of a Synset
        # instance and a Pointer instance
        self._all_relations = None

        # a list of all synsets that are basic types
        self._basic_types = { NOUN: [], VERB: [] }

        #pdb.set_trace()

        wn_dir = WORDNET_DIR % wn_version
        
        self._load_lemmas(NOUN, index_file(wn_dir, wn_version, NOUN))
        self._load_synsets(NOUN, data_file(wn_dir, wn_version, NOUN))
        self._load_lemmas(VERB, index_file(wn_dir, wn_version, VERB))
        self._load_synsets(VERB, data_file(wn_dir, wn_version, VERB))
        
        # PGA: sense_file maps sense_keys to sense_offsets
        # sense_keys do not change across versions, while sense_offsets can.
        self._load_senses(sense_file(wn_dir, wn_version))

        print("Loaded", self)

    def __str__(self):
        return "<WordNet nouns=%d verbs=%d>" \
            % (len(self._lemma_idx[NOUN]), len(self._lemma_idx[VERB]))

    def _load_lemmas(self, cat, index_file):
        print('Loading %s ...' % index_file)
        for line in open(index_file):
            if line.startswith('  ') or len(line) < 25:
                continue
            word = Word(line.strip())
            self._lemma_idx[cat][word.lemma] = word

    def _load_synsets(self, cat, data_file):
        print('Loading %s ...' % data_file)
        c = 0
        for line in open(data_file):
            c += 1
            #if c > 50: break
            if line.startswith('  ') or len(line) < 25:
                continue
            synset = Synset(self, line.strip(), cat)
            self._synset_idx[cat][synset.id] = synset

    # PGA
    # Load wordnet's index.sense file, that contains mappings from immutable
    # sense keys to synset offsets (which can change from version to version)
    # line example: bank%1:14:00:: 08437235 2 20
    def _load_senses(self, sense_file):
        print('Loading index.sense file')
        for line in open(sense_file):
            sense_id, synset_offset, synset_no, corpus_count = line.split(" ")
            synset_no = int(synset_no)
            self._sense_idx[sense_id] = synset_offset
            # Given a lemma and a synset offset, return the 
            # number of that synset for the lemma.  Synsets are
            # numbered by corpus frequency, so that the most
            # frequent synset(s) appear with the lowest numbers.
            lemma, rest = sense_id.split("%")
            self._synset_no_idx[(lemma, synset_offset)] = synset_no

    def lemma_index(self):
        return self._lemma_idx

    def synset_index(self):
        return self._synset_idx

    def sense_index(self):
        return self._sense_idx

    def synset_no_idx(self):
        return self._synset_no_idx

    def basic_types(self, cat=NOUN):
        return self._basic_types[cat]

    def get_noun(self, lemma):
        """Return None or the Word instance for the noun."""
        return self._lemma_idx[NOUN].get(lemma)

    def get_verb(self, lemma):
        """Return None or the Word instance for the verb."""
        return self._lemma_idx[VERB].get(lemma)

    def get_lemmas(self, lemma):
        """Return a dictionary with NOUN and VERB keys. The value of each key is
        a Word instance or None."""
        return { NOUN: self.get_noun(lemma),
                 VERB: self.get_verb(lemma) }

    def get_noun_synset(self, synset_offset):
        """Return the synset object for the synset identifier."""
        return self.get_synset(NOUN, synset_offset)

    def get_verb_synset(self, synset_offset):
        return self.get_synset(VERB, synset_offset)

    def get_synset(self, category, synset_offset):
        return self._synset_idx[category].get(synset_offset)

    def get_basic_types(self, cat):
        """return all synsets that are basic types."""
        return [ss for ss in self.get_all_synsets(cat) if ss.is_basic_type]

    def add_basic_types(self):
        """Add basic type information to verb and noun synsets."""
        self.add_nominal_basic_types()
        self.add_verbal_basic_types()
        
    def add_nominal_basic_types(self):
        """Add basic type information to noun synsets. This starts with the manually
        created lists in cltypes and adds information to the synsets mentioned
        in those lists. As a next step it descends down the hyponym tree for
        each marked synset and adds the basic types to sub synsets. If a synset
        is assigned two basic types bt1 and bt2 and bt1 is a subtype of bt2 then
        bt2 will not be included."""
        btypes = cltypes.get_basic_types(self.version)
        for btype in btypes:
            for synset_id, members in btypes[btype]:
                synset = self.get_noun_synset(synset_id)
                synset.is_basic_type = True
                synset.basic_type_name = btype
                synset.basic_types = set([btype])
                self._basic_types[NOUN].append(synset)
        for synset in self.basic_types(NOUN):
            for hyponym in synset.hyponyms():
                hyponym.add_basic_type(synset)
        type_relations = cltypes.get_type_relations(self.version)
        for synset in self.get_all_noun_synsets():
            synset.reduce_basic_types(type_relations)

    def add_verbal_basic_types(self):
        count = 0
        for synset in self.get_all_verb_synsets():
            if not synset.has_hypernyms():
                count += 1
                words = ["%s.%s.%s" % (word_lex[0], synset.lex_filenum, word_lex[1])
                         for word_lex in synset.words]
                name = ' '.join(words)
                synset.is_basic_type = True
                synset.basic_type_name = name
                synset.basic_types = set([name])
                self._basic_types[VERB].append(synset)
        for synset in self.basic_types(VERB):
            for hyponym in synset.hyponyms():
                hyponym.add_basic_type(synset)

    def toptypes(self, cat):
        toptypes = []
        for synset in self._synset_idx[cat].values():
            if not synset.has_hypernyms():
                toptypes.append(synset)
        return toptypes

    def pp_nouns(self, words):
        for w in words:
            self.pp_noun(w)
        print()

    def pp_noun(self, w):
        print("\n", w)
        word = self.get_noun(w)
        if word is None:
            print('   does not occur in WordNet')
        else:
            for synset_id in word.synsets:
                synset = self.get_noun_synset(synset_id)
                print('  ', synset.formatted())

    def pp_toplevel(self, cat):
        toptypes = self.toptypes(cat)
        for tt in toptypes:
            tt.pp_tree(4)
            print()

    def pp_basic_types(self, cat):
        basic_types = self.get_basic_types(cat)
        for bt in basic_types:
            synsets = [ss for ss in flatten(bt.paths_to_top()) if ss.is_basic_type]
            super_types = set([ss.basic_type_name for ss in synsets])
            super_types.remove(bt.basic_type_name)
            print(bt, ' '.join(super_types))
        print("\nNumber of basic types: %d\n" % len(basic_types))

    def get_all_noun_synsets(self):
        return self.get_all_synsets(NOUN)

    def get_all_verb_synsets(self):
        return self.get_all_synsets(VERB)

    def get_all_synsets(self, cat):
        """Return a list of all synsets for the category."""
        return self._synset_idx[cat].values()

    def get_all_terminal_synsets(self, cat):
        """Return a list of all terminal synsets for the category."""
        synsets = get_all_synsets(cat)
        synsets = [ss for ss in synsets if not ss.has_hyponyms]
        return synsets

    def get_all_relations(self, cat):
        """Return all relations between synsets of the given category."""
        if self._all_relations is None:
            self._all_relations = []
            synsets = self.get_all_synsets(cat)
            for synset in synsets:
                for symbol, pointers in synset.pointers.items():
                    for pointer in pointers:
                        if expand(pointer.pos) == cat:
                            self._all_relations.append([synset, pointer])
        return self._all_relations

    def get_all_basic_type_relations(self, cat):
        """Return a list of 5-tuples of the form <basic_type_name, pointer_symbol,
        basic_type_name, source_synset, target_synset>. There is at least one
        tuple for each relation amongst nominal synsets with the synsets
        replaced by the name of the basic types. If one of the synsets has two
        or more basic types, then a basic type relation will be created for each
        of them."""
        relations = self.get_all_relations(cat)
        bt_relations = []
        for source_synset, pointer in relations:
            # skip hypernyms and hyponyms
            if pointer.symbol in ('~', '~i', '@', '@i'):
                continue
            # skip lexical links
            if pointer.pointer_type != '0000':
                continue
            target_synset = self.get_noun_synset(pointer.target_synset)
            # some pointers are not to nouns, skip them
            if target_synset is None:
                continue
            for bts in source_synset.basic_types:
                for btt in target_synset.basic_types:
                    bt_relations.append([bts, pointer.symbol, btt,
                                         source_synset, target_synset])
        return bt_relations

    def display_basic_type_isa_relations(self):
        """Utility method to generate all subtype-supertype pairs amongst basic
        types. Results from this can be hand-fed into the cltypes module."""
        pairs = []
        for bt in self.get_basic_types():
            synsets = [ss for ss in flatten(bt.paths_to_top()) if ss.is_basic_type]
            super_types = set([ss.basic_type_name for ss in synsets])
            super_types.remove(bt.basic_type_name)
            for st in super_types:
                pairs.append((bt.basic_type_name, st))
        for pair in sorted(set(pairs)):
            print("%s," % str(pair), end='')
        print(len(pairs), len(set(pairs)))


class Word(object):

    # This class is only used as a way to store the synset identifiers that go
    # with a lemma.

    def __init__(self, line):
        self.fields = line.split()
        self.lemma = self.fields[0]
        # this is more general since WordNet 1.5 and 3.1 differ in where the
        # synset count is specified
        self.synsets = [f for f in self.fields if len(f) == 8 and f.isdigit()]

    def __str__(self):
        return "<Word %s - %s>" % (self.lemma, ' '.join(self.synsets))


class Synset(object):

    # TODO: for verb synsets not all data are loaded. In particular, it could
    # have something like '01 + 09 00' following the pointers.

    def __init__(self, wordnet, line, cat):
        """Initialize a synset by parsing the line in the data file. We are using the
        byte offset of the line as the synset identifier."""

        self.wn = wordnet
        self.cat = cat
        self.line = line

        # Default is that a synset is not a basic type, when we use basic types
        # then this default needs to be overwritted.
        # basic type.
        self.is_basic_type = False
        # If a synset is a basic type then the name of the type is stored here.
        self.basic_type_name = None
        # If used, this will contain the basic type names for this synset, this
        # would include a basic type from a synset higher in the synset
        # tree. Note that due to multiple inheritance there can be more than one
        # basic type here.
        self.basic_types = set()

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
        self._parse_words(fields)      # sets self.w_cnt and self.words list
        self._parse_pointers(fields)   # sets self.p_cnt and self.pointers dictionary
        self.fields = fields
        self.validate()


    def __str__(self):
        words = self.words_as_string()
        basic_type = ' %s' % self.basic_type_name if self.is_basic_type else ''
        return "<Synset %s %s %s%s>" % (self.id, self.ss_type, words, basic_type)

    def as_html(self):
        # currently not printing the synset identifier or the castegory
        words = ' '.join(["<span class=blue>%s</span>.%s.%s"
                          % (word_lex[0], self.lex_filenum, word_lex[1])
                          for word_lex in self.words])
        if self.is_basic_type:
            basic_type = '*' + self.basic_type_name
        else:
            basic_type = ' '.join(self.basic_types)
        return "%s <span class=green>%s</span>" % (words, basic_type)

    def formatted(self):
        return self.as_formatted_string()

    def words_as_string(self):
        return ' '.join(["%s.%s.%s" % (word_lex[0], self.lex_filenum, word_lex[1])
                         for word_lex in self.words])

    def as_formatted_string(self):
        words = ' '.join(["%s.%s.%s" % (blue(word_lex[0]), self.lex_filenum, word_lex[1])
                          for word_lex in self.words])
        basic_type = ' %s' % green('*' + self.basic_type_name) if self.is_basic_type else ''
        if not basic_type:
            basic_type = ' ' + green(' '.join(self.basic_types))
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
        self.is_basic_type = True
        self.basic_type_name = name

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
        return self.pointers.get('~') is not None \
            or self.pointers.get('~i') is not None

    def hypernyms(self):
        """Returns a list of hypernyms and instance hypernyms."""
        return self.get_pointers(['@', '@i'])

    def hyponyms(self):
        """Returns a list of hyponyms and instance hyponyms."""
        return self.get_pointers(['~', '~i'])

    def holonyms(self):
        """Returns a list of member, substance and part holonyms."""
        return self.get_pointers(['#m', '#s', '#p'])

    def meronyms(self):
        """Returns a list of member, substance and part meronyms."""
        return self.get_pointers(['%m', '%s', '%p'])

    def antonyms(self):
        """Returns a list of antonyms."""
        return self.get_pointers(['!'])

    def attributes(self):
        """Returns a list of attributes."""
        return self.get_pointers(['='])

    def get_pointers(self, pointer_list):
        # include only semantic pointers
        pointers = []
        for symbol in pointer_list:
            pointers.extend(self.pointers.get(symbol, []))
        return [self.wn.get_synset(self.cat, p.target_synset)
                for p in pointers if p.pointer_type == '0000']

    def paths_to_top(self):
        hypernyms = self.hypernyms()
        if not hypernyms:
            return [self]
        else:
            return [self] + [hyper.paths_to_top() for hyper in hypernyms]

    def add_basic_type(self, synset):
        """Recursively add a basic type to a synset. This would be the basic type
        that domitates the synset in the WordNet tree. Note that the synset given
        as an argument is not the basic type itself (since a basic type can contain
        more than one synset), but that it stores the name of the basic type in
        one of its variables.""" 
        self.basic_types.add(synset.basic_type_name)
        for hyponym in self.hyponyms():
            hyponym.add_basic_type(synset)

    def reduce_basic_types(self, type_relations):
        btypes = copy.copy(self.basic_types)
        for (subtype, supertype) in type_relations:
            if subtype in btypes and supertype in btypes:
                btypes.discard(supertype)
        self.basic_types = btypes

    def pp(self):
        """Write a pretty print to the standard output. This includes printing
        identifiers before synsets like [3], which can be used for further navigation in
        the userloop."""
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
        for symbol in POINTER_SYMBOL_LIST:
            self.pp_related_synsets(POINTER_SYMBOLS.get(symbol), pointer_symbols=[symbol])
        # not doing these because they can go to different categories
        # self.pp_attributes()
        
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

    def pp_pointers(self):
        print(self)
        for symbol, pointers in self.pointers.items():
            print("   %3s " % symbol, end='')
            for pointer in pointers[:10]:
                print(" %s" % pointer.target_synset, end='')
            print()
        print()

    def pp_related_synsets(self, name, synsets=None, pointer_symbols=None):
        if synsets is None:
            synsets = self.get_pointers(pointer_symbols)
        # doing this filter since for now we do not find related synsets that do
        # not have the same category
        synsets = [ss for ss in synsets if ss is not None]
        if synsets:
            print('\n  %s' % blue(name))
            for synset in synsets:
                print('    [%d] %s' % (self.count, synset.as_formatted_string()))
                self.mappings[self.count] = synset
                self.count +=1

    def pp_hypernyms(self):
        self.pp_related_synsets('hypernyms', self.hypernyms())

    def pp_hyponyms(self):
        self.pp_related_synsets('hyponyms', self.hyponyms())

    def pp_holonyms(self):
        self.pp_related_synsets('holonyms', self.holonyms())

    def pp_meronyms(self):
        self.pp_related_synsets('meronyms', self.meronyms())

    def pp_antonyms(self):
        self.pp_related_synsets('antonyms', self.antonyms())

    def pp_attributes(self):
        self.pp_related_synsets('attributes', self.attributes())

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
