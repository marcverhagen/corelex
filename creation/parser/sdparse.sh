#!/bin/bash

# Run the stanford dependency parser over a .tagged file produced by
# semcor_parse.py. The first argument is the filename prefix of the .tagged
# file. Output is $filename.parse

# The java jar file stanford-nndep-wrapper-1.0-SNAPSHOT-fatjar.jar is a modified
# version of the stanford dependency parser that will accept input that is
# tokenized with lemma and part of speech provided, as is the case for the
# semcor annotated brown corpora.

# To run on combined brown1, brown2 corpus, use the output of semcor_parse.py
# function: run_semcor(), which produces the files semcor.tagged and
# semcor.lexsn.

# Argument 1 is the filename (without qualifier) of a .tagged file, where each
# line of the file is one tokenized sentence. Each token can contain a lemma and
# part of speech, separated by the character specified in the -d option in the
# parser call.  Here we use ~, since we know it does not show up in the brown
# corpora.

# sample tagged sentence (one line in <filename>.tagged):
# The~DT Fulton_County_Grand_Jury~NE_group~NNP said~say~VB Friday~friday~NN an~DT investigation~investigation~NN of~IN Atlanta~atlanta~NN 's~POS recent~recent~JJ primary_election~primary_election~NN produced~produce~VB ``~`` no~DT evidence~evidence~NN ''~'' that~IN any~DT irregularities~irregularity~NN took_place~take_place~VB .~.

# This script should not run from this directory.
# It intended to be used by semcor_db.sh in the parent directory.
# sh parser/sdparse.sh semcor 

source ./config.sh

infile=$CLDATA_DIR/$1.tagged
outfile=$CLDATA_DIR/$1.parse

parser=parser/stanford-nndep-wrapper-1.0-SNAPSHOT-fatjar.jar

echo "cat $infile | java -jar $parser -d~ -o $outfile"
cat $infile | java -jar $parser -d~ -o $outfile
