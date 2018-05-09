"""


"""


import sys
from wordnet import WordNet, NOUN, VERB
from ansi_codes import BOLD, BLUE, RESET


if sys.version_info.major < 3:
    raise Exception("Python 3 is required.")


class UserLoop(object):

    MAIN_MODE = 0
    SEARCH_MODE = 1
    WORD_MODE = 2
    SYNSET_MODE = 3
    STATS_MODE = 4

    PROMPT = "\n%s>> %s" % (BOLD, RESET)
    
    def __init__(self, wordnet):
        self.wn = wordnet
        self.lemma_idx = wordnet.lemma_idx
        self.synset_idx = wordnet.synset_idx
        self.lemma_idx2 = wordnet.lemma_idx2
        self.synset_idx2 = wordnet.synset_idx2
        self.mode = UserLoop.MAIN_MODE
        self.search_term = None
        self.mapping = []
        self.mapping_idx = {}
        self.choices = []
        self.run()

    def run(self):
        while True:
            print()
            if self.mode == UserLoop.MAIN_MODE:
                self.main_mode()
            elif self.mode == UserLoop.SEARCH_MODE:
                self.search_mode()
            elif self.mode == UserLoop.WORD_MODE:
                self.word_mode()
            elif self.mode == UserLoop.SYNSET_MODE:
                self.synset_mode()
            elif self.mode == UserLoop.STATS_MODE:
                self.stats_mode()
    
    def main_mode(self):
        self.choices = [('s', 'search noun'), ('a', 'show statistics'), ('q', 'quit') ]
        self.print_choices()
        choice = input(UserLoop.PROMPT)
        if choice == 'q':
            exit()
        elif choice == 's':
            self.mode = UserLoop.SEARCH_MODE
        elif choice == 'a':
            self.mode = UserLoop.STATS_MODE
        else:
            print("Not a valid choice")

    def search_mode(self):
        print('\nEnter a noun to search WordNet')
        print('Enter return to go to the home screen')
        choice = input(UserLoop.PROMPT)
        if choice == '':
            self.mode = UserLoop.MAIN_MODE
        else:
            if choice in self.lemma_idx2[NOUN]:
                self.search_term = choice
                self.mode = UserLoop.WORD_MODE
            else:
                print("Not in WordNet")
                
    def word_mode(self):
        #synsets_offsets = self.lemma_idx.get(self.search_term)
        synsets_offsets = self.lemma_idx2[NOUN].get(self.search_term)
        print(synsets_offsets)
        #self.synsets = [self.wn.get_synset(off) for off in synsets_offsets]
        self.synsets = [self.wn.get_noun_synset(off) for off in synsets_offsets]
        self.mapping = list(enumerate(self.synsets))
        self.mapping_idx = dict(self.mapping)
        self.choices = [('s', 'search'), ('h', 'home'), ('q', 'quit') ]
        print("%s%s%s\n" % (BOLD, self.search_term, RESET))
        for count, synset in self.mapping:
            print("[%d]  %s" % (count, synset))
        self.print_choices()
        choice = input(UserLoop.PROMPT)
        if choice == 'q':
            exit()
        if choice == 'h':
            self.mode = UserLoop.MAIN_MODE
        elif choice == 's':
            self.mode = UserLoop.SEARCH_MODE
        elif choice.isdigit() and int(choice) in [m[0] for m in self.mapping]:
            # displaying a synset
            self.synset = self.mapping_idx[int(choice)]
            self.mode = UserLoop.SYNSET_MODE
        else:
            print("Not a valid choice")

    def print_choices(self):
        print()
        for choice, description in self.choices:
            print("[%s]  %s" % (choice, description))

    def synset_mode(self):
        self.synset.pp()
        self.choices = [('b', 'back to the word'), ('s', 'search'), ('h', 'home'), ('q', 'quit') ]
        self.print_choices()
        choice = input(UserLoop.PROMPT)
        if choice == 'b':
            self.mode = UserLoop.WORD_MODE
        elif choice == 's':
            self.mode = UserLoop.SEARCH_MODE
        elif choice == 'h':
            self.mode = UserLoop.MAIN_MODE
        elif choice == 'q':
            exit()
        elif choice.isdigit() and int(choice) in self.synset.mappings:
            self.synset = self.synset.mappings[int(choice)]

    def stats_mode(self):
        print('Synsets without hypernyms:\n')
        for synset in self.synset_idx.values():
            if not synset.hypernyms():
                print(synset)
                #synset.pp_short()
        # printintg the entity tree
        if self.wn.version == '3.1':
            print('\nEntity tree (4 levels deep):\n')
            self.synset_idx.get('00001740').pp_tree(4)
        self.mode = UserLoop.MAIN_MODE


if __name__ == '__main__':

    wn_version = sys.argv[1] if len(sys.argv) > 1 else '3.1'

    # TODO: this should not be hard-coded
    wn_dir = "/DATA/resources/lexicons/wordnet/WordNet-%s/" % wn_version

    if wn_version == '1.5':
        noun_index_file = wn_dir + 'wn15/DICT/NOUN.IDX'
        noun_data_file = wn_dir + 'wn15/DICT/NOUN.DAT'
        verb_index_file = wn_dir + 'wn15/DICT/VERB.IDX'
        verb_data_file = wn_dir + 'wn15/DICT/VERB.DAT'
    elif wn_version in ('3.0', '3.1'):
        noun_index_file = wn_dir + 'dict/index.noun'
        noun_data_file = wn_dir + 'dict/data.noun'
        verb_index_file = wn_dir + 'dict/index.verb'
        verb_data_file = wn_dir + 'dict/data.verb'
    else:
        exit("ERROR: unsupported wordnet version")

    wn = WordNet(wn_version,
                 noun_index_file, noun_data_file,
                 verb_index_file, verb_data_file)
    UserLoop(wn)

