"""corelex.py

To create  CoreLex from WordNet you want to do something like

>>> create_from_wordnet('3.1', 'noun')

This involves creating a class instance with an instance of WordNet as the
argument:

>>> wn = WordNet('3.1', 'noun')
>>> wn.add_basic_types(NOUN)
>>> cl = CoreLex(wn)

And after this you print files to the data directory.

You can alos just load CoreLex from the data directory:

>>> cl = CoreLex()


"""

import sys
import pprint
import textwrap
import io

from wordnet import WordNet, NOUN, VERB
import cltypes
from utils import index_file, data_file, flatten, bold


def filter_basic_types(set_of_basic_types, type_relations):
    for (subtype, supertype) in type_relations:
        if subtype in set_of_basic_types and supertype in set_of_basic_types:
            set_of_basic_types.discard(supertype)


class CoreLex(object):

    # TODO: distinguish between version that creates corelex from wordnet and
    # version that reads corelex from files (now we only have the former)

    def __init__(self, category=NOUN, wordnet=None):
        self.category = category
        self.word_index = {}
        self.class_index = {}
        self.corelex_type_to_class = {}
        self.class_to_corelex_type = {}
        self._load_corelex_types()
        if wordnet is not None:
            self.create_from_wordnet(wordnet)
        else:
            self.load_from_file()

    def create_from_wordnet(self, wordnet):
        self.wordnet = wordnet
        print("Creating CoreLex...")
        type_relations = self._get_type_relations()
        for word in sorted(wordnet.lemma_idx[NOUN].keys()):
            synsets = wordnet.lemma_idx[NOUN][word]
            synsets = [wordnet.get_noun_synset(synset) for synset in synsets]
            basic_types = set()
            for synset in synsets:
                path = synset.paths_to_top()
                synsets = flatten(path)
                for synset in synsets:
                    if synset.basic_type:
                        basic_types.add(synset.basic_type)
            filter_basic_types(basic_types, type_relations)
            corelex_class = ' '.join(sorted(basic_types))
            self.word_index[word] = corelex_class
            self.class_index.setdefault(corelex_class, []).append(word)

    def load_from_file(self):
        # TODO: cannot have the version hard-coded
        for line in open("data/corelex-%ss-3.1.tab" % self.category):
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
        print("Writing CoreLex compactly to", filename)
        fh = open(filename, 'w')
        for cl_class in sorted(self.class_index.keys()):
            fh.write("%s\t%s\n" % (cl_class, ' '.join(self.class_index[cl_class])))

    def write_tables(self, basic_types_sql_file, nouns_sql_file):
        #basic_types = cltypes.BASIC_TYPES_1_5
        #if self.wordnet.version == '3.1':
        #    basic_types = cltypes.BASIC_TYPES_3_1
        basic_types = cltypes.BASIC_TYPES_3_1
        bt_table = open(basic_types_sql_file, 'w')
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
        noun_table = open(nouns_sql_file, 'w')
        string_buffer = io.StringIO()
        noun_table.write("INSERT INTO nouns (noun, corelex_type, polysemous_type) VALUES\n")
        for word in self.word_index:
            pclass = self.word_index[word]
            cltype = self.class_to_corelex_type.get(pclass, '-')
            #noun_table.write("%s\t%s\t%s\n" % (word, cltype, pclass))
            string_buffer.write("   ('%s', '%s', '%s'),\n" % (word.replace("'", r"\'"), cltype, pclass))
        noun_table.write(string_buffer.getvalue()[:-2] + ";\n")
        print("Wrote %d types to file %s" % (len(basic_types), basic_types_sql_file))
        print("Wrote %d words to file %s\n" % (len(self.word_index), nouns_sql_file))

    def pp(self, filename):
        print("Writing CoreLex verbosely to", filename)
        fh = open(filename, 'w')
        tw = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
        for cl_class in sorted(self.class_index.keys()):
            fh.write("%s\n\n" % cl_class)
            for line in tw.wrap(' '.join(self.class_index[cl_class])):
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
        self.word_index = {}
        self.class_index = {}
        print("Creating CoreLex...")
        for word in sorted(wordnet.lemma_idx[VERB].keys()):
            synsets = wordnet.lemma_idx[VERB][word]
            synsets = [wordnet.get_synset(VERB, synset) for synset in synsets]
            basic_types = set()
            for synset in synsets:
                path = synset.paths_to_top()
                synsets = flatten(path)
                for synset in synsets:
                    if synset.basic_type:
                        basic_types.add(synset.basic_type)
            corelex_class = ' * '.join(sorted(basic_types))
            self.word_index[word] = corelex_class
            self.class_index.setdefault(corelex_class, []).append(word)

    def write(self, filename):
        print("Writing CoreLex compactly to", filename)
        fh = open(filename, 'w')
        for cl_class in sorted(self.class_index.keys()):
            if '*' in cl_class and len(self.class_index[cl_class]) > 4:
                fh.write("%s\t%s\n" % (cl_class, ' '.join(self.class_index[cl_class])))

    def pp(self, filename):
        print("Writing CoreLex verbosely to", filename)
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
            print()
            if self.mode == UserLoop.MAIN_MODE:
                self.main_mode()
            elif self.mode == UserLoop.SEARCH_MODE:
                self.search_mode()
            elif self.mode == UserLoop.WORD_MODE:
                self.word_mode()

    def main_mode(self):
        self.choices = [('s', 'search ' + self.category), ('a', 'show statistics'), ('q', 'quit') ]
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
        #self.mapping = list(enumerate(self.synsets))
        #self.mapping_idx = dict(self.mapping)
        self.choices = [('s', 'search'), ('h', 'home'), ('q', 'quit') ]
        print("%s -- %s\n" % (bold(self.search_term), corelex_class))
        #for count, synset in self.mapping:
        #    print("[%d]  %s" % (count, synset))
        self.print_choices()
        choice = input(UserLoop.PROMPT)
        if choice == 'q':
            exit()
        if choice == 'h':
            self.mode = UserLoop.MAIN_MODE
        elif choice == 's':
            self.mode = UserLoop.SEARCH_MODE
        #elif choice.isdigit() and int(choice) in [m[0] for m in self.mapping]:
        #    # displaying a synset
        #    self.synset = self.mapping_idx[int(choice)]
        #    self.mode = UserLoop.SYNSET_MODE
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


def create_from_wordnet(wn_version, category):
    """Create CoreLex files from a WordNet for the category specified."""

    wn = WordNet(wn_version, category)

    if category == NOUN:
        wn.add_basic_types(NOUN)
        cl = CoreLex(category, wn)
        cl.write("data/corelex-nouns-%s.tab" % wn_version)
        cl.pp("data/corelex-nouns-%s.txt" % wn_version)
        #cl.write_tables('sql/basic_types.sql', 'sql/nouns.sql')

    elif category == VERB:
        wn.set_verbal_basic_types()
        cl = CoreLexVerbs(wn)
        cl.write("data/corelex-verbs-%s.tab" % wn_version)
        cl.pp("data/corelex-verbs-%s.txt" % wn_version)


if __name__ == '__main__':

    wn_version = sys.argv[1]
    category = sys.argv[2]

    wn_dir = None

    if not wn_version in ('1.5', '3.0', '3.1'):
        exit("ERROR: unsupported wordnet version")

    #create_from_wordnet(wn_version, category)

    cl = CoreLex(category)
    cl.write_tables('sql/basic_types.sql', 'sql/nouns.sql')


    #UserLoop(cl)
