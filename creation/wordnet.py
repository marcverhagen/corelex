"""


"""


import sys
import textwrap
from ansi_codes import BOLD, BLUE, RESET
from ansi_codes import blue, green, bold, boldgreen

NOUN = 'noun'
VERB = 'verb'

if sys.version_info.major < 3:
    raise Exception("Python 3 is required.")


class WordNet(object):

    def __init__(self, wn_version,
                 noun_index_file, noun_data_file,
                 verb_index_file, verb_data_file):
        self.version = wn_version
        self.lemma_idx = { NOUN: {}, VERB: {} }
        self.synset_idx = { NOUN: {}, VERB: {} }
        self._load_index(NOUN, noun_index_file)
        self._load_synsets(NOUN, noun_data_file)

    def _load_index(self, cat, index_file):
        print('Loading %s ...' % index_file)
        for line in open(index_file):
            if line.startswith('  ') or len(line) < 25:
                continue
            word = Word(line.strip())
            self.lemma_idx[cat][word.lemma] = word.synsets

    def _load_synsets(self, cat, data_file):
        print('Loading %s ...' % data_file)
        for line in open(data_file):
            if line.startswith('  ') or len(line) < 25:
                continue
            synset = Synset(self, line.strip())
            self.synset_idx[cat][synset.id] = synset

    def get_noun_synset(self, synset_offset):
        return self.synset_idx[NOUN].get(synset_offset)

    def add_basic_types(self, basic_types):
        for name in basic_types:
            for synset, members in basic_types[name]:
                self.get_noun_synset(synset).make_basic_type(name)


class Word(object):

    def __init__(self, line):
        self.fields = line.split()
        self.lemma = self.fields[0]
        # this is more general since WordNet 1.5 and 3.1 differ in where the
        # synset count is
        self.synsets = [f for f in self.fields if len(f) == 8 and f.isdigit()]


class Synset(object):

    def __init__(self, wordnet, line, cat=NOUN):
        """Initialize a synset by parsing the line in the data file. We are using the
        byte offset of the line as the synset identifier."""
        self.wn = wordnet
        self.cat = NOUN
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
            print('WARNING: unparsed fields for', self)
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
        # TODO: make it use self.cat in determining where to get the synsets
        pointers = self.pointers.get('@', [])
        pointers.extend(self.pointers.get('@i', []))
        return [self.wn.get_noun_synset(p.target_synset) for p in pointers]

    def hyponyms(self):
        # TODO: make it use self.cat in determining where to get the synsets
        pointers = self.pointers.get('~', [])
        return [self.wn.get_noun_synset(p.target_synset) for p in pointers]

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
        print("%s" % self)
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
        print('%s%s' % (indent, self))
        for hyper in self.hypernyms():
            hyper.pp_paths_to_top(indent + '  ')

    def pp_hypernyms(self):
        if self.has_hypernyms():
            print('\n  %shypernyms%s' % (BLUE, RESET))
            for synset in self.hypernyms():
                print('    [%d] %s' % (self.count, synset))
                self.mappings[self.count] = synset
                self.count +=1

    def pp_hyponyms(self):
        if self.has_hyponyms():
            print('\n  %shyponyms%s' % (BLUE, RESET))
            for synset in self.hyponyms():
                print('    [%d] %s' % (self.count, synset))
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
        return "<Pointer %s %s>" % (self.symbol, self.target_synset)
