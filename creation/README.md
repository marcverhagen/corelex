# Creating CoreLex2

The main modules in this directory do the following:

- `wordnet.py` - give access to WordNet;
- `corelex.py` - create CoreLex from WordNet;
- `browse.py` - allow command-line browsing of WordNet and CoreLex.



## Requirements and Installation

This code is known to run on Python 3.7 on OSX and Linux, it is very possible that the code runs on Python 3.5 and 3.6 as well. No third party modules are used in the code described here, but some modules like semcor_cl.py and semcor_parse.py do use non-standard modules (nltk, bs4 and lxml).

For installation you need to copy the file `config.sample.py` to `config.py` and edit the variables in that file to match your local set up. For creating CoreLex you only need to look at `WORDNET_DIR`, which points to the WordNet sources.

### Installing WordNet

The pre-requisite for creating CoreLex is to have a copy of the WordNet index and data files. The `wordnet.py` module assumes that WordNet 1.5 or 3.1 can be found using the directory template in `WORDNET_DIR` in `config.py`, which probably needs to be edited to fits your needs, here is the default value:

```
/DATA/resources/lexicons/wordnet/WordNet-%s/
```

This basically assumes that there are two directories

```
/DATA/resources/lexicons/wordnet/WordNet-1.5/
/DATA/resources/lexicons/wordnet/WordNet-3.1/
```

The WordNet-3.1 directory should have the WordNet distribution as downloaded from the WordNet website, in particular, it should have a `dict` subdirectory. Downloading WordNet 1.5 gives you a directory `wn15` and this directory should be immediately under the `WordNet-1.5` directory. Download WordNet 3.1 from http://wordnet.princeton.edu/ and WordNet 1.5 from https://wordnet.princeton.edu/download/old-versions. There is no need to have both WordNets downloaded, for most uses just having WordNet 3.1 should be fine.

Note that to get WordNet 3.1, you need to combine WordNets 3.0 and 3.1. In short: (1) get WordNet.3.0, (2) get the database files for 3.1, (3) unpack both of them, (4) move `dict` (from 3.1) into `WordNet.3.0`, and (5) rename `WordNet.3.0` into `WordNet.3.1`.




## WordNet access

To load WordNet in Python do

```python
>>> from wordnet import WordNet
>>> wn = WordNet('3.1')
```

This loads version 3.1 of WordNet, you can use '1.5' instead. Once WordNet is loaded you can search and navigate it:

```python
>>> wn.get_noun('door').synsets
['02432728', '02435375', '03588923', '02433420', '02433281', '02433101']
>>> door = wn.get_noun_synset('02432728')
>>> door
<Synset 02432728 n door.06.0>
>>> print(door.hypernyms()[0])
<Synset 02801978 n movable_barrier.06.0>
```

You can add a set of basic types to the WordNet instance:

```python
>>> from cltypes import BASIC_TYPES_3_1
>>> wn.add_nominal_basic_types(BASIC_TYPES_3_1)
>>> wn.get_noun_synset('02432728').basic_types
{'art'}
```

Note that instead of importing the basic types from cltypes you can get them in any other way as long as they have the same format as cltypes.BASIC_TYPES_3_1.

To include the default basic types when loading WordNet do

```python
>>> wn = WordNet('3.1', add_basic_types=True)
```

This will load the default types for the specified WordNet version from cltypes.py.



## Creating CoreLex

The `corelex.py` module creates a basic CoreLex from WordNet:

```
$ python3 corelex.py --create-cltype-files <version>
```

For version you can use either `1.5` or `3.1`. When using version 1.5 you basically recreate something close to the old legacy CoreLex from 1998, with verbs added (but note that the verbs are still rather experimental). When using version 3.1 you create CoreLex 2.0.

CoreLex 2.0 is different from CoreLex in that while it creates systematically polysemous types from WordNet, it does not yet implement a many-to-one mapping from those types to CoreLex types.

See the docstring in the `corelex` module for more details.




## Command line browser for WordNet and CoreLex

Start the command line browser by running

```
$ python3 browse.py <version> <category>
```

where the version is `1.5` or `3.1` and the category is `noun` or `verb`.

This shows similar data as on the official web interface at http://wordnetweb.princeton.edu/perl/webwn, but in addition it adds the CoreLex basic types for nouns.
