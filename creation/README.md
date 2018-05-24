## Creating CoreLex2

Modules in this directory give access to WordNet, create CoreLex from WordNet, export CoreLex and allow command-line browsing of WordNet and CoreLex.


#### WordNet

The `wordnet.py` module assumes that WordNet 1.5 or 3.1 can be found using the directory template in `wordnet.WORDNET_DIR`. It also assumes that the WordNet-3.1 distribution is as downloaded from the WordNet website. Dowloading WordNet 1.5 from https://wordnet.princeton.edu/download/old-versions gives you a directory `wn15` and this directory should be immediately under the WordNet-1.5 directory.


#### WordNet Browser

Start the command line browser by running

```
$ python3 wn_browser.py <version> <category>
```

where the version is `1.5` or `3.1` and the category is `noun` or `verb`.


#### CoreLex

The `corelex.py` module creates CoreLex from WordNet and can export CoreLex nouns into SQL files:

```
$ python3 corelex.py --create <version> <category>
$ python3 corelex.py --sql <version> <category>
```

See the docstring in the module for more details.

In addition the module can fire up a simple command line browser:

```
$ python3 corelex.py --browse <version> <category>
```
