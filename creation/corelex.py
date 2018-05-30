"""corelex.py

Script to create CoreLex from WordNet.

Usage:

   $ python3 corelex.py --create <version> <category>
   $ python3 corelex.py --sql <version> <category>
   $ python3 corelex.py --browse <version> <category>

   where <version> is 1.5 or 3.1 and <category> is n or v


==> Creating CoreLex files from WordNet

For example, to create CoreLex nouns from WordNet 1.5:

   $ python3 corelex.py --create 1.5 n

This loads the nouns from WordNet 1.5 using the wordnet.py module and then
creates two files:

   data/corelex-1.5-nouns.tab
   data/corelex-1.5-nouns.txt

The first of these can later be used to load CoreLex, the second contains the
same data but it is easier on the eye.


==> Exporting CoreLex as SQL files

This assumes that the corelex-<version>-<category>.tab files have been created.

   $ python3 corelex.py --sql 1.5 n

This creates two files:

   sql/corelex-1.5-basic-types-nouns.sql
   sql/corelex-1.5-lemmas-nouns.sql

These can be imported into the database of the online CoreLex browser. Note that
we do not create a table for CoreLex types.

This does not yet work for verbs.


==> Browsing CoreLex

   $ python3 corelex.py --browse 1.5 n

This does not yet work for verbs.

"""

import sys
import pprint
import textwrap
import io

from wordnet import WordNet, NOUN, VERB, expand
import cltypes
from utils import index_file, data_file, flatten, bold


def get_basic_types(synsets):
    basic_types = set()
    for synset in synsets:
        for bt in synset.basic_types:
            basic_types.add(bt)
    return basic_types


def filter_basic_types(set_of_basic_types, type_relations):
    for (subtype, supertype) in type_relations:
        if subtype in set_of_basic_types and supertype in set_of_basic_types:
            set_of_basic_types.discard(supertype)


def print_usage():
    print("\nUsage:\n",
          "   $ python3 corelex.py --create <version> <category>\n",
          "   $ python3 corelex.py --sql <version> <category>\n",
          "   $ python3 corelex.py --browse <version> <category>\n")


class CoreLex(object):

    def __init__(self, version='1.5', category=NOUN, wordnet=None):
        self.category = expand(category)
        self.version = version
        self.word_index = {}
        self.class_index = {}
        self.corelex_type_to_class = {}
        self.class_to_corelex_type = {}
        self._load_corelex_types()
        if wordnet is not None:
            self._create_from_wordnet(wordnet)
        else:
            self._load_from_file()

    def _create_from_wordnet(self, wordnet):
        self.wordnet = wordnet
        self.wn_lemma_idx = wordnet.lemma_index()
        self.wn_synset_idx = wordnet.synset_index()
        type_relations = self._get_type_relations()
        for lemma in sorted(self.wn_lemma_idx[NOUN].keys()):
            word = self.wordnet.get_noun(lemma)
            synsets = [wordnet.get_noun_synset(synset) for synset in word.synsets]
            basic_types = get_basic_types(synsets)
            filter_basic_types(basic_types, type_relations)
            corelex_class = ' '.join(sorted(basic_types))
            self.word_index[word] = corelex_class
            self.class_index.setdefault(corelex_class, []).append(word)

    def _load_from_file(self):
        data_file = "data/corelex-%s-%ss.tab" % (self.version, self.category)
        with open(data_file) as fh:
            for line in fh:
                corelex_class, words = line.strip().split("\t")
                for word in words.split():
                    self.word_index[word] = corelex_class
                    self.class_index.setdefault(corelex_class, []).append(word)
            print("Loaded %d words and %d CoreLex classes\n"
                  % (len(self.word_index), len(self.class_index)))

    def _load_corelex_types(self):
        for cltype, classes in cltypes.CORELEX_TYPES.items():
            self.corelex_type_to_class[cltype] = classes
            for classs in classes:
                self.class_to_corelex_type[classs] = cltype

    def _get_type_relations(self):
        if self.wordnet.version == '1.5':
            return cltypes.BASIC_TYPES_ISA_RELATIONS_1_5
        return cltypes.BASIC_TYPES_ISA_RELATIONS_3_1

    def write(self, filename):
        print("Writing CoreLex to", filename)
        fh = open(filename, 'w')
        for cl_class in sorted(self.class_index.keys()):
            lemmas = [w.lemma for w in self.class_index[cl_class]]
            fh.write("%s\t%s\n" % (cl_class, ' '.join(lemmas)))

    def write_tables(self):
        basic_types_sql = "sql/corelex-%s-basic-types-%ss.sql" \
                          % (self.version, self.category)
        nouns_sql = "sql/corelex-%s-lemmas-%ss.sql" % (self.version, self.category)
        if self.version == "1.5":
            basic_types = cltypes.BASIC_TYPES_1_5
        else:
            basic_types = cltypes.BASIC_TYPES_3_1
        bt_table = open(basic_types_sql, 'w')
        string_buffer = io.StringIO()
        bt_table.write("INSERT INTO basic_types " +
                       "(basic_type, synset_number, synset_elements) VALUES\n")
        for btype in sorted(basic_types):
            for synset_number, synset_elements in basic_types[btype]:
                string_buffer.write("   ('%s', %d, '%s'),\n"
                                    % (btype, int(synset_number), synset_elements))
        bt_table.write(string_buffer.getvalue()[:-2] + ";\n")
        bt_table.close()
        string_buffer.close()
        noun_table = open(nouns_sql, 'w')
        string_buffer = io.StringIO()
        noun_table.write("INSERT INTO nouns (noun, corelex_type, polysemous_type) VALUES\n")
        for word in self.word_index:
            pclass = self.word_index[word]
            cltype = self.class_to_corelex_type.get(pclass, '-')
            string_buffer.write("   ('%s', '%s', '%s'),\n"
                                % (word.replace("'", r"\'"), cltype, pclass))
        noun_table.write(string_buffer.getvalue()[:-2] + ";\n")
        noun_table.close()
        print("Wrote %d types to file %s" % (len(basic_types), basic_types_sql))
        print("Wrote %d words to file %s\n" % (len(self.word_index), nouns_sql))

    def pp(self, filename):
        print("Writing CoreLex to", filename)
        fh = open(filename, 'w')
        tw = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
        for cl_class in sorted(self.class_index.keys()):
            fh.write("%s\n\n" % cl_class)
            lemmas = [w.lemma for w in self.class_index[cl_class]]
            for line in tw.wrap(' '.join(lemmas)):
                fh.write(line + "\n")
            fh.write("\n")

    def pp_summary(self):
        total_count = 0
        for cl_class in sorted(self.class_index.keys()):
            total_count += len(self.class_index[cl_class])
            print("%s\t%d" % (cl_class, len(self.class_index[cl_class])))
        print("TOTAL\t%d" % total_count)


class CoreLexVerbs(object):

    def __init__(self, wordnet):
        self.wordnet = wordnet
        self.category = wordnet.category
        self.wn_lemma_idx = wordnet.lemma_index()
        self.wn_synset_idx = wordnet.synset_index()
        self.word_index = {}
        self.class_index = {}
        print("Creating CoreLex...")
        for lemma in sorted(self.wn_lemma_idx[VERB].keys()):
            word = self.wordnet.get_verb(lemma)
            synsets = [wordnet.get_synset(VERB, synset) for synset in word.synsets]
            basic_types = get_basic_types(synsets)
            corelex_class = ' * '.join(sorted(basic_types))
            self.word_index[lemma] = corelex_class
            self.class_index.setdefault(corelex_class, []).append(lemma)

    def write(self, filename):
        print("Writing CoreLex to", filename)
        fh = open(filename, 'w')
        for cl_class in sorted(self.class_index.keys()):
            if '*' in cl_class and len(self.class_index[cl_class]) > 4:
                fh.write("%s\t%s\n" % (cl_class, ' '.join(self.class_index[cl_class])))

    def pp(self, filename):
        print("Writing CoreLex to", filename)
        fh = open(filename, 'w')
        tw = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
        for cl_class in sorted(self.class_index.keys()):
            if '*' in cl_class and len(self.class_index[cl_class]) > 4:
                fh.write("%s\n\n" % cl_class)
                for line in tw.wrap(' '.join(self.class_index[cl_class])):
                    fh.write(line + "\n")
                fh.write("\n")


class UserLoop(object):

    # TODO: there may be too many similarities with the wn_browser UserLoop

    MAIN_MODE = 'MAIN_MODE'
    SEARCH_MODE = 'SEARCH_MODE'
    WORD_MODE = 'WORD_MODE'
    SYNSET_MODE = 'SYNSET_MODE'
    STATS_MODE = 'STATS_MODE'

    PROMPT = "\n%s " % bold('>>')


    def __init__(self, corelex):
        self.corelex = corelex
        self.category = self.corelex.category
        self.mode = UserLoop.MAIN_MODE
        self.search_term = None
        self.run()

    def run(self):
        while True:
            if self.mode == UserLoop.MAIN_MODE:
                self.main_mode()
            elif self.mode == UserLoop.SEARCH_MODE:
                self.search_mode()
            elif self.mode == UserLoop.WORD_MODE:
                self.word_mode()

    def main_mode(self):
        self.choices = [('s', 'search ' + self.category), ('q', 'quit') ]
        self.print_choices()
        choice = input(UserLoop.PROMPT)
        if choice == 'q':
            exit()
        elif choice == 's':
            self.mode = UserLoop.SEARCH_MODE
        elif choice == 'a':
            self.mode = UserLoop.STATS_MODE
        else:
            print("Not a valid choice")

    def search_mode(self):
        print('\nEnter a %s to search in CoreLex' % self.category)
        print('Enter return to go to the home screen')
        choice = input(UserLoop.PROMPT)
        if choice == '':
            self.mode = UserLoop.MAIN_MODE
        else:
            choice = choice.replace(' ', '_')
            if choice in self.corelex.word_index:
                self.search_term = choice
                self.mode = UserLoop.WORD_MODE
            else:
                print("Not in CoreLex")

    def word_mode(self):
        corelex_class = self.corelex.word_index[self.search_term]
        self.choices = [('s', 'search'), ('h', 'home'), ('q', 'quit') ]
        print("\n%s -- %s" % (bold(self.search_term), corelex_class))
        self.print_choices()
        choice = input(UserLoop.PROMPT)
        if choice == 'q':
            exit()
        if choice == 'h':
            self.mode = UserLoop.MAIN_MODE
        elif choice == 's':
            self.mode = UserLoop.SEARCH_MODE
        elif choice.startswith('s '):
            self.search_term = choice[2:]
            self.mode = UserLoop.WORD_MODE
        else:
            print("Not a valid choice")

    def print_choices(self):
        print()
        for choice, description in self.choices:
            print("[%s]  %s" % (choice, description))


def test_paths_top_top(wn):
    act = wn.get_synset('00016649')
    compound = wn.get_synset('08907331')
    cat = wn.get_synset('05987089')
    woman = cat.hypernyms()[1]
    for ss in (act, compound, cat, woman):
        print()
        ss.pp_paths_to_top()


def create_corelex_from_wordnet(version, category):
    """Create CoreLex files from a WordNet version for the category specified."""
    if not version in ('1.5', '3.1'):
        exit("ERROR: unsupported wordnet version")
    if not category in ('n', 'v'):
        exit("ERROR: unsupported category")
    wn = WordNet(version, category)    
    if category == 'n':
        print("Adding basic types...")
        wn.add_nominal_basic_types()
        print("Creating CoreLex...")
        cl = CoreLex(category=category, version=version, wordnet=wn)
        cl.write("data/corelex-%s-nouns.tab" % version)
        cl.pp("data/corelex-%s-nouns.txt" % version)
    elif category == 'v':
        wn.add_verbal_basic_types()
        cl = CoreLexVerbs(wn)
        cl.write("data/corelex-%s-verbs.tab" % version)
        cl.pp("data/corelex-%s-verbs.txt" % version)


def scratch(version, category):

    """For whatever I am experimenting with."""

    pass

if __name__ == '__main__':

    if len(sys.argv) < 3:
        print_usage()
        exit()

    version = sys.argv[2]
    category = sys.argv[3]

    if sys.argv[1] == '--create':
        create_corelex_from_wordnet(version, category)

    elif sys.argv[1] == '--sql':
        if category == 'n':
            cl = CoreLex(version=version, category=NOUN)
            cl.write_tables()
        else:
            exit("This does not work for verbs yet")

    elif sys.argv[1] == '--browse':
        if category == 'n':
            cl = CoreLex(category=NOUN)
        else:
            exit("This does not work for verbs yet")
        UserLoop(cl)

    elif sys.argv[1] == '-s':
        scratch(version, category)

    else:
        print_usage()
