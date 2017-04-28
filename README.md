# CoreLex

CoreLex is a lexicon of nouns structured around systematic polysemy as found in WordNet. CoreLex was developed in the late nineties by Paul Buitelaar for his dissertation (*CoreLex: Systematic Polysemy and Underspecification*, PhD Thesis, Computer Science, Brandeis University, February 1998).

See [http://www.cs.brandeis.edu/~paulb/CoreLex/corelex.html](http://www.cs.brandeis.edu/~paulb/CoreLex/corelex.html) to more information on CoreLex and/or to download it. See http://wordnet.princeton.edu/ for WordNet.

This repository contains the front-end PHP code that gives access to database tables created from the CoreLex sources. The pages themselves are hosted at [http://timeml.org/corelex/browser](http://timeml.org/corelex/browser).

### Setting up the CoreLex browser site

To create the browser you need to do the following:

1. Create the database tables. There is code to do this which will be added to this repository, but part of it requires local access to the old static CoreLex Browser site on the Brandeis Computer Science server. Since CoreLex is built mostly automatically from WordNet these static files could be created directly from WordNet, but this has not been done yet.

2. Create a database, upload the schema and populate the tables. How to do this depends on your host set up. We have used MySQL.

3. Put the `browser` directory with all its contents on a server.

4. Copy the file `config-default.txt` to `config.txt` and edit the contents as required by the host.
