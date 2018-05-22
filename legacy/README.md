# Legacy CoreLex

This directory contains the sources for the legacy CoreLex which was created from WordNet 1.5. It also contains code that can be used to create database tables from the sources.

See [http://www.cs.brandeis.edu/~paulb/CoreLex/corelex.html](http://www.cs.brandeis.edu/~paulb/CoreLex/corelex.html) for more information on the legacy CoreLex and the old on-line version. You can also download the sources there.

The original sources are

```
data/corelex_nouns.txt
data/corelex_nouns.classes.txt
data/corelex_nouns.basictypes.txt
data/CoreLex
```

The `CoreLex` contains the static HTML files that comprise the old static CoreLex pages at http://www.cs.brandeis.edu/~paulb/CoreLex/overview.html.

To create database tables from these sources you can run

```
$ python read_html_pages.py > data/nouns_plus_types.tab
$ python analyze.py
```

which will create an intermediary file

```
data/nouns_plus_types.tab
```

as well as the following SQL files

```
data/corelex_nouns.sql
data/corelex_nouns.classes.sql
data/corelex_nouns.basictypes.sql
```

The intermediary file and the three SQL files are also included in the repository so typically there is no need to run the commands above.

The SQL files can be used to populate the database that the CoreLex browser points at, see the [browser](../browser/README.md) directory in this repository for more details on setting up a CoreLex browser.
