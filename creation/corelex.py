
import sys
import pprint
import textwrap

from wordnet import WordNet, NOUN, VERB
import cltypes
from utils import flatten


def filter_basic_types(set_of_basic_types, type_relations):
    for (subtype, supertype) in type_relations:
        if subtype in set_of_basic_types and supertype in set_of_basic_types:
            set_of_basic_types.discard(supertype)


class CoreLex(object):

    # TODO: distinguish between version that creates corelex from wordnet and
    # version that reads corelex from files (now we only have the former)

    def __init__(self, wordnet):
        self.wordnet = wordnet
        self.word_index = {}
        self.class_index = {}
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

    def _get_type_relations(self):
        if self.wordnet.version == '1.5':
            return cltypes.BASIC_TYPES_ISA_RELATIONS_1_5
        return cltypes.BASIC_TYPES_ISA_RELATIONS_3_1

    def write(self, filename):
        print("Writing CoreLex compactly to", filename)
        fh = open(filename, 'w')
        for cl_class in sorted(self.class_index.keys()):
            fh.write("%s\t%s\n" % (cl_class, ' '.join(self.class_index[cl_class])))

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


def test_paths_top_top(wn):
    act = wn.get_synset('00016649')
    compound = wn.get_synset('08907331')
    cat = wn.get_synset('05987089')
    woman = cat.hypernyms()[1]
    for ss in (act, compound, cat, woman):
        print()
        ss.pp_paths_to_top()


if __name__ == '__main__':

    wn_version = sys.argv[1]
    category = sys.argv[2]

    wn_dir = "/DATA/resources/lexicons/wordnet/WordNet-%s/" % wn_version

    if wn_version == '1.5':
        noun_index_file = wn_dir + 'wn15/DICT/NOUN.IDX'
        noun_data_file = wn_dir + 'wn15/DICT/NOUN.DAT'
        verb_index_file = wn_dir + 'wn15/DICT/VERB.IDX'
        verb_data_file = wn_dir + 'wn15/DICT/VERB.DAT'
        btypes = cltypes.BASIC_TYPES_1_5
    elif wn_version == '3.1':
        noun_index_file = wn_dir + 'dict/index.noun'
        noun_data_file = wn_dir + 'dict/data.noun'
        verb_index_file = wn_dir + 'dict/index.verb'
        verb_data_file = wn_dir + 'dict/data.verb'
        btypes = cltypes.BASIC_TYPES_3_1
    else:
        exit("ERROR: unsupported wordnet version")

    wn = WordNet(wn_version, category,
                 noun_index_file, noun_data_file,
                 verb_index_file, verb_data_file)

    if category == NOUN:
        wn.add_basic_types(btypes)
        #wn.pp_toplevel()
        wn.pp_basic_types()
        #wn.display_basic_type_relations()
        #exit()
        cl = CoreLex(wn)
        #cl.pp_summary()
        cl.write('corelex.tab')
        cl.pp('corelex.txt')

        #test_paths_top_top(wn):

    elif category == VERB:
        wn.set_verbal_basic_types()
        #wn.pp_basic_types(VERB)
        cl = CoreLexVerbs(wn)
        #cl.pp_summary()
        cl.write('corelex.verbs.tab')
        cl.pp('corelex.verbs.txt')
