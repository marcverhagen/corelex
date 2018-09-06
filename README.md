#  CoreLex2

CoreLex 2.0 is a lexicon of nouns structured around systematic polysemy as found in WordNet (http://wordnet.princeton.edu/).

The original CoreLex was developed in the late nineties by Paul Buitelaar in his dissertation (*CoreLex: Systematic Polysemy and Underspecification*, PhD Thesis, Computer Science, Brandeis University, February 1998). See the original [CoreLex website](http://www.cs.brandeis.edu/~paulb/CoreLex/corelex.html) for more information on the legacy CoreLex and the old on-line version.

CoreLex 2.0 is a follow up project that expands on CoreLex. Expansion is partially by using WordNet 3.1 instead of WordNet 1.5, but also by adding more information on nominals and by trying to extend the approach to verbs. CoreLex data files can be created with code in this repository, but the main CoreLex 2.0 data file with mappings from WordNet nouns to polysemous types is included in the distribution at `creation/data/corelex-2.0-lemmas-nouns.tab`.

This repository contains the following:

1. [Legacy CoreLex](legacy). Sources of the legacy CoreLex as well as new code to create database tables from those sources.

2. [CoreLex Browser](browser). The PHP code that gives access to an online database created from the CoreLex sources. The pages themselves are hosted at [http://timeml.org/corelex/browser](http://timeml.org/corelex/browser).

3. [CoreLex Creation](creation). Code to automatically create CoreLex from WordNet.

The versioning of this code goes in lockstep with the version of CoreLex created.
