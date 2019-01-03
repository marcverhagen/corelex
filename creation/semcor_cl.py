"""
semcor_cl.py 

This module contains utilities for processing the semcor annotated corpus and
producing human readable files regarding certain relationships between noun synsets.
The semcor corpus consists of two subsets of the Brown corpus which have been tokenized, 
lemmatized, part of speech tagged, and labeled with wordnet senses.
Semcor documentation and downloads are available at 
http://web.eecs.umich.edu/~mihalcea/downloads.html#semcor

Dependencies:

To use this code, download and install SemCor 3.0.  Modify your config.py file to 
contain the full path for your semcor3.0 directory in the variable SEMCOR_DIR.

You will also need wordnet 3.1 installed, with a pointer to the wordnet directory 
(missing the version #) in the config.py file as the value of WORDNET_DIR.
The line should look like:
WORDNET_DIR = '<your-full-path-here>/WordNet-%s/'

python 3.x

To run:

To create all the files described below:
From command line, run
$python3 semcor_cl.py

or within python, run 

>semcor_cl.create_SemCorF() 

Output:

file: corelex-3.1-semcor_pairs-nouns.tab
description: One line for each pair of synsets which map to the same lemma and appear
together in at least one document in the semcor corpus.  These represent lemmas for which
alternate senses occur within the same (document sized) "context".
format: lemma basic_type_for_synset1 basic_type_for_synset2 synset1_offset synset2_offset synset1_text|synset2_text
example line:
ability atr psy 05207437        05624029        the quality of being able to perform...|possession of the qualities (especially mental qualities) required to do something...
NOTE: for browsing the file, it is useful to sort it lexicographically first, so that pairs 
for the same lemma will occur in sequence.

file: corelex-3.1-semcor_sentno2file-nouns.tab
description: One line mapping a sentence number to the document it occurs in.  Sentence numbering
starts at 0.  Document names are the same as file names in the Brown corpus directories.
format: sentence_number doc_name
example line: 7       br-a01

file: corelex-3.1-semcor_doc_pairs-nouns.tab
description: One line for a pair of synsets for the same lemma, showing the doc they cooccurred in
and the sentence numbers with that doc.  
format: lemma synset1_offset synset2_offset document_name list_of_sent_nos_for synset1 list_for_synset2
example line: vote    00183062        00184354        br-a01  [76]    [44, 47, 62, 63, 65, 67]
NOTE: For browsing, it is best to sort the file lexicographically.

file: corelex-3.1-semcor_missing_sids-nouns.tab
description: a list of sense_keys (sids) which have no corresponding synset offset in the
wordnet 3.1 index.sense file.
format: sense_key
example line: variety%1:09:00::
NOTE: It is unclear why so many sense keys have no mapping.  Needs to be investigated further.

"""

from collections import defaultdict
from config import SEMCOR_DIR
from wordnet import WordNet
import itertools
import pdb
import os

# to use reload in python3: >>> from importlib import reload

# utilities
# create a single string out of a set of strings
def set2string(myset):
    return("|".join(myset))

# Set write_output_p to True to generate output files.
# Set it to False to return a populated SemCorF object without writing 
# data to files. All the info needed to generate the output files
# is stored in the object.
def create_SemCorF(write_output_p = True):
    wn = WordNet('3.1')
    wn.add_basic_types()
    sc = SemCorF(wn, SEMCOR_DIR, write_output_p)
    return(sc)
    
# class to create and output files based on semcor annotations
class SemCorF():

    # output file for pairs of synset ids that occur for the same lemma in the same doc
    # lemma sid1 sid2 doc sent_no1 sent_no2
    def corelex_semcor_pairs_file(self, category, extension='tab'):
        return "data/corelex-%s-semcor_pairs-%ss.%s" % (self.cl_version, category, extension)

    # output file for pairs of synset ids, docs and sentence numbers where they occur
    def corelex_semcor_doc_pairs_file(self, category, extension='tab'):
        return "data/corelex-%s-semcor_doc_pairs-%ss.%s" % (self.cl_version, category, extension)

    # output file of sense keys which map to no synset offset in wordnet 3.1
    def corelex_semcor_missing_sids_file(self, category, extension='tab'):
        return "data/corelex-%s-semcor_missing_sids-%ss.%s" % (self.cl_version, category, extension)

    # mapping of sent_no to the file_name (document) it appears in
    def corelex_semcor_sentno2file(self, category, extension='tab'):
        return "data/corelex-%s-semcor_sentno2file-%ss.%s" % (self.cl_version, category, extension)

    
    def __init__(self, wn, semcor_dir, write_output_p = True):

        self.wordnet = wn
        self.cl_version = '3.1'
        self.write_output_p = write_output_p

        #sid is synset offset (synset.id in wordnet.py)
        #lemma is the canonical wordnet string
        #cf is corpus frequency
        #df is document frequency
        #spair is a tuple of synset offsets for a lemma, alphabetically sorted
                
        self.dn_lemma2cf = defaultdict(int)
        self.dn_lemma2df = defaultdict(int)
        #self.dn_sid2lemma = {}
        #self.dn_lemma2sid = {}
        self.dn_sid2cf = defaultdict(int)
        self.dn_sid2df = defaultdict(int)
        # dict whose key is a tuple of a lemma and pair of synset offsets (for example:
        # ('end', '05989760', '15291722')
        # and value is the number of docs the synsets
        # cooccur in (as long as the number is >= 1)
        # By iterating through this dict, you can get all the pairs that cooccur.
        # e.g., lemma_pair = next(iter(sc.dn_spair2df.items))
        self.dn_spair2df = defaultdict(int)

        # map a sentence number to the document it occurs in
        self.sent_no2doc = {}

        # track any missing sense keys that appear in semcor but not in
        # wordnet index.sense file.
        self.missing_keys = set()

        self._load_semcor(semcor_dir)
        #self._output_semcor_stats(output_dir)
        if self.write_output_p:        
            self._output_dn_semcor('noun')
        
        # print out missing sense keys
        if self.write_output_p:
            number_missing_keys = len(self.missing_keys)
            filename = self.corelex_semcor_missing_sids_file('noun')

            print("WARNING: %i sense keys had no mapping in wordnet.  See %s" % (number_missing_keys, filename))
            with open(filename, 'w') as fh:
                for key in self.missing_keys:
                    fh.write("%s\n" % key)
            
    def _load_semcor(self, semcor_dir):
    # As of December 2018, semcor directory contains two files with 
    # wordnet sense annotations for nouns and verbs:
    # brown1, brown2.
    # We will combine these into a single corpus for our corpus 
    # statistics.

        # To track sentence numbers (consistent with nltk semcor numbering)
        # we will start numbering sentences by 0 and continue the numbering
        # across the brown1 and brown2 corpora.
        # We will look for a <sent> tag in the xml file to know when to increment sent_no
        sent_no = -1

        # file to capture pairs along with specific documents and sentence numbers
        semcor_doc_pairs_file = self.corelex_semcor_doc_pairs_file('noun')

        if self.write_output_p:
            semcor_doc_pairs_stream = open(semcor_doc_pairs_file, "w")

        # We are interested in semcor lines containing nouns. e.g.
        # <wf cmd=done pos=NN lemma=jury wnsn=1 lexsn=1:14:00::>jury</wf>
        #for subdir in ["brown1"]:
        for subdir in ["brown1", "brown2"]:

            path = os.path.join(semcor_dir, subdir, "tagfiles")
            # Note that nltk semcor routines process the files in lexicographic order.
            # In order for our sentence numbering to match theirs, we have to process
            # the files in the same order.
            for semcor_file in sorted(os.listdir(path)):
                # for each lemma in the doc, keep the set of 
                # sids that appear for the lemma
                dn_lemma2sids = defaultdict(set)

                # keep a doc specific list of sentence numbers in which a
                # synset occurs
                dn_sid2sent_nos = defaultdict(list)

                semcor_path = os.path.join(path, semcor_file)
                for line in open(semcor_path):
                    # check if the line starts a new sentence
                    # indicated by the tag <s snum=1>
                    # If so, increment the sent_no
                    if line[0:7] == "<s snum":
                        sent_no += 1
                        # capture the relationship between sent_no and document (semcor filename)
                        self.sent_no2doc[sent_no] = semcor_file

                    # simple way to extract needed fields for noun lemmas
                    try:
                        (w, d, p, l, w, s) = line.split(' ')
                        if p == "pos=NN":
                            # we have a common noun.
                            # extract the field values we need.
                            pos = p.split('=')[1]
                            lemma = l.split('=')[1]
                            wnsn = int(w.split('=')[1])
                            lexsn = s.split('>')[0].split('=')[1]
                            lemma_sense_key = "%".join([lemma, lexsn])
                            # get the synset_offset (sid) corresponding to the sense key composed of lemma%lexsn
                            # NOTE: some semcor keys do not appear to be
                            # in wordnet's index.sense 3.1 mapping file.  We have to
                            # ignore these.
                            #pdb.set_trace()
                            if lemma_sense_key in self.wordnet._sense_idx:
                                sid = self.wordnet._sense_idx[lemma_sense_key]

                                # update the corpus frequencies
                                self.dn_lemma2cf[lemma] += 1
                                self.dn_sid2cf[sid] += 1

                                # add the sid to the set of sids for the lemma
                                # assuming the sense id has a mapping to a synset offset
                                # in wordnet's index.sense file.
                                dn_lemma2sids[lemma].add(sid)
                                # keep track of all the sentences this synset occurs in
                                dn_sid2sent_nos[sid].append(sent_no)
                                #pdb.set_trace()

                            else:
                                self.missing_keys.add(lemma_sense_key)

                    except ValueError:
                        continue

                # We have finished processing a single doc.
                # Update doc frequencies
                for lemma, sids in dn_lemma2sids.items():
                    self.dn_lemma2df[lemma] += 1
                    for sid in sids:
                        self.dn_sid2df[sid] += 1

                    #pdb.set_trace()
                    # compute all sid pairs and update their doc freqs
                    # extract pairs of sids for the lemma by taking all 
                    # combinations of two items in the l_basic_type list.
                    l_sid_pair =  list(itertools.combinations(sids, 2))
                    for sid_pair in l_sid_pair:
                        sid_pair = sorted(sid_pair)
                        sid_tuple = tuple([lemma] + sid_pair)
                        # save the tuple and increment count (across docs)
                        self.dn_spair2df[sid_tuple] += 1

                        sid1 = sid_pair[0]
                        sid2 = sid_pair[1]
                        sid1_sents = dn_sid2sent_nos[sid1]
                        sid2_sents = dn_sid2sent_nos[sid2]
                        # output the within doc tuples along with their sent_nos
                        # filename = self.corelex_semcor_doc_pairs_file(category)
                        if self.write_output_p:
                            semcor_doc_pairs_stream.write("%s\t%s\t%s\t%s\t%s\t%s\n" %(lemma, sid1, sid2, semcor_file, sid1_sents, sid2_sents))
                        #pdb.set_trace()

        if self.write_output_p:        
            semcor_doc_pairs_stream.close()

            filename = self.corelex_semcor_sentno2file('noun') 
            with open(filename, 'w') as fh:
                for (sent_no, doc) in self.sent_no2doc.items():
                    fh.write("%i\t%s\n" % (sent_no, doc))


                        
    # This output is collapsed across docs.  The same sense pair appearing in
    # multiple documents will only be output once.  However, if it appears with a
    # different lemma, it will be output once per lemma.
    def _output_dn_semcor(self, category):
        filename = self.corelex_semcor_pairs_file(category)
        with open(filename, 'w') as fh:
            for pair, df in self.dn_spair2df.items():
                lemma = pair[0]
                s1 = pair[1]
                s2 = pair[2]
                #pdb.set_trace()
                # Note that some synsets may have multiple basic types.  We will 
                # append these into a string separated by | using set2string.
                s1_bt = set2string(self.wordnet.get_noun_synset(s1).basic_types)
                s2_bt = set2string(self.wordnet.get_noun_synset(s2).basic_types)
                #pdb.set_trace()

                joined_basic_types = " ".join([s1_bt, s2_bt])

                s1_gloss = self.wordnet.get_noun_synset(s1).gloss
                s2_gloss = self.wordnet.get_noun_synset(s2).gloss
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (lemma, joined_basic_types, s1, s2,  '|'.join([s1_gloss, s2_gloss])))

        


if __name__ == '__main__':
    print("Creating semcor files in %s" % SEMCOR_DIR)
    create_SemCorF()
    print("File created.")

