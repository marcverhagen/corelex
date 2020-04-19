"""
NOTE: To create the semcor.db sqlite database, use create_semcor_db.sh, 
a script which calls the approporiate functions here.

semcor_parse.py contains functions to extract annotation data from the semcor 
brown corpus (brown1, brown2) and to create the data files needed to run
the Stanford dependency parser over the corpus and subsequently merge the 
parsed output with the annotated data (doc, sentence, wordnet features)

Dependencies: bs4 and lxml packages must be installed.
pip install bs4
pip install lxml

config.py should contain the location of the semcor data (SEMCOR_DIR) and
a directory where output files will be placed (CLDATA_DIR)

To process the semcor corpus:
(1) In python 3:
semcor_parse.run_semcor()

This creates: semcor.tagged, semcor.lexsn

(2) From command line:
$sh sdparse.sh semcor   (which depends on directories specified in config.sh)

This takes a while to run and creates: semcor.parse

(3) In python 3:
semcor_parse.run_create()

This creates semcor.token and semcor.sent described below:
semcor.token - tab separated file with parser output and semantic annotations.
one line per token.
current_token_id, current_sent_id, token_no, surface, lemma, pos, sense_no, sense_key, ssid, int_dom_token_no, dom_token_id, rel

Any field ending in _id is a unique id. Those ending in _no are relative numbers.
sense_no is the wordnet sense number (as ordered by frequency)
sense_key can be concatenated to the lemma (<lemma>%<sense_key>) to identify a synset.
It maps to a synset offset (ssid), which can change from one wordnet version to another.
We use ssid to identify synsets in the corelex code.

semcor.sent - tab separated file with information about sentences, their location and text.
Anything ending in _id is a unique id. sent_no and para_no are relative to doc. first_token_id
is the id of the first token in the sentence.  text is blank separated tokens. 
sent_id, doc_id, para_no, sent_no, first_token_id, text

"""

from collections import defaultdict
from config import CLDATA_DIR
from config import SEMCOR_DIR
from wordnet import WordNet
import itertools
import pdb
import os
import semcor_cl
from bs4 import BeautifulSoup
import sys

# to reload: >>> from importlib import reload

# create a wordnet object
wn = WordNet('3.1')

def semcor_sent2str(semcor_sent):
    sent_list = [] # one entry per chunk/pos
    sent_str = "" # string of chunks to be returned

    # Work our way through the tree data structure nltk
    # uses to represent tagged chunks.
    #for node in semcor_sent:
     
    # global_sent_no can be used to add new files with output starting at
    # (1 + global_sent_no).  Normally, we'd pass in a file_list and leave
    # the default as 0.  Then the output file will have a constinuous
    # list of sentence numbers starting at 1.
def secmcor_files2tagged_chunks(file_list, tagged_file, lexsn_file, global_sent_no=0):
    with open(lexsn_file, 'w') as lexsn_str:
        with open(tagged_file, 'w') as tagged_str:
            for semcor_file in file_list:
                last_sent_no = semcor_str2tagged_chunks(semcor_file, tagged_str, lexsn_str, global_sent_no)
                # To maintain the sentence number sequence across files,
                # we have to update the global_sent_no with the last_sent_no from
                # the previous file processed.
                global_sent_no = last_sent_no

# uses opened output streams and unopened input file
def semcor_str2tagged_chunks(semcor_file, tagged_str, lexsn_str, global_sent_no=0, delimiter="~"):
    # We will start numbering sentences with 1 to be consistent with
    # Stanford parser output.  We increment whenever we see <s snum...> tag
    # Sentences are numbered uniquely throughout the corpus.  Files
    # must be in lexicographic order to be consistent with nltk semcor 
    # oredering.
    token_list = []
    token_no = 0

    # features to output per chunk
    pos = ""
    word = ""
    lemma = ""
    lexsn = ""

    # these ids are relative to a single file
    # global_sent_no, by contrast, is unique across the corpus
    current_filename = ""
    current_sent_no = "0"
    current_para_no = "0"
    token_no = 0

    # read the input file into beautifulsoup
    handler = open(semcor_file).read()
    soup = BeautifulSoup(handler, 'lxml')

    # <context filename=br-a01 paras=yes>
    current_filename = soup.find_all('context')[0].get('filename')
    print("file: %s" % current_filename)

    # <p pnum=1>
    for para in soup.find_all('p'):
        # current_para_no is paragraph within the document
        current_para_no = para.get('pnum')
        for sent in para.find_all('s'):
            # current_sent_no is sent_no within the document
            current_sent_no = sent.get('snum')
            # global_sent_no is sent_no within the corpus
            global_sent_no += 1

            # initialize token number within a sentence.
            # First token within a sentence will be incremented
            # to 1 later.
            token_no = 0
            #print("\nlexsn:# sent = %i\n" % (sent_no))

            # output a comment with document info for the sentence
            lexsn_str.write("\n#sent %s %s %s %i\n" % (current_filename, current_para_no, current_sent_no, global_sent_no))

            
            # Not every line in a sent is a wf! (some are punc)
            for chunk in sent.find_all():
                token_no += 1

                # features to output per chunk
                # We will update token number based on word != ""
                # So we have to reinitialize our features before
                # each line is processed, so nothing is left over 
                # from the previous line.
                pos = ""
                word = ""
                lemma = ""
                lexsn = ""

                # uncomment for debugging
                #print("line: %s" % chunk)

                # To extract chunks, we have five possible formats for a chunk
                # <wf cmd=ignore pos=DT>The</wf>
                # <wf cmd=done pos=VB lemma=say wnsn=1 lexsn=2:32:00::>said</wf>
                # <wf cmd=done rdf=group pos=NNP lemma=group wnsn=1 lexsn=1:03:00:: pn=group>Fulton_County_Grand_Jury</wf>
                # <wf cmd=done pos=VBP ot=notag>be</wf>
                # <punc>.</punc>

                # Note that a verb can incorporate an adjunct:
                # <wf cmd=done pos=VB lemma=take_place wnsn=1 lexsn=2:30:00::>took_place</wf>

                #pdb.set_trace()

                # handle each chunk type
                if chunk.name == 'punc':
                    word = chunk.text
                    pos = word
                    tagged_str.write("%s%s%s " % (word, delimiter, pos))
                  
                # all other elements should be of type wf

                # "cmd=ignore" seems to indicate prepositions
                elif chunk.get('cmd') == "ignore":
                    # <wf cmd=ignore pos=TO>to</wf>
                    # <wf cmd=ignore dc=-3 pos=RB>on</wf>
                    pos = chunk.get('pos')
                    word = chunk.text
                    # include the token in the sentence we are building
                    tagged_str.write("%s%s%s " % (word, delimiter, pos))

                # all other elements should be words with lemmas ///
                else:
                    # extract the common attributes

                    word = chunk.text
                    lexsn = chunk.get('lexsn')
                    pos = chunk.get('pos')
                    wnsn = chunk.get('wnsn')
                    lemma = chunk.get('lemma')

                    # Idiosyncratic cases...
                    # Check for the case of a group (proper name chunk)
                    # <wf cmd=done rdf=group pos=NNP lemma=group wnsn=1 lexsn=1:03:00:: pn=group>U.S._Cavalry</wf>
                    if lemma == "group":
                        # For named entities, preface the entity type with NE_
                        # and keep this in the lemma field
                        lemma = "NE_" + lemma

                    elif lemma == None:
                        # no lemma or synset
                        # <wf cmd=done pos=VB ot=notag>be</wf>
                        lemma = word
                        
                        # There are some special cases we finesse:
                        # third field (x) is either sep or rdf
                        # rdf is a redefine due to non-adjacent multiword expression
                        # as in "do_justice"
                        # sep is a separator character (such as "-" in west-German)
                        # examples of both are in file br-r08 (Brown1 corpus)
                        # <wf cmd=done sep="-" pos=JJ lemma=west wnsn=1 lexsn=3:00:00::>West</wf>
                        
                    elif chunk.get('pn') == "other":
                        # pn=other
                        # <wf cmd=done pos=NNP pn=other ot=notag>Old_Order</wf>
                        lemma = word
                        
                    elif lemma == None:
                        # This should not occur.  It is a way to check for errors.
                        print("\nERROR: Did not find lemma in: %s\n" % chunk)
                        
                    # Add the token to the sentence we are building up
                    # use ~ as separator, since some words may include "/"
                    tagged_str.write("%s%s%s%s%s " % (word, delimiter, lemma, delimiter, pos))

                    # Also track the lemmas for which we have a sense annotated
                    if lexsn != None:
                        # print("lexsn: %i\t%s\t%s\t%s" % (token_no, word, lemma, lexsn))
                        # get the synset offset (sid) for the lemma_sense key.
                        sid = get_wordnet_sid(wn, lemma, lexsn)

                        if sid == None:
                            # output a nonexistent sid as an empty string
                            # Perhaps at some future point, we may be able to fill this in
                            # with the corresponding wordnet 3.1 synset offset.
                            sid = ""

                        lexsn_str.write("%i\t%s\t%s\t%s\t%s\t%s\n" % (token_no, word, lemma, wnsn, lexsn, sid))

            # end the sentence with a newline.
            # We output one sentence per line.
            tagged_str.write("\n")

    # return the last global_sent_no used
    return(global_sent_no)

# Given a wordnet object and semcor lemma_sense_key, return the synset offset
# if it exists, else return None.  lemma_sense_key 
def get_wordnet_sid(wn, lemma, lexsn):
    lemma_sense_key = "%".join([lemma, lexsn])
    if lemma_sense_key in wn._sense_idx:
        sid = wn._sense_idx[lemma_sense_key]
    else:
        sid = None
    return(sid)


# return a list of semcor files in lexicographic order, with full path.
def get_semcor_filelist():
    path_list = []
    for subdir in ["brown1", "brown2"]:
        path = os.path.join(SEMCOR_DIR, subdir, "tagfiles")
        # Note that nltk semcor routines process the files in lexicographic order.
        # In order for our sentence numbering to match theirs, we have to process
        # the files in the same order.
        sorted_filelist = sorted(os.listdir(path))
        for filename in sorted_filelist:
            path_list.append(os.path.join(path, filename))
    return(path_list)


### Create semcor.sent and semcor.token from semcor.lexsn and semcor.parse
### These files merge data from the two input files
# semcor_parse.create_sent_token_files("semcor.parse.6958", "semcor.lexsn.3605", "sent.subset", "token.subset")
# semcor_parse.run_create()
def run_create():
    """
    test subset:
    parse_file = "semcor.parse.6958"
    lexsn_file = "semcor.lexsn.3605"
    sent_file = "semcor.sent.subset.tsv" 
    token_file = "semcor.token.subset.tsv"
    """

    # run over entire semcor corpus
    parse_file = "semcor.parse"
    lexsn_file = "semcor.lexsn"
    # output .tsv files suitable for input into sqlite
    sent_file = "semcor.sent.tsv" 
    token_file = "semcor.token.tsv"

    create_sent_token_files(parse_file, lexsn_file, sent_file, token_file)

def create_sent_token_files(parse_file, lexsn_file, sent_file, token_file):
    d_sent_id2lexsn = {}
    # #sent br-a11 63 79 258
    # key is sent_id
    # value is [doc_id, para_no, sent_no, sent_id]
    d_sent_id_token2lexsn = {}
    # key is (sent_id, token_no)
    # value is [token_no, surface, lemma, sense_no, sense_key, ssid]
    # read lexsn_file data into dictionaries
    # sent br-a11 64 80 259
    # 1       Two     two     1       5:00:00:cardinal:00     02194109

    lexsn_path = os.path.join(CLDATA_DIR, lexsn_file)
    parse_path = os.path.join(CLDATA_DIR, parse_file)

    sent_path = os.path.join(CLDATA_DIR, sent_file)
    token_path = os.path.join(CLDATA_DIR, token_file)

    print("paths: %s\t%s\n%s\t%s\n" % (lexsn_path, parse_path, sent_path, token_path))

    # Put the lexsn data into two dictionaries, capturing sentence and token info
    for line in open(lexsn_path): 
        line = line.strip('\n')
        # line can be blank, start with #sent or be token info
        if line == "":
            # blank line
            continue
        elif line[0] == "#":
            # sentence info
            (s, doc_id, para_no, sent_no, sent_id) = line.split(" ")
            d_sent_id2lexsn[sent_id] = [doc_id, para_no, sent_no, sent_id]
        else:
            # token info
            (token_no, surface, lemma, sense_no, sense_key, ssid) = line.split("\t")
            d_sent_id_token2lexsn[(sent_id, token_no)] = (token_no, surface, lemma, sense_no, sense_key, ssid)

    #pdb.set_trace()
    # iterate through the .parse output, merging data with the dictionaries and creating
    # global token ids.

    # track the sentence id
    current_sent_id = "0"

    # create token ids, integer starting at 1 (we increment after finding a token)
    current_token_id = 0

    # track the global token_id of the first token in the current sentence
    current_first_token_id = 0

    with open(sent_path, 'w') as sent_str:
        with open(token_path, 'w') as token_str:
            for line in open(parse_path):
                line = line.strip('\n')
                if line == "":
                    # blank line
                    continue
                elif line[0:6] == "# sent":
                    # sentence info
                    (h, s, e, current_sent_id) = line.split(" ") 
                    # increment the current_first_token_id to be the first
                    # token_id in the sentence we have just entered.
                    current_first_token_id = current_token_id + 1
                elif line[0:6] == "# text":
                    # text of sentence is everything beyond "# text = "
                    text = line[9:]
                    # use current_sent_id as key to dictionary and merge and write sentence data
                    (doc_id, para_no, sent_no, sent_id) = d_sent_id2lexsn[current_sent_id]
                    sent_str.write("%s\t%s\t%s\t%s\t%i\t%s\n" % (sent_id, doc_id, para_no, sent_no, current_first_token_id, text))
                else:
                    # token info
                    # d1, d2, d3 are dashes for fields to be ignored.
                    (token_no, surface, lemma, pos, pos2, d1, dom_token_no, rel, d2, d3) = line.split("\t")
                    current_token_id += 1
                    # compute the global token_id for the dominating token
                    # NOTE: if the dominating token is the root (0), then the global
                    # token id will be 0.
                    int_dom_token_no = int(dom_token_no)
                    if int_dom_token_no == 0:
                        dom_token_id = int_dom_token_no
                    else:
                        dom_token_id = (current_first_token_id + int_dom_token_no) - 1

                        # d_sent_id_token2lexsn[(sent_id, token_no)] = (token_no, surface, lemma, sense_no, sense_key, ssid)
                        # check for synset info for the token
                        key = (current_sent_id, token_no)
                        if key in d_sent_id_token2lexsn:
                            (ln_token_no, ln_surface, ln_lemma, sense_no, sense_key, ssid) = d_sent_id_token2lexsn[key]
                        else:
                            sense_no = ""
                            sense_key = ""
                            ssid = ""

                    token_str.write("%i\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%s\t%i\t%i\t%s\n" % (current_token_id, current_sent_id, token_no, surface, lemma, pos, sense_no, sense_key, ssid, int_dom_token_no, dom_token_id, rel))  
        


################# Run various subsets of brown corpus
# semcor_parse.run_semcor()

def run_semcor():
    """ 
    Create .tagged and .lexsn files for the entire
    semcor corpus (brown1, brown2)
    """
    semcor_files = get_semcor_filelist()

    # output files
    tagged_file = CLDATA_DIR + "/semcor.tagged"
    lexsn_file = CLDATA_DIR + "/semcor.lexsn"

    secmcor_files2tagged_chunks(semcor_files, tagged_file, lexsn_file)
    print("wrote to %s, %s\n" % (tagged_file, lexsn_file))

# semcor_parse.test()
def test():
    ifile = "/home/j/anick/DATA/resources/semcor3.0/test/br-a01"
    ofile = "/home/j/anick/DATA/resources/semcor3.0/test/br-a01.tagged"
    secmcor_files2tagged_chunks([ifile], ofile)
    print("wrote to %s\n" % ofile)

# semcor_parse.multi_test()
def multi_test():

    ifile1 = "/home/j/anick/DATA/resources/semcor3.0/test/br-a01"
    ifile2 = "/home/j/anick/DATA/resources/semcor3.0/brown1/tagfiles/br-r08"

    tagged_file = CLDATA_DIR + "/multi2.tagged"
    lexsn_file = CLDATA_DIR + "/multi2.lexsn"

    filelist = [ifile1, ifile2 ]
    secmcor_files2tagged_chunks(filelist, tagged_file, lexsn_file)
    print("wrote to %s, %s\n" % (tagged_file, lexsn_file))

# semcor_parse.mini()
def mini():
    ifile = "/home/j/anick/DATA/resources/semcor3.0/test/mini"
    ofile = "/home/j/anick/DATA/resources/semcor3.0/test/mini.tagged"
    secmcor_files2tagged_chunks([ifile], ofile)
    print("wrote to %s\n" % ofile)

# semcor_parse.test2()
def test2():
    ifile = SEMCOR_DIR + "/test/test2"
    tagged_file = CLDATA_DIR + "/test2.tagged"
    lexsn_file = CLDATA_DIR + "/test2.lexsn"
    secmcor_files2tagged_chunks([ifile], tagged_file, lexsn_file)
    print("wrote to %s, %s\n" % (tagged_file, lexsn_file))

"""
# To parse the tagged output file:
# cdcc
# cat /home/j/anick/DATA/resources/semcor3.0/test/br-a01.tagged | java -jar stanford-nndep-wrapper-1.0-SNAPSHOT-fatjar.jar - > /home/j/anick/DATA/resources/semcor3.0/test/br-a01.out                     
# cat /home/j/anick/DATA/resources/semcor3.0/test/mini.tagged | java -jar stanford-nndep-wrapper-1.0-SNAPSHOT-fatjar.jar > /home/j/anick/DATA/resources/semcor3.0/test/mini.out                     
# The parser does not handle " well.  It seems to do better on '', so we will not
# convert any pairs of quotes into ".

# What about:

[anick@sarpedon tagfiles]$ cat * | grep '"' | more
<wf cmd=done sep="-" pos=JJ lemma=west wnsn=1 lexsn=3:00:00::>West</wf>
What does sep= mean?  This is the only instance.

"""

if __name__ == '__main__':
    
    action = sys.argv[1]
    if action == "extract":
        run_semcor()
    elif action == "merge":
        run_create()
    else:
        print("Argument must be extract or merge")


