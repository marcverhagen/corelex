# Exploring SemCor

Some code to store SemCor in a database and query it.

### Database creation

To create the database you need Python 3 with lxml, BeautifulSoup and NLTK installed:

```bash
$ pip install lxml bs4 nltk
```

The following scripts are used:

````
semcor_db.sh
parser/sdparse.sh
parser/stanford-nndep-wrapper-1.0-SNAPSHOT-fatjar.jar
semcor_parse.py
semcor_cl.py
wordnet.py
````

You also need to create a config.sh file with content like

```properties
CLDATA_DIR=data/semcor
SEMCOR_DIR=/Users/Shared/data/resources/corpora/semcor/semcor3.0
PYTHON=python3.9
```

To create the database in `data/semcor/semcor.db`:

```bash
$ sh semcor_db.sh
```

This should take 5-10 minutes.

### Database querying

```bash
$ pip install nested_dict
```

The following scripts and file are used:

````
semcor_db.py
semcor_cl.py
wordnet.py
data/semcor/semcor.db
````

Open a cursor:

 ```python
>>> import semcor_db
>>> c = semcor_db.get_cursor()
 ```

Example query:

```python
>>> semcor_db.get_dom_lemma_ssid(c, "victory", "07488581", "dobj")
```
This returns:

```
[['give', '01632595'], ['gain', '02293158'], ['describe', '00007846'], ['give', '01632595'], ['total', '02651091']]
```

See `semcor_db.py` for more queries.

