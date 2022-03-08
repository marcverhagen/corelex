"""corelex.py

Script to create Corelex from WordNet.

Usage:

   $ python3 corelex.py --create-types <version>
   $ python3 corelex.py --create-relations <version>
   $ python3 corelex.py --export-sql <version>

   where <version> is WordNet version 1.5 or 3.1


==> Creating Corelex files from WordNet

For example, to create Corelex types for lemmas in WordNet 3.1:

   $ python3 corelex.py --create-types 3.1

See the documentation string on TypeGenerator for more information on what files
are created.

Note that the WordNet version is not the same as the Corelex version. In this
case we used WordNet 3.1 and we created Corelex 2.0, which was specified by the
CORELEX_VERSION global variable, which is taken from the ../VERSION file. If we
had used WordNet 1.5 then we would have created Corelex x.x. See the comment
just above the CORELEX_VERSION variable for more on this.


==> Creating basic types relations from WordNet

   $ python3 corelex.py --create-relations <version>

This reads the specified WordNet version and creates two files and a directory:

   data/corelex-<version>-relations-nouns-all.txt
   data/corelex-<version>-relations-nouns-basic-types.txt
   data/corelex-<version>-relations-nouns-basic-types/

See the docstring in create_relations() for a description of what is in these files.

This is experimental and it only works for nouns.


==> Exporting Corelex as SQL files

This assumes that the corelex-<version>-nouns.tab file has been created.

   $ python3 corelex.py --export-sql 3.1

This creates two files:

   sql/corelex-3.1-basic-types-nouns.sql
   sql/corelex-3.1-lemmas-nouns.sql

These can be imported into the database of the online Corelex browser. Note that
we do not create a table for Corelex types.

NOTE: this is broken at the moment

"""

import os
import sys
import textwrap
import io
import itertools
from operator import itemgetter

import cltypes
from wordnet import WordNet, NOUN, VERB, expand
from utils import index_file, data_file, flatten, bold
from utils.statistics import Distribution, ChiSquaredCell, CorelexStatistics
from utils.html import RelationsWriter


### Versioning

# The versioning is a bit tricky. The old legacy Corelex has no number, so we
# just call it version 1.0. It is created from WordNet 1.5 and is similar but
# not identical to the legacy Corelex. There will most likely be no attempts to
# created a verson 1.1. This code also creates version 2.0 and higher. We
# stipulate that Corelex 2.0 is created from WordNet 3.1.

CORELEX_VERSION = open("../VERSION").read().strip()

def get_corelex_version(wn_version):
    return '1.0' if wn_version == '1.5' else CORELEX_VERSION



### Top-level methods that are executed driven by command line options

def create_types(wordnet):
    """Create Corelex types from the given WordNet version and write the results
    to a couple of files."""
    TypeGenerator(wordnet, category=NOUN)
    TypeGenerator(wordnet, category=VERB)


def create_relations(wn, version, category):

    """Collect all relations and then turn them into relations between basic
    types. Store the relations not as individual relations but as a relation
    signature between basic types, where the signature specifies how many
    relations of a given type occur between the two synsets. Output created:

       data/corelex-VERSION-relations-CATEGORY-all.txt
       data/corelex-VERSION-relations-CATEGORY-basic-types.txt
       data/corelex-VERSION-relations-CATEGORY-basic-types/

    The first has all relations as 5-tuples with basic types, pointers and the
    identifiers of the source and target synsets. The second is a summary file
    that has the relation signatures between basic type pairs. The directory
    contains an html export of relation types between basic types. The index
    file in the directory contains a table with only the significant relations
    expressed between basic types, where significant is determined using some
    version of the chi-square test. The rest of the directory contains html
    pages with more comprehensive views of the relations."""

    # collecting relations and relation signatures
    bt_relations = wn.get_all_basic_type_relations(NOUN)
    bt_relation_index = _create_basic_type_relations_summary(bt_relations)

    # writing results
    c = expand(category)
    relations = 'data/corelex-%s-relations-%ss-all.txt' % (CORELEX_VERSION, c)
    basicrels = 'data/corelex-%s-relations-%ss-basic-types.txt' % (CORELEX_VERSION, c)
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
                for k, v in bt_relation_index[pair].items():
                    fh.write("\t%s %s" % (k, v))
                fh.write("\n")

    # collecting and writing relations between basic types
    btr = BasicTypeRelations(wn, category)
    btr.calculate_distribution()
    btr.collect_significant_relations()
    #RelationsWriter(btr).write()
    RelationsWriter(CORELEX_VERSION, btr).write()


def scratch(version):
    """For whatever I am experimenting with."""
    wn = WordNet(version)
    wn.pp_nouns(['abstraction', 'door', 'woman', 'chicken', 'aachen'])


### Utilities

def corelex_type_file(corelex_version='2.0', category='noun', extension='tab'):
    return "data/corelex-%s-types-%ss.%s" % (corelex_version, category, extension)


def get_basic_types(synsets):
    basic_types = set()
    for synset in synsets:
        for bt in synset.basic_types:
            basic_types.add(bt)
    return basic_types


def get_basic_types_ss(synsets):
    """Version of get_basic_types that concatenates the synset with its basic
    type(s). "|" is used as a separator between basic_type and synset."""
    basic_types = set()
    for synset in synsets:
        for bt in synset.basic_types:
            bt_ss = "|".join([bt, synset.id])
            basic_types.add(bt_ss)
    return basic_types


def filter_basic_types(set_of_basic_types, type_relations):
    for (subtype, supertype) in type_relations:
        if subtype in set_of_basic_types and supertype in set_of_basic_types:
            set_of_basic_types.discard(supertype)


def print_usage():
    print("\nUsage:\n",
          "   $ python3 corelex.py --create-type-files <version>\n",
          "   $ python3 corelex.py --btyperels1 <version>\n",
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


class TypeGenerator(object):

    """Generate polysemous types and corelex types for all lemmas. These types can
    then later be loaded into an instance of the Corelex class. It creates the
    following files:

       data/corelex-VERSION-types-nouns.tab
       data/corelex-VERSION-types-nouns.txt
       data/corelex-VERSION-types-verbs.tab
       data/corelex-VERSION-types-verbs.txt

    These files contain mappings from type signatures (which are basic types or
    polysemous types) to lemmas. The tab files can later be used to load Corelex
    and the txt files contain the same data but are easier on the eye.

    Several additional files for nouns and verbs (n, v) are generated by the
    methods create_nv_clpairs(category) and write_nv_clpairs(category):

       data/corelex-2.0-class_pair-nouns-all.tab
       data/corelex-2.0-lemma_pair-nouns-all.tab
       data/corelex-2.0-class_pair_glosses-nouns-all.tab
       data/corelex-2.0-class_pair-verbs-all.tab
       data/corelex-2.0-lemma_pair-verbs-all.tab
       data/corelex-2.0-class_pair_glosses-verbs-all.tab

    These files capture information about pairs of senses for the same lemma
    (noun or verb). Each line of the class_pair files shows a pair of basic_type
    classes, along with all lemmas (and their sense pairs) which map to this
    combination of basic types. The number of lemma/sense pairs for the compound
    basic type is used to sort the lines, such that the most common pairs are
    listed first.

    Each line of the glosses files contains a basic_type pair and one associated
    lemma/sense pair, along with the wordnet glosses for the two senses. This
    allows us to examine the "meanings" associated with senses for the same
    lemma. Like the class_pair files, lines are sorted by the number of
    lemma/sense pairs for the compound basic type. Thus the most common pairs
    appear first. To make it easy to browse the file in an editor, an extra
    field is added to the first line for each new basic_type pair. The field
    consists of /n<sequence number>/. Searching for "/n" will advance you to the
    next basic_type pair. Using the sequence number, you can jump the to the
    first line for the nth pair.

    Each line of the lemma_pair files contains a lemma/sense pair and its
    associated pair of basic types. This allows us to examine all compound
    basic classes for a given lemma.

    """

    def __init__(self, wordnet, category):
        self.wordnet = wordnet
        self.category = expand(category)
        self.version = wordnet.version
        self.cl_version = get_corelex_version(wordnet.version)
        self.lemma_index = {}
        self.class_index = {}
        self.lemma_pair_index = {}
        self.class_pair_index = {}
        self.wn_lemma_idx = self.wordnet.lemma_index()
        self.wn_synset_idx = self.wordnet.synset_index()
        if category == NOUN:
            self.create_noun_types()
            self.write_nouns()
        elif category == VERB:
            self.create_verb_types()
            self.write_verbs()
        self.create_nv_clpairs(category)
        self.write_nv_clpairs(category)

    def corelex_class_pair_file(self, category, extension='tab'):
        return "data/corelex-%s-class_pair-%ss-all.%s" \
            % (self.cl_version, category, extension)

    def corelex_lemma_pair_file(self, category, extension='tab'):
        return "data/corelex-%s-lemma_pair-%ss-all.%s" \
            % (self.cl_version, category, extension)
   
    def corelex_lemma_pair_glosses_file(self, category, extension='tab'):
        return "data/corelex-%s-class_pair_glosses-%ss-all.%s" \
            % (self.cl_version, category, extension)

    def create_noun_types(self):
        self.create_types(NOUN, separator='.')

    def create_verb_types(self):
        self.create_types(VERB, separator=' * ')

    def create_types(self, cat, separator='.'):
        for lemma in sorted(self.wn_lemma_idx[cat].keys()):
            word = self.wordnet.get_word(lemma, cat)
            synsets = [self.wordnet.get_synset(cat, synset) for synset in word.synsets]
            basic_types = get_basic_types(synsets)
            corelex_class = separator.join(sorted(basic_types))
            self.lemma_index[lemma] = corelex_class
            # TODO: we now put the Word in the index, do the lemma instead?
            # TODO: make the index specific to the category
            self.class_index.setdefault(corelex_class, []).append(word)

    def _create_verb_clpairs(self):
        """Create paired types for verbs (PGA)."""
        for lemma in sorted(self.wn_lemma_idx[VERB].keys()):
            
            word = self.wordnet.get_verb(lemma)
            # get all the synsets for the lemma
            synsets = [self.wordnet.get_synset(VERB, synset) for synset in word.synsets]
            # get the list of basic types for all synsets for this lemma
            # Result is s a list of basic_type|synset_id strings.
            l_basic_type = list(get_basic_types_ss(synsets))

            # extract pairs of basic types for the lemma by taking all 
            # combinations of two items in the l_basic_type list.
            l_bt_pair = list(itertools.combinations(l_basic_type, 2))

            # list of class pairs for a lemma
            l_class_pair = []

            # Create names for the class pairs using * between the class names.
            for bt_pair in l_bt_pair:
                # class_pair = ' * '.join(sorted(bt_pair))
                class_sid_pair = sorted(bt_pair)
                # at this point, a class_pair looks like:
                # 'abandon.31.1 give_up.31.0|00614907 * abandon.40.1 give_up.40.0|02232523'
                # It is time to separate the basic_types from the word sense ids,
                # although we will keep this info together for printing out, 
                # along with the lemma.
                class_pair = []
                sid_pair = []
                for class_sid in class_sid_pair:
                    (class_part, sid_part) = class_sid.split("|")
                    class_pair.append(class_part)
                    sid_pair.append(sid_part)
                class_pair_str = " * ".join(class_pair)
                sid_pair_str = "|".join(sid_pair)
                combo_str = class_pair_str + "\t" + lemma + "|" + sid_pair_str
                l_class_pair.append(combo_str)

            # list of class pairs for the lemma
            self.lemma_pair_index[lemma] = l_class_pair

            # The value of the class_pair_index is a list of lemmas
            for class_pair in l_class_pair:
                (class_part, lemma_part) = class_pair.split("\t")
                self.class_pair_index.setdefault(class_part, []).append(lemma_part)

    def create_nv_clpairs(self, category):
        for lemma in sorted(self.wn_lemma_idx[category].keys()):
            if category == VERB:
                word = self.wordnet.get_verb(lemma)
            elif category == NOUN:
                word = self.wordnet.get_noun(lemma)
            else:
                print("[_create_nv_clpairs] failed due to unsupported category")
                continue

            # get all the synsets for the lemma
            synsets = [self.wordnet.get_synset(category, synset) for synset in word.synsets]

            # get the list of basic types for all synsets for this lemma
            # Result is s a list of basic_type|synset_id strings.
            l_basic_type = list(get_basic_types_ss(synsets))

            # extract pairs of basic types for the lemma by taking all 
            # combinations of two items in the l_basic_type list.
            l_bt_pair = list(itertools.combinations(l_basic_type, 2))

            # list of class pairs for a lemma
            l_class_pair = []

            # Create names for the class pairs using * between the class names.
            for bt_pair in l_bt_pair:
                class_sid_pair = sorted(bt_pair)
   
                # At this point, a class_pair looks like:
                # 'abandon.31.1 give_up.31.0|00614907 * abandon.40.1 give_up.40.0|02232523'
                # It is time to separate the basic_types 
                # from the word sense ids,
                # although we will keep this info together for printing out, 
                # along with the lemma.
                class_pair = []
                sid_pair = []
                for class_sid in class_sid_pair:
                    (class_part, sid_part) = class_sid.split("|")
                    class_pair.append(class_part)
                    sid_pair.append(sid_part)
                class_pair_str = " * ".join(class_pair)
                sid_pair_str = "|".join(sid_pair)
                combo_str = class_pair_str + "\t" + lemma + "|" + sid_pair_str

                l_class_pair.append(combo_str)

            # list of class pairs for the lemma
            self.lemma_pair_index[lemma] = l_class_pair

            # The value of the class_pair_index is a list of lemmas
            for class_pair in l_class_pair:
                (class_part, lemma_part) = class_pair.split("\t")
                self.class_pair_index.setdefault(class_part, []).append(lemma_part)


    def _get_type_relations(self):
        if self.wordnet.version == '1.5':
            return cltypes.BASIC_TYPES_ISA_RELATIONS_1_5
        return cltypes.BASIC_TYPES_ISA_RELATIONS_3_1

    def write_nouns(self):
        filename1 = corelex_type_file(self.cl_version, NOUN, 'tab')
        filename2 = corelex_type_file(self.cl_version, NOUN, 'txt')
        self._write_nountypes_tab(filename1)
        self._write_nountypes_txt(filename2)

    def _write_nountypes_tab(self, fname):
        print("Writing", fname)
        with open(fname, 'w') as fh:
            # the index maps type signatures to lists of wordnet.Word instances
            for type_signature in sorted(self.class_index.keys()):
                lemmas = [w.lemma for w in self.class_index[type_signature]]
                fh.write("%s\t%s\n" % (type_signature, ' '.join(lemmas)))

    def _write_nountypes_txt(self, fname):
        print("Writing", fname)
        fh = open(fname, 'w')
        tw = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
        for cl_class in sorted(self.class_index.keys()):
            fh.write("%s\n\n" % cl_class)
            lemmas = [w.lemma for w in self.class_index[cl_class]]
            for line in tw.wrap(' '.join(lemmas)):
                fh.write(line + "\n")
            fh.write("\n")

    def write_verbs(self):
        filename1 = corelex_type_file(self.cl_version, VERB, 'tab')
        filename2 = corelex_type_file(self.cl_version, VERB, 'txt')
        self._write_verbtypes_tab(filename1)
        self._write_verbtypes_txt(filename2)

    def _write_verbtypes_tab(self, fname):
        print("Writing", fname)
        with open(fname, 'w') as fh:
            for type_signature in sorted(self.class_index.keys()):
                lemmas = [w.lemma for w in self.class_index[type_signature]]
                fh.write("%s\t%s\n" % (type_signature, ' '.join(lemmas)))

    def _write_verbtypes_txt(self, fname):
        print("Writing", fname)
        fh = open(fname, 'w')
        tw = textwrap.TextWrapper(width=80, initial_indent="  ", subsequent_indent="  ")
        for cl_class in sorted(self.class_index.keys()):
            # TODO: maybe do same kind of check for the others?
            if '*' in cl_class and len(self.class_index[cl_class]) > 4:
                fh.write("%s\n\n" % cl_class)
                lemmas = [w.lemma for w in self.class_index[cl_class]]
                for line in tw.wrap(' '.join(lemmas)):
                    fh.write(line + "\n")
                fh.write("\n")



        
    """
    Create .tab files for lemmas and paired classes regardless of size of class.  We will
    use this data to create paired_classes, lemmas along with any pairs of basic
    classes they occur in.
    c1_class is of the form "class3 * class2"
    class_index[cl_class] is a list of lemmas which are members of the class.
    We will compute each pair of classes in the c1_class and output a line
    consisting of len(class_index[cl_class]), class_pair, space separated lemmas
    
    """

    """
    def write_verb_pairs(self):
        filename1 = self.corelex_class_pair_file(VERB, 'tab')
        filename2 = self.corelex_lemma_pair_file(VERB, 'tab')
        filename3 = self.corelex_lemma_pair_glosses_file(VERB, 'tab')
        print("Writing", filename1)
        # number of sense_pairs\tbasic_types_class_pair\tlemma|sense1|sense2 ...
        # 2       abandon.31.1 give_up.31.0 * abandon.40.1 give_up.40.0   abandon|00614907|02232523 give_up|00614907|02232523
        
        # create a list sorted by the number of lemma/sense pairs in the class
        l_class_pair = []
        for class_pair in sorted(self.class_pair_index.keys()):
            # Remove restrictions on the size of the class
            ###if '*' in cl_class and len(self.class_index[cl_class]) > 4:
            ###if '*' in class_pair:
            ###fh.write("%s\t%s\n" % (cl_class, ' '.join(self.class_pair_index[cl_class])))
            l_class_pair.append([len(self.class_pair_index[class_pair]), class_pair, self.class_pair_index[class_pair]])

        # sort in place on the length (number of lemma sense pairs)
        l_class_pair.sort(key=itemgetter(0), reverse=True)

        with open(filename1, 'w') as fh:
            ###for cl_class in sorted(self.class_index.keys()):
            #for class_pair in sorted(self.class_pair_index.keys()):
            for class_pair in l_class_pair:
                # Remove restrictions on the size of the class
                ###if '*' in cl_class and len(self.class_index[cl_class]) > 4:
                ###if '*' in class_pair:
                    ###fh.write("%s\t%s\n" % (cl_class, ' '.join(self.class_pair_index[cl_class])))
                #fh.write("%i\t%s\t%s\n" % (len(self.class_pair_index[class_pair]), class_pair, ' '.join(self.class_pair_index[class_pair])))
                fh.write("%i\t%s\t%s\n" % (class_pair[0], class_pair[1], ' '.join(class_pair[2])))

        print("Writing", filename2)
        # lemma|sense1-id|sense2-id\tbasic_types_class_pair
        # The basic types correspond to the senses in the order given.  e.g.,
        # abandon|00614907|00615748       abandon.31.1 give_up.31.0 * leave.31.5
        with open(filename1) as fh1, open(filename2, 'w') as fh2:
            lemma_list = []
            for line in fh1:
                lemma_len, cltype, lemmas = line.strip().split("\t")
                for lemma in lemmas.split():
                    lemma_list.append("%s\t%s\n" % (lemma, cltype))
            for lemma in sorted(lemma_list):
                fh2.write(lemma)

        print("Writing", filename3)
       
        Output: length\basic_class_pair\lemma\sense_offsets\gloss1\gloss2
        e.g., 1503    change.30.0 * change.30.1 alter.30.1 modify.30.a        abate   00245945
|00246175       become less in amount or intensity; "The storm abated"; "The rai
n let up after a few hours"     make less active or intense
       
        with open(filename3, 'w') as fh3:
            # track the last basic_class pair seen.  We will add a field
            # of /n[n]/ at the end if the basic_class changes. [n] is an ascending
            # count.  The idea is to make it easy to search for the next class pair
            # if the file is opened in an editor.  We can search either for /n to get
            # to the next class pair or for /n35/ to get to the start of the 35th class pair.
            last_pair = ""
            count = 1
            for class_pair in l_class_pair:
                length = class_pair[0]
                pair = class_pair[1]
                for lemma_sense_pair in class_pair[2]:
                    lemma, sense1, sense2 = lemma_sense_pair.split("|")
                    senses = "|".join([sense1, sense2])
                    # use the word sense offsets to fetch the gloss for each sense
                    s1_gloss = self.wordnet.get_verb_synset(sense1).gloss
                    s2_gloss = self.wordnet.get_verb_synset(sense2).gloss
                    fh3.write("%i\t%s\t%s\t%s\t%s | %s" % (length, pair, lemma, senses, s1_gloss, s2_gloss))
                    if class_pair != last_pair:
                        # add a marker to the file
                        fh3.write("\t/n%i/\n" % (count))
                        count += 1
                        last_pair = class_pair
                    else:
                        # just terminate the line
                        fh3.write("\n")

    """

    def write_nv_clpairs(self, category):
        filename1 = self.corelex_class_pair_file(category, 'tab')
        filename2 = self.corelex_lemma_pair_file(category, 'tab')
        filename3 = self.corelex_lemma_pair_glosses_file(category, 'tab')
        print("Writing", filename1)
        # number of sense_pairs\tbasic_types_class_pair\tlemma|sense1|sense2 ...
        # 2       abandon.31.1 give_up.31.0 * abandon.40.1 give_up.40.0   abandon|00614907|02232523 give_up|00614907|02232523
        
        # create a list sorted by the number of lemma/sense pairs in the class
        l_class_pair = []
        for class_pair in sorted(self.class_pair_index.keys()):
            # Note no restrictions on the size of the class
            l_class_pair.append([len(self.class_pair_index[class_pair]), class_pair, self.class_pair_index[class_pair]])

        # sort in place on the length (number of lemma sense pairs)
        l_class_pair.sort(key=itemgetter(0), reverse=True)

        with open(filename1, 'w') as fh:
            #for class_pair in sorted(self.class_pair_index.keys()):
            for class_pair in l_class_pair:
                # Note no restrictions on the size of the class
                fh.write("%i\t%s\t%s\n" % (class_pair[0], class_pair[1], ' '.join(class_pair[2])))

        print("Writing", filename2)
        # lemma|sense1-id|sense2-id\tbasic_types_class_pair
        # The basic types correspond to the senses in the order given.  e.g.,
        # abandon|00614907|00615748       abandon.31.1 give_up.31.0 * leave.31.5
        with open(filename1) as fh1, open(filename2, 'w') as fh2:
            lemma_list = []
            for line in fh1:
                lemma_len, cltype, lemmas = line.strip().split("\t")
                for lemma in lemmas.split():
                    lemma_list.append("%s\t%s\n" % (lemma, cltype))
            for lemma in sorted(lemma_list):
                fh2.write(lemma)

        print("Writing", filename3)
        
        # Output is of the form: length\basic_class_pair\lemma\sense_offsets\gloss1\gloss2
        # e.g., 1503    change.30.0 * change.30.1 alter.30.1 modify.30.a        abate
        # 00245945|00246175       become less in amount or intensity; "The storm abated";
        # "The rain let up after a few hours"     make less active or intense
        
        with open(filename3, 'w') as fh3:
            # track the last basic_class pair seen.  We will add a field
            # of /n[n]/ at the end if the basic_class changes. [n] is an ascending
            # count.  The idea is to make it easy to search for the next class pair
            # if the file is opened in an editor.  We can search either for /n to get
            # to the next class pair or for /n35/ to get to the start of the 35th class pair.
            last_pair = ""
            count = 1
            for class_pair in l_class_pair:
                length = class_pair[0]
                pair = class_pair[1]
                for lemma_sense_pair in class_pair[2]:
                    lemma, sense1, sense2 = lemma_sense_pair.split("|")
                    senses = "|".join([sense1, sense2])
                    # use the word sense offsets to fetch the gloss for each sense
                    if category == VERB:
                        s1_gloss = self.wordnet.get_verb_synset(sense1).gloss
                        s2_gloss = self.wordnet.get_verb_synset(sense2).gloss
                    elif category == NOUN:
                        s1_gloss = self.wordnet.get_noun_synset(sense1).gloss
                        s2_gloss = self.wordnet.get_noun_synset(sense2).gloss

                    fh3.write("%i\t%s\t|%s|\t%s\t%s | %s" % (length, pair, lemma, senses, s1_gloss, s2_gloss))
                    if class_pair != last_pair:
                        # add a marker to the file
                        fh3.write("\t/n%i/\n" % count)
                        count += 1
                        last_pair = class_pair
                    else:
                        # just terminate the line
                        fh3.write("\n")


class Corelex(object):

    def __init__(self, version='2.0', category=NOUN, wordnet=None):
        self.category = expand(category)
        self.version = version
        self.stats = CorelexStatistics()
        self.lemma_index = {}
        self.class_index = {}
        self.corelex_types = cltypes.CORELEX_TYPES
        self.polysemous_types = {}
        self._populate_polysemous_types()
        self._load_corelex()

    def __str__(self):
        return "<Corelex cltypes=%d potypes=%d classes=%d lemmas=%d>" \
            % (len(self.corelex_types), len(self.polysemous_types),
               len(self.class_index), len(self.lemma_index))

    def _populate_polysemous_types(self):
        """Create mappings from polysemous type to corelx types, basically
        inverting the corelex_types index."""
        for cltype, ptypes in self.corelex_types.items():
            for ptype in ptypes:
                self.polysemous_types[ptype] = cltype
        #self.pp_polysemous_types()

    def _load_corelex(self):
        # this file has each lemma mapped to a basic type or polysemous type
        data_file = "data/corelex-%s-lemmas-%ss.tab" % (self.version, self.category)
        with open(data_file) as fh:
            for line in fh:
                lemma, type_signature = line.strip().split("\t")
                corelex_type = self.polysemous_types.get(type_signature, '-')
                self.stats.update(lemma, type_signature, corelex_type)
                self.lemma_index[lemma] = (corelex_type, type_signature)
        self.stats.pp()

    def export_sql(self):
        btypes_sql = "sql/corelex-%s-btypes-%ss.sql" % (self.version, self.category)
        nouns_sql = "sql/corelex-%s-lemmas-%ss.sql" % (self.version, self.category)
        basic_types = cltypes.get_basic_types(self.version)
        # Collecting basic types in a buffer which makes it easy to change the
        # end of the final insert from a comma into a semi-colon
        btypes_buffer = io.StringIO()
        btypes_buffer.write("INSERT INTO basic_types " +
                            "(basic_type, synset_number, synset_elements) VALUES\n")
        for btype in sorted(basic_types):
            for synset_number, synset_elements in basic_types[btype]:
                btypes_buffer.write("   ('%s', %d, '%s'),\n"
                                    % (btype, int(synset_number), synset_elements))
        with open(btypes_sql, 'w') as fh:
            fh.write(btypes_buffer.getvalue()[:-2] + ";\n")
        noun_table = open(nouns_sql, 'w')
        string_buffer = io.StringIO()
        noun_table.write("INSERT INTO nouns (noun, corelex_type, type_signature) VALUES\n")
        for lemma in self.lemma_index:
            cltype, potype = self.lemma_index.get(lemma, ('-', '-'))
            string_buffer.write("   ('%s', '%s', '%s'),\n"
                                % (lemma.replace("'", r"\'"), cltype, potype))
        noun_table.write(string_buffer.getvalue()[:-2] + ";\n")
        noun_table.close()
        print("Wrote %d basic types to %s" % (len(basic_types), btypes_sql))
        print("Wrote %d lemmas to %s\n" % (len(self.lemma_index), nouns_sql))

    def pp_summary(self):
        total_count = 0
        for cl_class in sorted(self.class_index.keys()):
            total_count += len(self.class_index[cl_class])
            print("%s\t%d" % (cl_class, len(self.class_index[cl_class])))
        print("TOTAL\t%d" % total_count)

    def pp_polysemous_types(self):
        for ptype in sorted(self.polysemous_types):
            print("[%-20s ==>  %s" % (ptype + ']', self.polysemous_types[ptype]))


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
        fname = ("data/corelex-%s-relations-%ss-basic-types.txt"
                 % (get_corelex_version(self.version), expand(self.category)))
        for line in open(fname):
            fields = line.strip().split("\t")
            types = fields.pop(0)
            rel = tuple(types.split('-'))
            pointer_dictionary = {}
            for field in fields:
                pointer, count = field.split()
                # use only holonyms and meronyms, not the domain relations
                # if pointer[0] in ('%', '#'):
                pointer_dictionary[pointer] = int(count)
            # print(pointer_dictionary)
            self.btrels1[rel] = pointer_dictionary

    def _read_relations(self):
        """Read all the relations from the data/corelex-VERSION-CATEGORY-relations.txt
        file and return them as a dictionary indexed on the basic type pair."""
        fname = ("data/corelex-%s-relations-%ss-all.txt"
                 % (get_corelex_version(self.version), expand(self.category)))
        with open(fname) as fh:
            for line in fh:
                fields = line.strip().split("\t")
                bt1, pointer, bt2, ss1_id, ss2_id = fields
                basic_rel = "%s-%s" % (bt1, bt2)
                ss1 = self.wordnet.get_noun_synset(ss1_id)
                ss2 = self.wordnet.get_noun_synset(ss2_id)
                # if pointer[0] in ('#', '%'):
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


if __name__ == '__main__':

    flag = sys.argv[1]
    version = sys.argv[2]

    if flag == '--create-types':
        wn = WordNet(version, add_basic_types=True)
        create_types(wn)

    elif flag == '--create-relations':
        wn = WordNet(version, add_basic_types=True)
        create_relations(wn, version, 'n')

    elif flag == '--export-sql':
        cl = Corelex(version=version, category='n')
        print(cl)
        cl.export_sql()

    elif flag == '-s':
        scratch(version)

    else:
        print_usage()
