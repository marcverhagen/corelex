## Creating CoreLex2

Modules in this directory do the following:

- `wordnet.py` - give access to WordNet;
- `corelex.py` - create CoreLex from WordNet;
- `browse.py` - allow command-line browsing of WordNet and CoreLex.


#### WordNet access

The pre-requisite for creating CoreLex is to have a copy of the WordNet index and data files. The `wordnet.py` module assumes that WordNet 1.5 or 3.1 can be found using the directory template in `WORDNET_DIR` in `wordnet..py`:

```
/DATA/resources/lexicons/wordnet/WordNet-%s/
```

Basically it assumes two directories

```
/DATA/resources/lexicons/wordnet/WordNet-1.5/
/DATA/resources/lexicons/wordnet/WordNet-3.1/
```

The WordNet-3.1 should have the WordNet distribution as downloaded from the WordNet website, in particular, it should have a `dict` subdirectory. Downloading WordNet 1.5 gives you a directory `wn15` and this directory should be immediately under the `WordNet-1.5` directory. Download WordNet 3.1 from http://wordnet.princeton.edu/ and WordNet 1.5 from https://wordnet.princeton.edu/download/old-versions.

The `wordnet.py` moduel is used by the `corelex.py` module.


#### Creating CoreLex

The `corelex.py` module creates a basic CoreLex from WordNet:

```
$ python3 corelex.py --create-cltype-files <version>
```

For version you can use either `1.5` or `3.1`. When using version 1.5 you basically recreate something close to the old legacy CoreLex from 1998, with verbs added (but note that the verbs are still rather experimental). When using version 3.1 you create CoreLex 2.0.

CoreLex 2.0 is different from CoreLex in that while it creates systematically polysemous types from WordNet, it does not yet implement a many-to-one mapping from those types to CoreLex types.

See the docstring in the `corelex` module for more details.


#### Command line browser for WordNet and CoreLex

Start the command line browser by running

```
$ python3 browse.py <version> <category>
```

where the version is `1.5` or `3.1` and the category is `noun` or `verb`.

This shows similar data as on the official web interface at http://wordnetweb.princeton.edu/perl/webwn, but in addition it adds the CoreLex basic types for nouns.
