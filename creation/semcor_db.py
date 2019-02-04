"""
semcor_db.py contains functions for performing useful queries over the sqlite database
semcor.db, created by create_semcor_db.sh 

semcor.db schema:

sent(sent_id integer primary key, doc_id varchar(10), para_no integer, sent_no integer, first_token_id integer, sentence text)

token(token_id integer primary key, sent_id integer, token_no integer, surface text, lemma text, pos varchar(6), sense_no integer, sense_key text,ssid varchar(10), dom_token_no integer, dom_token_id integer, rel varchar(14) )

Usage:
# open a connection and get a cursor:
c = semcor_db.get_cursor()

# given a cursor, lemma, synset_id (ssid), and relation,
# return a list of [lemma, ssid] pairs for dominating words
r = semcor_db.get_dom_lemma_ssid(c, "victory", "07488581", "dobj")
Example:
>>> r = semcor_db.get_dom_lemma_ssid(c, "victory", "07488581", "dobj")
>>> r
[['give', '01632595'], ['gain', '02293158'], ['describe', '00007846'], ['give', '01632595'], ['total', '02651091']]

Dependencies:
nested_dict package must be installed
"""

from collections import defaultdict
from config import CLDATA_DIR
from wordnet import WordNet
import itertools
import pdb
import os
import semcor_cl
import sys
import sqlite3
from nested_dict import nested_dict

# to reload: >>> from importlib import reload

# c = semcor_db.get_cursor()
def get_cursor():
    "establish a connection to semcor.db and return a connection object"
    database_filename = "semcor.db"

    db_path = os.path.join(CLDATA_DIR, database_filename)
    conn = sqlite3.connect(db_path)
    # set row_factory method to allow access to fields in a row by name
    conn.row_factory = sqlite3.Row
    c = conn.cursor()   
    return(c)
 

#victory|07488581|dobj|
# r = semcor_db.get_dom(c, "victory", "07488581", "dobj")    
def get_dom(c, lemma, ssid, rel):
    # select m.lemma, m.rel, d.lemma, d.ssid from token m inner join token d on m.dom_token_id = d.token_id where m.rel = "dobj";
    sql = "SELECT d.lemma, d.ssid, m.sent_id from token m INNER JOIN token d on m.dom_token_id = d.token_id where m.lemma = ? AND m.ssid = ? AND m.rel = ?"
    args = (lemma, ssid, rel)
    c.execute(sql, args)
    results = c.fetchall()
    """
    for result in results:
        print(result)
    """
    return(results)

# return matches for sense, lemma, or synset, given a list of dominant relations
# Note that in order to place a variable number of ? into the IN clause of the query,
# we have to do this dynamically using the length of the rels list.  Then rels have
# to be added to the list of args for the query.

# rs = semcor_db.get_sense_dom(c, "victory", "07488581", ["dobj", "nsubj"])    
def get_sense_dom(c, lemma, ssid, rels):
    # select m.lemma, m.rel, d.lemma, d.ssid from token m inner join token d on m.dom_token_id = d.token_id where m.rel = "dobj";

    sql = "SELECT d.lemma, d.ssid, m.sent_id, m.rel from token m INNER JOIN token d on m.dom_token_id = d.token_id where m.lemma = ? AND m.ssid = ? AND m.rel IN ("  +   ",".join(["?"]*len(rels))  +  ")"

    args = [lemma, ssid]
    args.extend(rels)
    c.execute(sql, args)
    results = c.fetchall()
    """
    for result in results:
        print(result)
    """
    return(results)

# rss = semcor_db.get_synset_dom(c, "07488581", ["dobj", "nsubj"])    
def get_synset_dom(c, ssid, rels):
    # select m.lemma, m.rel, d.lemma, d.ssid from token m inner join token d on m.dom_token_id = d.token_id where m.rel = "dobj";
    sql = "SELECT d.lemma, d.ssid, m.sent_id, m.rel from token m INNER JOIN token d on m.dom_token_id = d.token_id where m.ssid = ? AND m.rel IN ("  +   ",".join(["?"]*len(rels))  +  ")"
    args = [ssid]
    args.extend(rels)
    c.execute(sql, args)
    results = c.fetchall()
    """
    for result in results:
        print(result)
    """
    return(results)


# rl = semcor_db.get_lemma_dom(c, "victory", ["dobj", "nsubj"])    
def get_lemma_dom(c, lemma, rels):
    # select m.lemma, m.rel, d.lemma, d.ssid from token m inner join token d on m.dom_token_id = d.token_id where m.rel = "dobj";
    sql = "SELECT d.lemma, d.ssid, m.sent_id, m.rel from token m INNER JOIN token d on m.dom_token_id = d.token_id where m.lemma = ? AND m.rel IN ("  +   ",".join(["?"]*len(rels))  +  ")"
    args = [lemma]
    args.extend(rels)
    c.execute(sql, args)
    results = c.fetchall()
    """
    for result in results:
        print(result)
    """
    return(results)


# r = semcor_db.get_sent(c, sent_id)
def get_sent(c, sent_id):
    sql = "SELECT sentence, doc_id, sent_no FROM sent WHERE sent_id = ?" 
    # Note the need to include a trailing comma if the arg list contains only one parameter.
    args = (sent_id, )
    c.execute(sql, args)
    results = c.fetchall()
    """
    for result in results:
        print(result)
    """
    return(results)

# r = semcor_db.get_dom_lemma_ssid(c, "victory", "07488581", "dobj")    
def get_dom_lemma_ssid(c, lemma, ssid, rel):
    rs = get_dom(c, lemma, ssid, rel)
    doms = []
    for r in rs:
        doms.append( [ r['lemma'], r['ssid'] ] )
        
    return(doms)
                    
        

# l_results is a list of result lists, so that we
# can combine counts from multiple lists (as generated by sister synsets,
# for example).  All result lists should be of the same type, however.
# result_type is lemma, sense, or synset
# drl = semcor_db.dictify_mult([rss], 'synset')

def dictify_mult(l_results, result_type):
    nd = nested_dict(2, int)
    for each_results in l_results:
        for row in each_results:
            #pdb.set_trace()
            rel = row['rel']
            if result_type == 'lemma':
                type_instance = row['lemma']
            elif result_type == 'synset':
                type_instance = row['ssid']
            elif result_type == 'sense':
                type_instance = (row['lemma'], row['ssid'])
            nd[rel][type_instance] += 1

    for key1 in nd.keys():
        sub_dic = nd[key1]
        print("key: %s" % key1)
        for key2 in sub_dic.keys():
            print("%s: %i" % (key2, sub_dic[key2]))

    return(nd)

# dictify a single result
def dictify(results, result_type):
    nd = nested_dict(2, int)
    for row in results:
        #pdb.set_trace()
        rel = row['rel']
        if result_type == 'lemma':
            type_instance = row['lemma']
        elif result_type == 'synset':
            type_instance = row['ssid']
        elif result_type == 'sense':
            type_instance = (row['lemma'], row['ssid'])
        nd[rel][type_instance] += 1

    for key1 in nd.keys():
        sub_dic = nd[key1]
        print("key: %s" % key1)
        for key2 in sub_dic.keys():
            print("%s: %i" % (key2, sub_dic[key2]))

    return(nd)

        

                             
