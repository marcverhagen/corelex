"""CoreLex Analysis and DB Creation

This script allows some minor analysis of CoreLex by loading all data in
dictionaries. In addition it can generate tables for a relational database.

Load the dictionaries:

>>> nouns = Nouns(NOUNS)
>>> corelex_types = CoreLexTypes(CORELEX_TYPES)
>>> basic_types = BasicTypes(BASIC_TYPES)

And print some statistics:

>>> print nouns
<Nouns on data/corelex_nouns.txt with 39937 nouns and 126 corelex_types>

>>> print corelex_types
<CoreLexTypes on data/corelex_nouns.classes.txt with 126 corelex_types>

>>> print basic_types
<BasicTypes on data/corelex_nouns.basictypes.txt with 39 basic_types>

You can also do a pretty print of the types with the pp() method.

Check whether values in the nouns dictionary are the same set as the keys in the
corelex types dictionary:

>>> s1 = set([v[0] for v in nouns.nouns.values()])
>>> s2 = set(corelex_types.corelex_types.keys())
>>> print s1.difference(s2)
set([])
>>> print s2.difference(s1)
set([])

To create database tables use the create_sql() method on Nouns, CoreLexTypes and
BasicTypes instances.

To run the script on you need the four files below (NOUNS, NOUNS_PLUS,
CORELEX_TYPES and BASIC_TYPES). Three of them are from the original CoreLex
distribution, but NOUNS_PLUS is created by read_html_pages.py from the CoreLex
html files.

"""

import sys, StringIO, collections

NOUNS = 'data/corelex_nouns.txt'
NOUNS_PLUS = 'data/nouns_plus_types.tab'
CORELEX_TYPES = 'data/corelex_nouns.classes.txt'
BASIC_TYPES = 'data/corelex_nouns.basictypes.txt'


class Nouns(object):

    """Contains a dictionary indexed on nouns with corelex_types as values (of which
    there are 126). Also has a dictionary indexed on corelex types with lists of
    nouns as values."""
    
    def __init__(self, fname):
        self.fname = fname
        self.nouns = {}
        self.corelex_types = {}
        for (noun, corelex_type) in read_file(fname):
            self.nouns[noun] = corelex_type
            self.corelex_types.setdefault(corelex_type, []).append(noun)
        self._add_polysemous_types()

    def __str__(self):
        return "<Nouns on %s with %s nouns and %s corelex_types>" \
            % (self.fname, len(self.nouns), len(self.corelex_types))

    def _add_polysemous_types(self):
        for line in open(NOUNS_PLUS):
            corelex_type, polysemous_type, noun = line.strip().split("\t")
            if self.nouns[noun] != corelex_type:
                print "WARNING: noun-type mismatch"
            self.nouns[noun] = (corelex_type, polysemous_type)

    def create_sql(self):
        table_file = self.fname[:-3] + 'sql'
        values_string = StringIO.StringIO()
        for noun in sorted(self.nouns.keys()):
            corelex_type, polysemous_type = self.nouns[noun]
            values_string.write('("%s", "%s", "%s"),\n'
                                % (noun, corelex_type, polysemous_type))
        fh = open(table_file, 'w')
        fh.write("INSERT INTO nouns () VALUES\n")
        fh.write(values_string.getvalue()[:-2])
        fh.write(';\n')
        print "Table printed to %s" % table_file


class CoreLexTypes(object):

    """Contains a dictionary indexed on corelex types. For each corelex type, the
    value is a list of lists of basic types. For example, for the corelex type
    acp we have:

    acp --> [ [ act, atr, pro ],
              [ act, atr, pro, sta ],
              ... ]
    """
    
    def __init__(self, fname):
        self.fname = fname
        self.corelex_types = {}
        for fields in read_file(fname):
            corelex_type = fields.pop(0)
            basic_types = fields
            self.corelex_types.setdefault(corelex_type, []).append(basic_types)

    def __str__(self):
        return "<CoreLexTypes on %s with %s corelex_types>" \
            % (self.fname, len(self.corelex_types))

    def create_sql(self):
        table_file = self.fname[:-3] + 'sql'
        fh = open(table_file, 'w')
        insert_statements = set()
        for corelex_type in sorted(self.corelex_types.keys()):
            for basic_types in self.corelex_types[corelex_type]:
                basic_types_str = ' '.join(basic_types)
                insert_statements.add("INSERT INTO corelex_types () VALUES ('%s', '%s');\n"
                                      % (corelex_type, basic_types_str))
        for statement in sorted(insert_statements):
            fh.write(statement)
        print "Table printed to %s" % table_file

    def check(self):
        """Used this to find where there was a duplication, it turns out it was 'act com
        evt', which occurred twice as a value, both with the same corelex type."""
        btypes = []
        for corelex_type in sorted(self.corelex_types.keys()):
            for basic_types in self.corelex_types[corelex_type]:
                btypes.append(' '.join(basic_types))
        print len(btypes)
        print len(set(btypes))
        counter = collections.Counter(btypes)
        print counter

    def pp(self):
        for corelex_type in sorted(self.corelex_types.keys()):
            print corelex_type
            for basic_types in self.corelex_types[corelex_type]:
                print '  ', ' '.join(basic_types)


class BasicTypes(object):

    """This doctionary assciates the 39 basic types with synsets. Note that some
    basic types are associated with more than one synset."""
    
    def __init__(self, fname):
        self.fname = fname
        self.basic_types = {}
        for fields in read_file(fname):
            basic_type = fields.pop(0)
            synset_number = fields.pop(0)
            synset = fields
            bt = BasicType(basic_type, synset_number, synset)
            self.basic_types.setdefault(basic_type, []).append(bt)

    def __str__(self):
        return "<BasicTypes on %s with %s basic_types>" \
            % (self.fname, len(self.basic_types))

    def create_sql(self):
        table_file = self.fname[:-3] + 'sql'
        fh = open(table_file, 'w')
        for bt_name in sorted(self.basic_types.keys()):
            #print bt_name
            for basic_types in self.basic_types[bt_name]:
                synset = ' '.join(basic_types.synset[0::2])
                #print bt_name, basic_types.synset_number, synset
                fh.write("INSERT INTO basic_types () VALUES ('%s', %s, '%s');\n"
                         % (bt_name, basic_types.synset_number, synset))
        print "Table printed to %s" % table_file
    
    def pp(self):
        for basic_type in sorted(self.basic_types.keys()):
            print basic_type
            for bt in self.basic_types[basic_type]:
                print "   %s" % bt.synset_string()


class BasicType(object):

    def __init__(self, basic_type, synset_number, synset):
        self.basic_type = basic_type
        self.synset_number = synset_number
        self.synset = synset

    def synset_string(self):
        return "%s %s" % (self.synset_number, ' '.join(self.synset[0::2]))

        
def read_file(fname):
    lines = []
    for line in open(fname):
        if line[0] == '#':
            continue
        line = line.strip()
        if line:
            lines.append(line.split())
    return lines


    
if __name__ == '__main__':

    import doctest
    doctest.testmod()

    nouns = Nouns(NOUNS)
    corelex_types = CoreLexTypes(CORELEX_TYPES)
    basic_types = BasicTypes(BASIC_TYPES)

    #corelex_types.check()
    
    print nouns
    print corelex_types
    print basic_types

    nouns.create_sql()
    corelex_types.create_sql()
    basic_types.create_sql()
