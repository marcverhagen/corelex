# CoreLex

CoreLex is a lexicon of nouns structured around systematic polysemy as found in WordNet. The original CoreLex was developed in the late nineties by Paul Buitelaar in his dissertation (*CoreLex: Systematic Polysemy and Underspecification*, PhD Thesis, Computer Science, Brandeis University, February 1998).

CoreLex2 is a follow up project that expands on CoreLex.

This repository contains the following:

1. [legacy](legacy). Sources of the legacy CoreLex as well as new code to create database tables from those sources.

2. [browser](browser). The PHP code that gives access to an online database created from the CoreLex sources. The pages themselves are hosted at [http://timeml.org/corelex/browser](http://timeml.org/corelex/browser).

3. [creation](creation). Code to automatically create CoreLex from WordNet. Currently supported WordNet versions are 1.5, 3.0 and 3.1. When run on WordNet 1.5, this code creates the original CoreLex, when run on WordNet 3.1 it creates a version of CoreLex updated for WordNet 3.1, but it also run extra code to add verbs to CoreLex.

The pre-requisite for creating CoreLex is to have a copy of the WordNet index and data files. See http://wordnet.princeton.edu/ for WordNet downloads.
