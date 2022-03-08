"""wordnet.py

Module that provides access to WordNet 1.5 and WordNet 3.1 data.

Assumes that the two WordNet versions can be found using the directory template
in WORDNET_DIR. It also assumes that the WordNet-3.1 distribution is as
downloaded from the WordNet website. Dowloading WordNet 1.5 gives you a
directory wn15 and this directory should be immediately under the WordNet-1.5
directory.

See https://wordnet.princeton.edu/documentation/wndb5wn for the format of the
data and index files.

Loading WordNet requires version 1.5 or 3.1:

   >>> wn = WordNet('3.1')
   Loading /DATA/resources/lexicons/wordnet/WordNet-3.1/DICT/index.noun ...
   Loading /DATA/resources/lexicons/wordnet/WordNet-3.1/DICT/index.verb ...
   Loading /DATA/resources/lexicons/wordnet/WordNet-3.1/DICT/data.noun ...
   Loading /DATA/resources/lexicons/wordnet/WordNet-3.1/DICT/data.verb ...
   Loading /DATA/resources/lexicons/wordnet/WordNet-3.1/DICT/index.sense ...

   >>> print(wn)
   <WordNet 3.1 nouns=117953 verbs=11540>

Searching for a lemma gives you a Word instance, which stores the lemma and a
list of sysnet identifiers:

   >>> door = wn.get_noun('door')
   >>> print(door)
   <Word door - 03226423 03228735 05188408 03227021 03226879>
   >>> door.synsets
   ['03226423', '03228735', '05188408', '03227021', '03226879']

Getting the synset object given a synset identifier:

   >>> door_synset = wn.get_noun_synset('03226423')
   >>> print(door_synset)
   <Synset 03226423 n door.06.0>

"""

import sys
import copy
import textwrap
from functools import reduce

import cltypes
from config import WORDNET_DIR
from utils import flatten, blue, green, bold, boldgreen
from utils import union, index_file, data_file, sense_file


if sys.version_info.major < 3:
    raise Exception("Python 3 is required.")

NOUN = 'noun'
VERB = 'verb'

CATEGORY_ABBREVIATIONS = {'n': NOUN, 'v': VERB}

POINTER_SYMBOLS = {
    # taken from https://wordnet.princeton.edu/documentation/wninput5wn
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
    '&': 'Similar to',
    '<': 'Participle of verb',
    '\\': 'Pertainym (pertains to noun)',
}


def expand(category):
    """Mapping from abbreviations to category name."""
    return CATEGORY_ABBREVIATIONS.get(category)


class WordNet(object):

    """Class to store all WordNet information that we want access to.

    Instance variables:

    version
        WordNet version, '1.5' or '3.1'

    _lemma_idx
        Stores Word instances indexed on category and lemma
        Filled in by _load_lemmas()
        { NOUN|VERB ==> DICT { lemma ==> Word } }
        _lemma_idx['noun']['zoom'] ==> <Word zoom - 07390125 00327117>

    _synset_idx
        Stores Synset instances indexed on category and synset identifier
        Filled in by _load_synsets()
        { NOUN|VERB ==> DICT { synset_id ==> Synset } }
        _synset_idx['noun']['07390125'] ==>
          <Synset 07390125 n rapid_climb.11.0 rapid_growth.11.0 zoom.11.0>

    _sense_idx
        Stores synset identifiers (offsets) indexed on synset senses
        { synset_sense ==> synset_id }
        _sense_idx['zyrian%1:10:00::'] ==> '06969782'

    _all_relations
        A list of all relations where a relation is a pair of a Synset instance
        and a Pointer instance. Filled in by get_all_basic_type_relations().

    _basic_types
        A dictionary with for each category (noun, verb) a list of all synsets
        that are basic types. Filled in if add_basic_types in the initialization
        method was set to True.

    """

    def __init__(self, wn_version, add_basic_types=False):
        if wn_version not in ('1.5', '3.1'):
            exit("ERROR: unsupported wordnet version")
        self.version = wn_version
        self._lemma_idx = {NOUN: {}, VERB: {}}
        self._synset_idx = {NOUN: {}, VERB: {}}
        self._sense_idx = {}
        self._all_relations = None
        self._basic_types = {NOUN: [], VERB: []}
        wn_dir = WORDNET_DIR % self.version
        self._load_lemmas(NOUN, index_file(wn_dir, self.version, NOUN))
        self._load_lemmas(VERB, index_file(wn_dir, self.version, VERB))
        self._load_synsets(NOUN, data_file(wn_dir, self.version, NOUN))
        self._load_synsets(VERB, data_file(wn_dir, self.version, VERB))
        self._load_senses(sense_file(wn_dir, self.version))
        if add_basic_types:
            self.add_basic_types()

    def __str__(self):
        return "<WordNet %s nouns=%d verbs=%d>" \
            % (self.version, len(self._lemma_idx[NOUN]), len(self._lemma_idx[VERB]))

    def _load_lemmas(self, cat, index_file):
        """Load all lemmas from the index file."""
        print('Loading %s ...' % index_file)
        for line in open(index_file):
            if line.startswith('  ') or len(line) < 25:
                continue
            # Example input line:
            #   zoom v 3 3 @ ~ + 3 1 02059445 02060133 01947577
            word = Word(line.strip())
            self._lemma_idx[cat][word.lemma] = word

    def _load_synsets(self, cat, data_file):
        """Load all synsets from the data file."""
        print('Loading %s ...' % data_file)
        c = 0
        for line in open(data_file):
            c += 1
            # if c > 50: break
            if line.startswith('  ') or len(line) < 25:
                continue
            # Example input line:
            #   02770203 43 v 01 flare_up 0 002 @ 02765572 v 0000 ~ 02767643 \
            #   v 0000 01 + 01 00 | ignite quickly and suddenly, especially \
            #   after having died down; "the fire flared up and died down \
            #   once again"
            synset = Synset(self, line.strip(), cat)
            self._synset_idx[cat][synset.id] = synset

    def _load_senses(self, sense_file):
        """Load wordnet's index.sense file, which contains mappings from immutable sense
        keys to synset offsets (which can change from version to version)."""
        if self.version == '1.5':
            # there is no index.sense file for version 1.5, so skip it
            return
        print('Loading %s ...' % sense_file)
        for line in open(sense_file):
            # Example input line:
            #   bank%1:14:00:: 08437235 2 20
            # TODO: maybe nice to use a Sense class
            sense_id, synset_offset, synset_no, corpus_count = line.split(" ")
            synset_no = int(synset_no)
            self._sense_idx[sense_id] = synset_offset

    def lemma_index(self):
        return self._lemma_idx

    def synset_index(self):
        return self._synset_idx

    def sense_index(self):
        return self._sense_idx

    def basic_types(self, cat=NOUN):
        return self._basic_types[cat]

    def get_word(self, lemma, cat):
        """Return None or the Word instance for the lemma of category cat."""
        return self._lemma_idx[cat].get(lemma)

    def get_noun(self, lemma):
        """Return None or the Word instance for the noun."""
        return self.get_word(lemma, NOUN)

    def get_verb(self, lemma):
        """Return None or the Word instance for the verb."""
        return self.get_word(lemma, VERB)

    def get_lemmas(self, lemma):
        """Return a dictionary with NOUN and VERB keys. The value of each key is
        a Word instance or None."""
        return {NOUN: self.get_noun(lemma), VERB: self.get_verb(lemma)}

    def get_synset(self, category, synset_offset):
        return self._synset_idx[category].get(synset_offset)

    def get_noun_synset(self, synset_offset):
        """Return the synset object for the synset identifier."""
        return self.get_synset(NOUN, synset_offset)

    def get_verb_synset(self, synset_offset):
        return self.get_synset(VERB, synset_offset)

    def get_basic_types(self, cat):
        """return all synsets that are basic types."""
        return [ss for ss in self.get_all_synsets(cat) if ss.is_basic_type()]

    def get_basic_types_for_noun(self, noun):
        """Get a set of all the basic types for the noun lemma."""
        synsets = self.get_noun(noun).synsets
        sets = [self.get_synset('noun', ss).basic_types for ss in synsets]
        return reduce(union, sets)

    def reset_nominal_basic_types(self):
        for synset in self._synset_idx[NOUN].values():
            synset.reset_basic_types()

    def add_basic_types(self):
        """Add basic type information to verb and noun synsets."""
        self.add_nominal_basic_types()
        self.add_verbal_basic_types()

    def add_nominal_basic_types(self, btypes=None):
        """Add basic type information to noun synsets. This starts with the manually
        created lists in cltypes and adds information to the synsets mentioned
        in those lists. As a next step it descends down the hyponym tree for
        each marked synset and adds the basic types to sub synsets. If a synset
        is assigned two basic types bt1 and bt2 and bt1 is a subtype of bt2 then
        bt2 will not be included."""
        if btypes is None:
            # use the default if no basic types were handed in
            btypes = cltypes.get_basic_types(self.version)
        for btype in btypes:
            for synset_id, members in btypes[btype]:
                synset = self.get_noun_synset(synset_id)
                synset.basic_type = btype
                synset.basic_types = {btype}
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
                synset.basic_type = name
                synset.basic_types = {name}
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
            synsets = [ss for ss in flatten(bt.paths_to_top())
                       if ss.is_basic_type()]
            super_types = set([ss.basic_type for ss in synsets])
            super_types.remove(bt.basic_type)
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
        synsets = self.get_all_synsets(cat)
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
        """Return a list of 5-tuples of the form <basic_type, pointer_symbol,
        basic_type, source_synset, target_synset>. There is at least one
        tuple for each relation amongst nominal synsets with the synsets
        replaced by the name of the basic types. If one of the synsets has two
        or more basic types, then a basic type relation will be created for each
        of them."""
        relations = self.get_all_relations(cat)
        bt_relations = []
        for source_synset, pointer in relations:
            # skip hypernyms and hyponyms
            if pointer.is_hypernym_or_hyponym():
                continue
            if pointer.is_lexical():
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
        for bt in self.get_basic_types(NOUN):
            synsets = [ss for ss in flatten(bt.paths_to_top())
                       if ss.is_basic_type()]
            super_types = set([ss.basic_type for ss in synsets])
            super_types.remove(bt.basic_type)
            for st in super_types:
                pairs.append((bt.basic_type, st))
        for pair in sorted(set(pairs)):
            print("%s," % str(pair), end='')
        print(len(pairs), len(set(pairs)))


class Word(object):

    """Used to store all the synset identifiers that go with a lemma. There is
    a one-to-one correspondence between Word instances and lemmas (modulo the
    category)."""

    def __init__(self, line):
        """Create an instance from a line in the Wordnet index file."""
        self.fields = line.split()
        self.lemma = self.fields[0]
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
        self.basic_type = None    # name of basic type
        self.basic_types = set()  # set of basic type and inherited basic types
        try:
            fields, gloss = self.line.split('|')
            self.gloss = gloss.strip()
        except ValueError:
            # WordNet 1.5 does not always have a gloss
            fields = self.line
            self.gloss = None
        fields = fields.strip().split()
        self.id = fields.pop(0)
        self.lex_filenum = fields.pop(0)
        self.ss_type = fields.pop(0)
        self.p_cnt = None
        self.w_cnt = None
        self.words = None              # list of words
        self.pointers = None           # dictionary of pointers
        self._parse_words(fields)      # sets self.w_cnt and self.words
        self._parse_pointers(fields)   # sets self.p_cnt and self.pointers
        self.fields = fields
        self.validate()

    def __str__(self):
        words = self.words_as_string()
        basic_type = ' %s' % self.basic_type if self.is_basic_type() else ''
        return "<Synset %s %s %s%s>" % (self.id, self.ss_type, words, basic_type)

    def is_basic_type(self):
        return self.basic_type is not None

    def reset_basic_types(self):
        self.basic_type = None
        self.basic_types = set()

    def as_html(self):
        # currently not printing the synset identifier or the castegory
        words = ' '.join(["<span class=blue>%s</span>.%s.%s"
                          % (word_lex[0], self.lex_filenum, word_lex[1])
                          for word_lex in self.words])
        if self.is_basic_type():
            basic_type = '*' + self.basic_type
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
        basic_type = ' %s' % green('*' + self.basic_type) if self.is_basic_type() else ''
        if not basic_type:
            basic_type = ' ' + green(' '.join(self.basic_types))
        # return "%s %s" % (self.id, words)
        return "<Synset %s %s %s%s>" % (self.id, self.ss_type, words, basic_type)

    def parents(self):
        return self.hypernyms()

    def children(self):
        return self.hyponyms()

    def sisters(self):
        my_sisters = []
        for parent in self.parents():
            for child in parent.children():
                # do not include the source synset
                if child != self:
                    my_sisters.append(child)
        return my_sisters

    @staticmethod
    def _validate_w_cnt(field):
        if len(field) != 2:
            return False
        try:
            int(field, 16)
            return True
        except ValueError:
            return False

    def _validate_p_cnt(self, field, line):
        if len(field) != 3 or not field.isdigit():
            print("WARNING: '%s' is not a correct p_cnt" % self.p_cnt)
            print(line)

    def validate(self):
        if self.fields:
            if self.fields[1] != '+':
                print('WARNING: unparsed fields for', self)
                print(self.line)
                print(self.fields)
        self._validate_pointers()

    def make_basic_type(self, name):
        """Make the synset a basic type by changing the value of the basic_type instance
        variable from None to the name of the type."""
        self.basic_type = name

    def _parse_words(self, fields):
        # this first field should be a hexadecimal string of length 2
        self._validate_w_cnt(fields[0])
        self.w_cnt = int(fields.pop(0), 16)
        self.words = []
        for i in range(self.w_cnt):
            self.words.append([fields.pop(0), fields.pop(0)])
        # PGA: Store a flat list of the word strings themselves
        self.l_words = [item[0] for item in self.words]
        # word list excluding compound terms (containing "_")
        self.simple_words = []
        for item in self.l_words:
            if "_" not in item:
                self.simple_words.append(item)

    def _parse_pointers(self, fields):
        self._validate_p_cnt(fields[0], self.line)
        self.p_cnt = int(fields.pop(0))
        self.pointers = {}
        for i in range(self.p_cnt):
            pointer = Pointer(fields)
            if pointer.symbol not in self.pointers:
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
                for p in pointers if p.is_semantic()]

    def paths_to_top(self):
        hypernyms = self.hypernyms()
        if not hypernyms:
            return [self]
        else:
            return [self] + [hyper.paths_to_top() for hyper in hypernyms]

    def add_basic_type(self, synset):
        """Recursively add a basic type to a synset. This would be the basic type
        that dominates the synset in the WordNet tree. Note that the synset given
        as an argument is not the basic type itself (since a basic type can contain
        more than one synset), but that it stores the name of the basic type in
        one of its variables."""
        self.basic_types.add(synset.basic_type)
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
        the userloop used by the browser."""
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
        for symbol in POINTER_SYMBOLS:
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
                self.count += 1

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

    """A pointer to another synset, either between words of the synset or between
    the synsets themselves. Pointers in the source file are tuples of the form
    <symbol, target_synset, pos, source_target>, they look like

        @ 02765572 v 0000
        ~ 02767643 v 0000

    The source is implied because a Pointer always lives inside of a Synset
    instance (similar to how pointer tuples are associated with a source synset
    in the source file).

    Instance variables:

    symbol
        The pointer symbol, see the POINTER_SYMBOLS dictionary. The pointer
        symbol is a shorthand for a WordNet relation.

    target_synset
        The identifier of the target synset.

    pos
        The part of speeach of the target synset.

    source_target
        The exact source and target. If this is 0000 then the relation is
        between the synsets. Otherwise the first two digits identify the source
        word and the second two the target word. For example, if the type is
        0301 then the relation is between the third word of the source synset
        and the first word of the target synset.

    """

    def __init__(self, fields):
        """Initialize a pointer from the first four elements of the fields list. This
        removes the first four elements of fields."""
        self.symbol = fields.pop(0)
        self.target_synset = fields.pop(0)
        self.pos = fields.pop(0)
        self.source_target = fields.pop(0)

    def __str__(self):
        return "<Pointer %s %s %s %s>" % (self.pos, self.symbol,
                                          self.target_synset, self.source_target)

    def is_lexical(self):
        """Return true if the relation is between words."""
        return self.source_target != '0000'

    def is_semantic(self):
        """Return true if the relation is between synsets."""
        return self.source_target == '0000'

    def is_hypernym_or_hyponym(self):
        return self.symbol in ('~', '~i', '@', '@i')


if __name__ == '__main__':

    import doctest
    doctest.testmod()
