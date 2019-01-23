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

To run without producing files:
sc = semcor_cl.create_SemCorF(False)

"""

from collections import defaultdict
from config import SEMCOR_DIR
from wordnet import WordNet
from nltk.corpus import semcor
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

        # map a lemma and synset offset (lemma, sid tuple) 
        # to the set of sentence numbers it
        # occurs in. Use a set in case the same lemma/sid occurs
        # multiple times in the same sentence.  
        # Sentence numbers are ordered from 0 and continue through
        # the brown1 and brown2 semcor files (taken in lexicographic order.)
        self.dn_lemma_sid2all_sent_nos = defaultdict(set)

        # map from lemma to the set of (lemma, sid) tuples found in the corpus
        self.dn_lemma2all_lemma_sid = defaultdict(set)

        # keep a set of all sids (synset offsets) found in the corpus for a 
        # given lemma
        self.dn_lemma2all_sids = defaultdict(set)

        # mapping from lemma to all pairs of sids for the lemma the cooccur in
        # at least one document.
        self.dn_lemma2spair = defaultdict(set)

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

    # return the nth sentence from the semcor corpus
    def get_semcor_sentence(self, sent_no):
        sent = " ".join(semcor.sents()[0])
        return(sent)
    
    def get_lemma_sid_info(self, lemma, sid):
        bt = set2string(self.wordnet.get_noun_synset(sid).basic_types)
        sents = list(self.dn_lemma_sid2all_sent_nos[(lemma, sid)])
        return(bt, sents)
        
    def get_lemma_sid_pair_info(self, lemma, sid1, sid2):
        (bt1, sents1) = self.get_lemma_sid_info(lemma, sid1)
        (bt2, sents2) = self.get_lemma_sid_info(lemma, sid2)
        return(bt1, bt2, sents1, sents2)

    def get_spair_info(self, spair):
        (lemma, sid1, sid2) = spair
        (bt1, bt2, sents1, sents2) = self.get_lemma_sid_pair_info(lemma, sid1, sid2)
        gloss1 = self.wordnet.get_noun_synset(sid1).gloss
        gloss2 = self.wordnet.get_noun_synset(sid2).gloss
        return(lemma, bt1, bt2, gloss1, gloss2, self.get_semcor_sentence(sents1[0]), self.get_semcor_sentence(sents2[0]) ) 

            
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

        ## /// NOTE: We will need to change the start number to 1, rather than 0.  TODO
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

                # keep a doc specific set of sentence numbers in which a
                # synset occurs.  Use a set in case the same lemma/sid occurs
                # multiple times in the same sentence.
                dn_sid2sent_nos = defaultdict(set)

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

                                # corpus-wide mapping of lemma to (lemma, sid) tuples
                                self.dn_lemma2all_lemma_sid = defaultdict(set)

                                # update the corpus-wide set of sids per lemma 
                                self.dn_lemma2all_sids[lemma].add(sid)

                                # keep track of all the sentences this synset occurs in
                                dn_sid2sent_nos[sid].add(sent_no)

                                # update the corpus-wide set of sentences for the 
                                # lemma/synset combination
                                lemma_sid = (lemma, sid)

                                ### BUG? Check the lemma_sid. Is the sid a number or
                                ### string.  Is the sent_no correct. ///
                                self.dn_lemma_sid2all_sent_nos[lemma_sid].add(sent_no)
                                
                                # update the corpus-wide set of lemma-sid tuples for 
                                # each lemma

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

                        # corpus-wide mapping of lemma to sid pairs
                        # pairs that cooccur in at least one document
                        self.dn_lemma2spair[lemma].add(sid_tuple)

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

def create_parallel(write_output_p = False):
    wn = WordNet('3.1')
    wn.add_basic_types()
    para = Parallel(wn)
    return(para)

# from importlib import reload
# import wordnet
# wn = wordnet.WordNet('3.1')
# wn.add_basic_types()
# import semcor_cl
# semcor_cl.run_para(wn)
def run_para(wn):
    p = Parallel(wn)
    #p.top_pair_parallels(10, 10000)
    p.filter_pair_file()

class Parallel():

    def __init__(self, wn):
        self.wordnet = wn
        # This file needs to be created from corelex-3.1-semcor_pairs-nouns.tab:
        # cat corelex-3.1-semcor_pairs-nouns.tab | cut -f2 | sunr > corelex-3.1-semcor_pairs-nouns.f2.sunr
        # alias sunr='sort | uniq -c | sort -nr | sed -e '\''s/^ *\([0-9]*\) /\1  /'\'''
        self.sorted_pairs_file = "data/corelex-3.1-semcor_pairs-nouns.f2.sunr"
        # We'll use a threshold of frequency of pair type >= 10 for generating
        # the parallels data in top_pair_parallels()
        self.para_file = "data/corelex-3.1-semcor-gte_10.para"
        # pair_file generated using the semcor_cl class
        # use the sorted file to get output in alphabetical order by source lemma
        self.semcor_pairs_nouns_file = "data/corelex-3.1-semcor_pairs-nouns.tab.sorted"
        self.filtered_pair_file = "data/corelex-3.1-semcor_pairs-nouns.filt"

    # /// add a class to hold the sister synsets and its parallel words/synsets
    #class sister_pair(self):
        #self.synset
        

    def word2bt_synsets(self, word, basic_type):
        word_synset_ids = []
        word_obj = self.wordnet.get_noun(word)
        # It is possible to get a word that is referenced in a synset which does
        # not have its own wordnet entry (e.g. "Anglo-Saxon").  So we have to
        # test for that situation here by seeing if the resulting word object is null.
        if word_obj == None:
            print("[semcor_cl.py]word2bt_synsets: word not in wordnet: %s\n" % word)
            return([])
        else:
            word_synset_ids = self.wordnet.get_noun(word).synsets

        # convert ids list to synset list
        word_synsets = [self.wordnet.get_noun_synset(sid) for sid in word_synset_ids]
        # create list of synsets which have the basic_type requested
        wbt_synsets = []
        #pdb.set_trace()
        for synset in word_synsets:
            if basic_type in synset.basic_types:
                wbt_synsets.append(synset)
        return(wbt_synsets)

    # Given a lemma and two synsets for the lemma
    # Find sister synsets of synset 1 that have lemmas with synsets which also
    # match the basic_type of synset 2 
    # p.find_parallels("american", "06960241", "09758057", "com", "hum")
    # p.find_parallels("addition", "00364614", "02682269", "act", "pho")
    # p.find_parallels("allotment",  "01085569", "13310490","act", "pos" )
    # p.find_parallels("air", "08670889", "14865437", "loc", "sub")
    def find_parallels(self, lemma, sid1, sid2, basic_type_1, basic_type_2, verbose_p = False):
        ss1 = self.wordnet.get_noun_synset(sid1)
        sister_lemmas = []
        parallels = []
        no_parallels = []
        # extract the (simple word) lemmas for sister synsets
        for sister_synset in ss1.sisters():
            l_simple_words = sister_synset.simple_words
            if l_simple_words != []:
                sister_lemmas.extend(l_simple_words)

        #pdb.set_trace()
        for word in sister_lemmas:
            sister_word_synsets = self.word2bt_synsets(word, basic_type_2)
            # track any word that has no parallel synset (with desired basic_type)
            if sister_word_synsets == []:
                no_parallels.append(word)
                if verbose_p:
                    print("no parallel for: %s\n" % word)
            for sister_word_synset in sister_word_synsets:
                parallels.append((word, sister_word_synset))
                if verbose_p:
                    print("%s\t%s\t%s\n" % (word, sister_word_synset.id, sister_word_synset.gloss))

        return(parallels, no_parallels)

    def top_pair_parallels(self, min_count = 10, limit = 100000000):
        # any pair of unequal basic types with semcor frequency >= min_count
        d_top_pairs = {}
        for line in open(self.sorted_pairs_file):
            (count, pair) = line.split("\t")
            bt1, bt2 = pair.split(" ")
            count = int(count)
            if count >= min_count:
                # index by tuple of basic types
                d_top_pairs[(bt1, bt2)] = count
            else:
                continue

        # open our output file for parallels
        with open(self.para_file, 'w') as parallels_str:
            # iterate through the sorted file of pairs found in semcor
            # watch for limit (to process a subset of the file)
            line_number = 0
            for line in open(self.semcor_pairs_nouns_file):
                line_number += 1
                if line_number > limit:
                    print("Reached line limit: %i\n" % line_number)
                    return()
                # conditions: 
                # 1. Pair must be high frequency (ie. in the d_top_pairs dict
                # 2. Pair must be composed of two different basic types
                # (Note that many pairs have the same basic type. We ignore these
                # for now.)
                (lemma1, bt_pair, sid1, sid2, glosses) = line.split("\t")
                (basic_type_1, basic_type_2) = bt_pair.split(" ")
                if basic_type_1 == basic_type_2:
                    continue
                (parallels, no_parallels) = self.find_parallels(lemma1, sid1, sid2, basic_type_1, basic_type_2)
                parallels_str.write("%s\t%s\t%s %s\t%s\n" % (lemma1, bt_pair, sid1, sid2, glosses))
                for parallel in parallels:
                    (word, sister_word_synset) = parallel
                    parallels_str.write("\t%s\t%s\t%s\n" % (word, sister_word_synset.id, sister_word_synset.gloss))
                #parallels_str.write("\tNo match: %s\n\n" % no_parallels)

        print("Processed line number: %i\n" % line_number)

    # Take a pair file sorted by the pair field (column 2)
    # Remove any lines for which the members of the pair are equal.
    # This gives us all examples of a particular pair type.
    def filter_pair_file(self, min_count = 10):
        d_pairs = {}
        # create dict with counts for each pair of basic types
        for line in open(self.sorted_pairs_file):
            line = line.strip()
            (count, pair) = line.split("\t")
            count = int(count)
            d_pairs[pair] = count

        #pdb.set_trace()
        with open(self.filtered_pair_file, 'w') as filtered_str:
            for line in open(self.semcor_pairs_nouns_file):
                # conditions: 

                # 2. Pair must be composed of two different basic types
                # (Note that many pairs have the same basic type. We ignore these
                # for now.)
                (lemma, bt_pair, sid1, sid2, glosses) = line.split("\t")
                (basic_type_1, basic_type_2) = bt_pair.split(" ")
                count = d_pairs[bt_pair]
                if (basic_type_1 != basic_type_2) and (count >= min_count):
                    filtered_str.write("%i\t%s\t%s\t%s %s\t%s\n\n" % (count, bt_pair, lemma, sid1, sid2, glosses))
        

if __name__ == '__main__':
    print("Creating semcor files in %s" % SEMCOR_DIR)
    create_SemCorF()
    print("File created.")

