"""btype_manager.py

Contains a class to manage basic types. You can

- remove a type
- add a type
- replace a type and build a new one from all hypernyms of the synsets of the type
- replace a type and build a new one from all hyponyms of the synsets of the type
- save new types to a file


Load with the default WordNet version and print a list of basic types

    >>> btm = BasicTypeManager()
    >>> print(btm)
    <BasicTypeManager with 37 types>

Remove the articaft type

    >>> btm.remove_type('art')

And put it back in again

    >>> btm.add_type('art',  [('00022119', 'artifact.03.0 artefact.03.0')])

Replace the spc type with its supertypes

    >>> btm.replace_type_with_supertype('spc')

And the replace that one with all daughters of that supertype

    >>> btm.replace_type_with_subtypes('spc.sup')

Write new basic types to disk

    >>> btm.write('new_basic_types.py')


"""


import pprint
import wordnet
import cltypes


class BasicTypeManager(object):

    def __init__(self, types=None, wn=None):
        """Types and WordNet instance can be handed in, if not defaults will be used."""
        self.types = cltypes.BASIC_TYPES_3_1 if types is None else types
        self.types = self.types.copy()
        self.wn = wordnet.WordNet('3.1') if wn is None else wn

    def __str__(self):
        return "<BasicTypeManager with %s types>" % len(self.types)

    def print_types(self, verbose=True):
        """Pretty print types to the terminal."""
        for t in self.types:
            if verbose:
                print(t, self.types[t])
            else:
                print(t, end=' ')
        print()

    def remove_type(self, typename):
        """Remove basic type if it exists."""
        if typename in self.types:
            del(self.types[typename])

    def add_type(self, typename, synsets):
        self.types[typename] = synsets

    def replace_type_with_supertype(self, typename):
        new_typename = typename + '.sup'
        new_synsets = []
        for synset_id, synset_description in self.types[typename]:
            ss = self.wn.get_synset('noun', synset_id)
            hypernyms = ss.hypernyms()
            new_synsets.extend([(h.id, h.words_as_string()) for h in hypernyms])
        self.remove_type(typename)
        self.add_type(new_typename, new_synsets)

    def replace_type_with_subtypes(self, typename):
        new_typename = typename + '.sub'
        new_synsets = []
        for synset_id, synset_description in self.types[typename]:
            ss = self.wn.get_synset('noun', synset_id)
            hyponyms = ss.hyponyms()
            new_synsets.extend([(h.id, h.words_as_string()) for h in hyponyms])
        self.remove_type(typename)
        self.add_type(new_typename, new_synsets)

    def write(self, fname):
        with open(fname, 'w') as fh:
            pp = pprint.PrettyPrinter(stream=fh, indent=4)
            pp.pprint(self.types)


if __name__ == '__main__':

    btm = BasicTypeManager()

    print(btm)
    btm.remove_type('art')
    btm.remove_type('axe')   # does nothing, no error
    print(btm)               # should be less types now

    btm.replace_type_with_supertype('spc')
    btm.replace_type_with_subtypes('spc.sup')

    btm.print_types()



