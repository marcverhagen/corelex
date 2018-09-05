## Creating CoreLex and CoreLex2

Modules in this directory do the following:

- Give access to WordNet;
- Create CoreLex from WordNet;
- Allow command-line browsing of WordNet and CoreLex.


#### WordNet access

The `wordnet.py` module assumes that WordNet 1.5 or 3.1 can be found using the directory template in `wordnet.WORDNET_DIR`. It also assumes that the WordNet-3.1 distribution is as downloaded from the WordNet website. Dowloading WordNet 1.5 from https://wordnet.princeton.edu/download/old-versions gives you a directory `wn15` and this directory should be immediately under the WordNet-1.5 directory.


#### Creating CoreLex

The `corelex.py` module creates CoreLex from WordNet and can export CoreLex nouns into SQL files:

```
$ python3 corelex.py --create <version> <category>
$ python3 corelex.py --sql <version>
```

See the docstring in the module for more details.


#### Command line browser for WordNet and CoreLex

Start the command line browser by running

```
$ python3 browse.py <version> <category>
```

where the version is `1.5` or `3.1` and the category is `noun` or `verb`.

This shows similar data as for nouns and verbs on the official web interface at http://wordnetweb.princeton.edu/perl/webwn, but in addition it adds the CoreLex basic types for nouns.
