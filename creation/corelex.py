
import sys
import pprint
import textwrap

from wordnet import WordNet
import basic_types


def flatten(some_list):
    result = []
    for element in some_list:
        if isinstance(element, list):
            result.extend(flatten(element))
        else:
            result.append(element)
    return result


def filter_basic_types(set_of_basic_types):
    for (subtype, supertype) in basic_types.BASIC_TYPES_ISA_RELATIONS_1_5:
        if subtype in set_of_basic_types and supertype in set_of_basic_types:
            set_of_basic_types.discard(supertype)


class CoreLex(object):

    # TODO: distinguish between version that create corelex from wordnet and
    # version that reads corelex from files
    
    def __init__(self, wordnet):
        self.wordnet = wordnet
        self.word_index = {}
        self.class_index = {}
        print("Creating CoreLex...")
        for word in sorted(wordnet.lemma_idx.keys()):
            synsets = wordnet.lemma_idx[word]
            synsets = [wordnet.get_synset(synset) for synset in synsets]
            basic_types = set()
            for synset in synsets:
                path = synset.paths_to_top()
                synsets = flatten(path)
                for synset in synsets:
                    if synset.basic_type:
                        basic_types.add(synset.basic_type)
            filter_basic_types(basic_types)
            corelex_class = ' '.join(sorted(basic_types))
            self.word_index[word] = corelex_class
            self.class_index.setdefault(corelex_class, []).append(word)

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
        for cl_class in sorted(self.class_index.keys()):
            print("%s\t%d" % (cl_class, len(self.class_index[cl_class])))


def test_paths_top_top(wn):
    act = wn.get_synset('00016649')
    compound = wn.get_synset('08907331')
    cat = wn.get_synset('05987089')
    woman = cat.hypernyms()[1]
    for ss in (act, compound, cat, woman):
        print()
        ss.pp_paths_to_top()


if __name__ == '__main__':

    wn_version = sys.argv[1] if len(sys.argv) > 1 else '3.1'
    wn_dir = "/DATA/resources/lexicons/wordnet/WordNet-%s/" % wn_version

    if wn_version == '1.5':
        index_file = wn_dir + 'wn15/DICT/NOUN.IDX'
        data_file = wn_dir + 'wn15/DICT/NOUN.DAT'
        btypes = basic_types.BASIC_TYPES_1_5
    elif wn_version == '3.1':
        index_file = wn_dir + 'dict/index.noun'
        data_file = wn_dir + 'dict/data.noun'
        btypes = basic_types.BASIC_TYPES_3_1
    else:
        exit("ERROR: unsupported wordnet version")

    wn = WordNet(wn_version, index_file, data_file)

    # todo: add this to corelex creation
    wn.add_basic_types(btypes)

    cl = CoreLex(wn)
    cl.pp_summary()
    #cl.write('corelex.tab')
    #cl.pp('corelex.txt')

    #test_paths_top_top(wn):
