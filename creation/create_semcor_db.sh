#!/bin/bash
# create_semcor_db.sh

# Creates an sqlite database named semcor.db in CLDATA_DIR that includes two tables: sent, token

# Prerequisites:
# semcor corpus must be loaded in a directory referenced in config.sh (as SEMCOR_DIR)
# Make sure you are in a real or virtual environment with all prerequisite 
# python modules available before running this script:
# The command "python" must invoke python version 3.x
# Required modules: bs4 (BeautifulSoup), lxml 

# config.py must define the variables WORDNET_DIR and CLDATA_DIR
# config.sh must define CLDATA_DIR (same as in config.py) and SEMCOR_DIR, the location of
# the semcor3.0 directory.
# (Note that config.py and config.sh should be added to .gitignore if not already there.)
# CLDATA_DIR/semcor.db should not already exist

# Usage:

# nohup sh create_semcor_db.sh > semcor.log
# Note that the progress of the run and any errors will be writtent to semcor.log

source ./config.sh

start_time="$(date -u +%s)"

echo "Running: python semcor_parse.py extract"
python3 semcor_parse.py extract

end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "Time elapsed so far: $elapsed seconds"

echo "Running: sh sdparse.sh semcor"
sh sdparse.sh semcor

end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "Time elapsed so far: $elapsed seconds"

echo "Running: python semcor_parse.py merge"
python3 semcor_parse.py merge

end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "Time elapsed so far: $elapsed seconds"

# Create and populate sqlite database called semcor.db
echo "Changing directory to $CLDATA_DIR to create sqlite semcor.db database there"

cd $CLDATA_DIR

echo "Creating semcor.db, tables: sent, token"
sqlite3 semcor.db <<END_SQL
.timeout 2000

create table sent(sent_id integer primary key, doc_id varchar(10), para_no integer, sent_no integer, first_token_id integer, sentence text); 

create table token(token_id integer primary key, sent_id integer, token_no integer, surface text, lemma text, pos varchar(6), sense_no integer, sense_key text, ssid varchar(10), dom_token_no integer, dom_token_id integer, rel varchar(14) );

.separator "\t"
.import semcor.sent.tsv sent
.import semcor.token.tsv token

create index lemma_idx on token(lemma);
create index ssid_idx on token(ssid);

END_SQL

echo "Database semcor.db has been populated."

end_time="$(date -u +%s)"
elapsed="$(($end_time-$start_time))"
echo "Total of $elapsed seconds elapsed for entire process"

