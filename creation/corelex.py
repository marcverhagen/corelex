"""corelex.py

Script to create CoreLex from WordNet.

Usage:

   $ python3 corelex.py --create-lemma-to-cltype-files <version>
   $ python3 corelex.py --btyperels1 <version> <category>
   $ python3 corelex.py --btyperels2 <version> <category>
   $ python3 corelex.py --browse <version> <category>
   $ python3 corelex.py --sql <version>

   where <version> is 1.5 or 3.1 and <category> is n or v


==> Creating CoreLex files from WordNet

For example, to create CoreLex types for lemmas in WordNet 1.5:

   $ python3 corelex.py --create-lemma-to-cltype-files 1.5

This loads WordNet 1.5 using the wordnet.py module and then creates four files:

   data/corelex-1.5-nouns.tab
   data/corelex-1.5-nouns.txt
   data/corelex-1.5-verbs.tab
   data/corelex-1.5-verbs.txt

The tab files can later be used to load CoreLex, the txt files contain the same
data but are easier on the eye.


==> Creating basic types relations from WordNet

   $ python3 corelex.py --btyperels1 <version> <category>
   $ python3 corelex.py --btyperels2 <version> <category>

The first invocation reads the specified WordNet version and creates two files:

   data/corelex-<version>-<category>s-basic-type-relations.txt
   data/corelex-<version>-<category>s-relations.txt

The first one contains counts of the relations expressed between basic types and
the second contains all relations with both the basic types and the identifiers
for the source and target synsets.

The second invocation reads the results of the first invocation and creates a
directory with html files:

   directory data/corelex-<version>-<category>s-basic-type-relations/

The index file in the directory contains a table with only the significant
relations expressed between basic types, where significant is determined using
some version of the chi-square test. The rest of the directory contains html
pages with more comprehensive views of the relations.

This does not yet work for verbs.


==> Browsing CoreLex

   $ python3 corelex.py --browse 1.5 n

This is now mostly deprecated because the wordnet browser in browse.py
basically shows all information shown by the corelex browser.

This does not yet work for verbs.


==> Exporting CoreLex as SQL files

This assumes that the corelex-<version>-nouns.tab file has been created.

   $ python3 corelex.py --sql 1.5

This creates two files:

   sql/corelex-1.5-basic-types-nouns.sql
   sql/corelex-1.5-lemmas-nouns.sql

These can be imported into the database of the online CoreLex browser. Note that
we do not create a table for CoreLex types.

This does not yet work for verbs.

"""

import os
import sys
import pprint
import textwrap
import io

from wordnet import WordNet, NOUN, VERB, POINTER_SYMBOLS, expand
import cltypes
from utils import index_file, data_file, flatten, bold
from statistics import Distribution, ChiSquaredCell


### Top-level methods that are executed driven by user flags

def create_lemma_to_cltype_files(wordnet_version):
    """Create CoreLex files from the given WordNet version."""
    wn = WordNet(wordnet_version)
    wn.add_basic_types()
    CoreLexTypeGenerator(wn, category=NOUN)
    CoreLexTypeGenerator(wn, category=VERB)


def create_basic_type_relations1(version, category):

    """Collect all relations and then turn them into relations between basic
    types. Store the relations not as individual relations but as a relation
    signature between basic types, where the signature specifies how many
    relations of a given type occur between the two synsets. Files created:

       data/corelex-VERSION-CATEGORY-relations.txt
       data/corelex-VERSION-CATEGORY-basic-type-relations.txt

    The first has all relations as 5-tuples with basic types, pointers and the
    identifiers of the source and target synsets. The second is a summary file
    that has the relation signatures between basic type pairs.

    """

    # collecting relations and relation signatures
    wn = WordNet(version)
    wn.add_basic_types()
    bt_relations = wn.get_all_basic_type_relations(NOUN)
    bt_relation_index = _create_basic_type_relations_summary(bt_relations)

    # writing results
    c = expand(category)
    relations = 'data/corelex-%s-%ss-relations.txt' % (version, c)
    basicrels = 'data/corelex-%s-%ss-basic-type-relations.txt' % (version, c)
    with open(relations, 'w') as fh:
        for bt_relation in bt_relations:
            source = bt_relation[3]
            target = bt_relation[4]
            fh.write("%s\t%s\t%s\n"
                     % ("\t".join(bt_relation[:3]), source.id, target.id))

    with open(basicrels, 'w') as fh:
        for pair in sorted(bt_relation_index.keys()):
            if pair[0] != pair[1]:
                fh.write("%s-%s" % (pair[0], pair[1]))
                for k,v in bt_relation_index[pair].items():
                    fh.write("\t%s %s" % (k, v))
                fh.write("\n")


def create_basic_type_relations2(version, category):
    wn = WordNet(version)
    wn.add_basic_types()
    btr = BasicTypeRelations(wn, category)
    btr.calculate_distribution()
    btr.collect_significant_relations()
    rw = RelationsWriter(btr)
    rw.write()
    

def scratch(version, category):

    """For whatever I am experimenting with."""

    wn = WordNet(version, category)
    wn.pp_nouns(['abstraction', 'door', 'woman', 'chicken', 'aachen'])


### Utilities

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
          "   $ python3 corelex.py --create-lemma-to-cltype-files <version>\n",
          "   $ python3 corelex.py --btyperels1 <version> <category>\n",
          "   $ python3 corelex.py --btyperels2 <version> <category>\n",
          "   $ python3 corelex.py --browse <version> <category>\n",
          "   $ python3 corelex.py --sql <version> <category>\n")


def test_paths_top_top(wn):
    act = wn.get_synset('00016649')
    compound = wn.get_synset('08907331')
    cat = wn.get_synset('05987089')
    woman = cat.hypernyms()[1]
    for ss in (act, compound, cat, woman):
        print()
        ss.pp_paths_to_top()


def _create_basic_type_relations_summary(bt_relations):
    bt_relation_index = {}
    for bt_relation in bt_relations:
        pair = (bt_relation[0], bt_relation[2])
        rel = bt_relation[1]
        if pair not in bt_relation_index:
            bt_relation_index[pair] = {}
        bt_relation_index[pair][rel] = bt_relation_index[pair].get(rel, 0) + 1
    return bt_relation_index


class CoreLexTypeGenerator(object):

    """This class is used to generated the mappings from lemmas to polysemous types
    and corelex types. These mappings can then later be loaded into an instance of
    the CoreLex class. It creates the following files:

       data/corelex-VERSION-nouns.tab
       data/corelex-VERSION-nouns.txt
       data/corelex-VERSION-verbs.tab
       data/corelex-VERSION-verbs.txt

    The tab files are read into CoreLex and the txt files contain the same data
    but more pleasant to the eye.

    """

    def __init__(self, wordnet, category):
        self.wordnet = wordnet
        self.category = expand(category)
        self.version = wordnet.version
        self.lemma_index = {}
        self.class_index = {}
        self.wn_lemma_idx = self.wordnet.lemma_index()
        self.wn_synset_idx = self.wordnet.synset_index()
        if category == NOUN:
            self._create_noun_cltypes()
            self.write_nouns()
            self.pp_nouns()
        elif category == VERB:
            self._create_verb_cltypes()
            self.write_verbs()
            self.pp_verbs()

    def write(self):
        if self.category == NOUN:
            self.write_nouns()
            self.pp_nouns()
            
    def corelex_file(self, category, extension='tab'):
        return "data/corelex-%s-%ss.%s" % (self.version, category, extension)

    def _create_noun_cltypes(self):
        type_relations = self._get_type_relations()
        for lemma in sorted(self.wn_lemma_idx[NOUN].keys()):
            word = self.wordnet.get_noun(lemma)
            synsets = [self.wordnet.get_noun_synset(synset) for synset in word.synsets]
            basic_types = get_basic_types(synsets)
            corelex_class = ' '.join(sorted(basic_types))
            self.lemma_index[word] = corelex_class
            self.class_index.setdefault(corelex_class, []).append(word)

    def _create_verb_cltypes(self):
        for lemma in sorted(self.wn_lemma_idx[VERB].keys()):
            word = self.wordnet.get_verb(lemma)
            synsets = [self.wordnet.get_synset(VERB, synset) for synset in word.synsets]
            basic_types = get_basic_types(synsets)
            corelex_class = ' * '.join(sorted(basic_types))
            self.lemma_index[lemma] = corelex_class
            self.class_index.setdefault(corelex_class, []).append(lemma)

    def _get_type_relations(self):
        if self.wordnet.version == '1.5':
            return cltypes.BASIC_TYPES_ISA_RELATIONS_1_5
        return cltypes.BASIC_TYPES_ISA_RELATIONS_3_1

    def write_nouns(self):
        filename = self.corelex_file(NOUN, 'tab')
        print("Writing CoreLex to", filename)
        fh = open(filename, 'w')
        for cl_class in sorted(self.class_index.keys()):
            lemmas = [w.lemma for w in self.class_index[cl_class]]
            fh.write("%s\t%s\n" % (cl_class, ' '.join(lemmas)))

    def pp_nouns(self):
        filename = self.corelex_file(NOUN, 'txt')
        print("Writing CoreLex to", filename)
        fh = open(filename, 'w')
        tw = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
        for cl_class in sorted(self.class_index.keys()):
            fh.write("%s\n\n" % cl_class)
            lemmas = [w.lemma for w in self.class_index[cl_class]]
            for line in tw.wrap(' '.join(lemmas)):
                fh.write(line + "\n")
            fh.write("\n")

    def write_verbs(self):
        filename = self.corelex_file(VERB, 'tab')
        print("Writing CoreLex to", filename)
        fh = open(filename, 'w')
        for cl_class in sorted(self.class_index.keys()):
            if '*' in cl_class and len(self.class_index[cl_class]) > 4:
                fh.write("%s\t%s\n" % (cl_class, ' '.join(self.class_index[cl_class])))

    def pp_verbs(self):
        filename = self.corelex_file(VERB, 'txt')
        print("Writing CoreLex to", filename)
        fh = open(filename, 'w')
        tw = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
        for cl_class in sorted(self.class_index.keys()):
            if '*' in cl_class and len(self.class_index[cl_class]) > 4:
                fh.write("%s\n\n" % cl_class)
                for line in tw.wrap(' '.join(self.class_index[cl_class])):
                    fh.write(line + "\n")
                fh.write("\n")


    
class CoreLex(object):

    def __init__(self, version='3.1', category=NOUN, wordnet=None):
        self.category = expand(category)
        self.version = version
        self.lemma_index = {}
        self.class_index = {}
        self.corelex_type_to_class = {}
        self.class_to_corelex_type = {}
        self._load_corelex_types()
        self._load_corelex()

    def _load_corelex_types(self):
        """Load the corelex types from the cltypes module."""
        for cltype, classes in cltypes.CORELEX_TYPES.items():
            self.corelex_type_to_class[cltype] = classes
            for class_ in classes:
                self.class_to_corelex_type[class_] = cltype

    def _load_corelex(self):
        data_file = "data/corelex-%s-%ss.tab" % (self.version, self.category)
        with open(data_file) as fh:
            for line in fh:
                corelex_class, words = line.strip().split("\t")
                for word in words.split():
                    self.lemma_index[word] = corelex_class
                    self.class_index.setdefault(corelex_class, []).append(word)
            print("Loaded %d words and %d CoreLex classes\n"
                  % (len(self.lemma_index), len(self.class_index)))

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
        for word in self.lemma_index:
            pclass = self.lemma_index[word]
            cltype = self.class_to_corelex_type.get(pclass, '-')
            string_buffer.write("   ('%s', '%s', '%s'),\n"
                                % (word.replace("'", r"\'"), cltype, pclass))
        noun_table.write(string_buffer.getvalue()[:-2] + ";\n")
        noun_table.close()
        print("Wrote %d types to file %s" % (len(basic_types), basic_types_sql))
        print("Wrote %d words to file %s\n" % (len(self.lemma_index), nouns_sql))

    def pp_summary(self):
        total_count = 0
        for cl_class in sorted(self.class_index.keys()):
            total_count += len(self.class_index[cl_class])
            print("%s\t%d" % (cl_class, len(self.class_index[cl_class])))
        print("TOTAL\t%d" % total_count)



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
            if choice in self.corelex.lemma_index:
                self.search_term = choice
                self.mode = UserLoop.WORD_MODE
            else:
                print("Not in CoreLex")

    def word_mode(self):
        corelex_class = self.corelex.lemma_index[self.search_term]
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


class BasicTypeRelations(object):

    def __init__(self, wordnet, category):
        self.wordnet = wordnet
        self.version = wordnet.version
        self.category = category
        self.btrels1 = {}                  # basic type relations
        self.btrels2 = {}                  # significant basic type relations
        self.allrels = {}                  # all relations
        self._read_basic_type_relations()  # fill in self.btrels1
        self._read_relations()             # fill in self.allrels

    def _read_basic_type_relations(self):
        """Read the relations between basic types from file and return the relations as
        a dictionary. Keys are pairs of basic relations, values are dictionaries of
        pointer symbols and their counts."""
        fname = "data/corelex-%s-%ss-basic-type-relations.txt" \
                % (self.version, expand(self.category))
        for line in open(fname):
            fields = line.strip().split("\t")
            types = fields.pop(0)
            rel = tuple(types.split('-'))
            pointer_dictionary = {}
            for field in fields:
                pointer, count = field.split()
                pointer_dictionary[pointer] = int(count)
            self.btrels1[rel] = pointer_dictionary

    def _read_relations(self):
        """Read all the relations from the data/corelex-VERSION-CATEGORY-relations.txt
        file and return them as a dictionary indexed on the basic type pair."""
        fname = "data/corelex-%s-%ss-relations.txt" % (self.version, expand(self.category))
        with open(fname) as fh:
            for line in fh:
                fields = line.strip().split("\t")
                bt1, pointer, bt2, ss1_id, ss2_id = fields
                basic_rel = "%s-%s" % (bt1, bt2)
                ss1 = self.wordnet.get_noun_synset(ss1_id)
                ss2 = self.wordnet.get_noun_synset(ss2_id)
                self.allrels.setdefault(basic_rel, []).append([bt1, pointer, bt2, ss1, ss2])

    def calculate_distribution(self):
        """Return a distribution of all relations in all basic type pairs. This will be
        used to compare the distributions of individual pairs to."""
        self.distribution = Distribution('ALL')
        for pointers in self.btrels1.values():
            for pointer, count in pointers.items():
                self.distribution.add(pointer, count)
        self.distribution.finish()

    def collect_significant_relations(self):
        """Return a dictionary indexed on type pairs with for each pair the relations
        that occur significantly more often than in WordNet overall."""
        for pair, pointers in self.btrels1.items():
            di = Distribution('-'.join(pair))
            for pointer, count in pointers.items():
                di.add(pointer, count)
            di.finish()
            di.chi_squared(self.distribution)
            if di.observations < 20 or di.X2_statistic < 100:
                continue
            cells = []
            for cell in di.X2_table.values():
                if cell.observed > cell.expected and cell.component() > 200:
                    cells.append(cell)
            if cells:
                self.btrels2[pair] = cells



class RelationsWriter(object):

    def __init__(self, basic_type_relations):
        self.btr = basic_type_relations
        self.html_dir = "data/corelex-%s-%ss-basic-type-relations" \
                        % (self.btr.version, expand(self.btr.category))
        self.rels_dir = os.path.join(self.html_dir, 'rels')
        self.index_file = os.path.join(self.html_dir, "index.html")
        self.basic_types = cltypes.get_basic_types(self.btr.version)

    def write(self):
        self._ensure_directories()
        with open(self.index_file, 'w') as fh:
            fh.write("<html>\n");
            self._write_head(fh)
            fh.write("<body>\n");
            fh.write("<table cellpadding=5 cellspacing=0 border=1>\n");
            fh.write("<tr align=center>\n");
            fh.write("  <td>&nbsp;</td>\n");
            categories = self.btr.distribution.get_categories()
            for cat in categories:
                fh.write("  <td width=30>%s</td>\n" % cat);
            fh.write("</tr>\n");
            for pair in sorted(self.btr.btrels2):
                cells = self.btr.btrels2[pair]
                cell_categories = set([cell.category for cell in cells])
                bt1, bt2 = pair
                fh.write("<tr align=center>\n")
                name = "%s-%s" % (bt1, bt2)
                fh.write("  <td align=left><a href=rels/%s.html>%s</a></td>\n" % (name, name))
                #self._write_pair_description(fh, bt1, bt2)
                #fh.write("  </td>\n")
                for cat in categories:
                    val = "&check;" if cat in cell_categories else "&nbsp;"
                    fh.write("  <td>%s</td>\n" % val);
                fh.write("</tr>\n")
                self._write_relation(bt1, bt2, name, cells)
            fh.write("</table>\n");

    def _write_head(self, fh):
        fh.write("<head>\n")
        fh.write("<style>\n")
        fh.write("a:link { text-decoration: none; }\n")
        fh.write("a:visited { text-decoration: none; }\n")
        fh.write("a:hover { text-decoration: underline; }\n")
        fh.write("a:active { text-decoration: underline; }\n")
        fh.write(".blue { color: blue; }\n")
        fh.write(".green { color: green; }\n")
        fh.write("dd { margin-bottom: 20px; }\n")
        fh.write("</style>\n</head>\n")

    def _ensure_directories(self):
        if not os.path.exists(self.html_dir):
            os.makedirs(self.html_dir)
            os.makedirs(self.rels_dir)

    def _write_relation(self, bt1, bt2, name, cells):
        fname = os.path.join(self.rels_dir, name + '.html')
        with open(fname, 'w') as fh:
            fh.write("<html>\n")
            self._write_head(fh)
            fh.write("<body>\n")
            fh.write("<h2>%s-%s</h2>\n" % (bt1, bt2))
            self._write_pair_description(fh, bt1, bt2)
            fh.write('<p>Relations:')
            for cell in cells:
                fh.write(" [<a href=#%s>%s</a>]"
                         % (cell.category, POINTER_SYMBOLS.get(cell.category)))
            fh.write('</p>')
            for cell in cells:
                fh.write("<a name=%s></a>\n" % cell.category)
                fh.write("<p>&bullet; %s  (%s)</p>\n"
                         % (POINTER_SYMBOLS.get(cell.category), cell.category))
                rels = self.btr.allrels[name]
                grouped_rels = {}
                for rel in rels:
                    # If we skip this test we get a problem when, for example,
                    # we have <ss1 #s ss2> and <ss2 %s ss1>. In that case the
                    # results will also show <ss1 %s ss2> and <ss2 #s ss1>.
                    if rel[1] == cell.category:
                        source = rel[3]
                        target = rel[4]
                        grouped_rels.setdefault(source.id, [source, []])
                        grouped_rels[source.id][1].append(target)
                fh.write("<blockquote>\n<dl>\n")
                for synset_id in grouped_rels:
                    source, targets = grouped_rels[synset_id]
                    fh.write("  <dt>%s</dt>\n" % source.as_html())
                    fh.write("  <dd>\n")
                    for target in targets:
                        fh.write("%s<br/>" % target.as_html())
                    fh.write("  </dd>\n")
                fh.write("</dl>\n</blockquote>\n")

    def _write_pair_description(self, fh, bt1, bt2):
        fh.write('<p>{')
        for offset, synset in self.basic_types.get(bt1):
            fh.write(' %s' % synset)
        fh.write(' } &bullet; {')
        for offset, synset in self.basic_types.get(bt2):
            fh.write(' %s' % synset)
        fh.write('}</p>\n')



if __name__ == '__main__':

    flag = sys.argv[1]
    version = sys.argv[2]
    if len(sys.argv) > 3:
        category = sys.argv[3]

    if flag == '--create-lemma-to-cltype-files':
        create_lemma_to_cltype_files(version)

    elif flag == '--sql':
        if category == 'n':
            cl = CoreLex(version=version, category=NOUN)
            cl.write_tables()
        else:
            exit("This does not work for verbs yet")

    elif flag == '--btyperels1':
        if category == 'n':
            create_basic_type_relations1(version, category)
        else:
            exit("This does not work for verbs yet")

    elif flag == '--btyperels2':
        if category == 'n':
            create_basic_type_relations2(version, category)
        else:
            exit("This does not work for verbs yet")

    elif flag == '--browse':
        if category == 'n':
            cl = CoreLex(category=NOUN)
        else:
            exit("This does not work for verbs yet")
        UserLoop(cl)

    elif flag == '-s':
        scratch(version, category)

    else:
        print_usage()
