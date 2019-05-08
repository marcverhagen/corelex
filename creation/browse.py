"""

Command line browser for WordNet, including added CoreLex basic types for nouns.

Usage:

    $ python3 browse.py <version> <category>

    <version> is 1.5 or 3.1
    <category> is noun or verb

"""


import sys
from wordnet import WordNet, NOUN, VERB, expand
from utils import index_file, data_file, bold


if sys.version_info.major < 3:
    raise Exception("Python 3 is required.")


class UserLoop(object):

    """For user interaction via the command line. The way this works is that the
    system will always be in a particular, which on initialization is the main
    mode. Each mode is associated with a method and that method does three
    things:

    1. Perform some action. For example, in synset mode the synset is printed to
       the terminal. This action can be empty.

    2. Print choices for next steps to the terminal. This tells the user what
       the next action in the user loop can be. The last part here is to
       sollicit the user's choice.

    3. Determine what the next mode is given the user response. This includes
       changing th emode if needed.

    """
    
    MAIN_MODE = 'MAIN_MODE'
    SEARCH_MODE = 'SEARCH_MODE'
    WORD_MODE = 'WORD_MODE'
    SYNSET_MODE = 'SYNSET_MODE'
    STATS_MODE = 'STATS_MODE'

    PROMPT = "\n%s " % bold('>>')
    
    def __init__(self, wordnet, category):
        self.wn = wordnet
        self.category = expand(category)
        self.lemma_idx = wordnet.lemma_index()
        self.synset_idx = wordnet.synset_index()
        self.mode = UserLoop.MAIN_MODE
        self.search_term = None
        self.mapping = []
        self.mapping_idx = {}
        self.choices = []
        self.run()

    def run(self):
        """The loop itself. Keep executing the method associated with the current
        mode. Breaking out of the loop happens inside the mode methods using the
        exit() method."""
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
        self.choices = [('s', 'search ' + self.category), ('a', 'show statistics'), ('q', 'quit') ]
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
        print('\nEnter a %s to search WordNet' % self.category)
        print('Enter return to go to the home screen')
        choice = input(UserLoop.PROMPT)
        if choice == '':
            self.mode = UserLoop.MAIN_MODE
        else:
            choice = choice.replace(' ', '_')
            if choice in self.lemma_idx[self.category]:
                self.search_term = choice
                self.mode = UserLoop.WORD_MODE
            else:
                print("Not in WordNet")
                
    def word_mode(self):
        #synsets_offsets = self.lemma_idx[self.category].get(self.search_term)
        word = self.lemma_idx[self.category].get(self.search_term)
        #self.synsets = [self.wn.get_synset(self.category, off) for off in synsets_offsets]
        self.synsets = [self.wn.get_synset(self.category, off) for off in word.synsets]
        self.mapping = list(enumerate(self.synsets))
        self.mapping_idx = dict(self.mapping)
        self.choices = [('s', 'search'), ('h', 'home'), ('q', 'quit') ]
        print("%s\n" % bold(self.search_term))
        for count, synset in self.mapping:
            print("[%d]  %s" % (count, synset.as_formatted_string()))
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
        count = 0
        for synset in self.synset_idx[self.category].values():
            if not synset.hypernyms():
                count += 1
                print(synset)
                #synset.pp_short()
        print("\nNumber of synsets without hypernym: %d\n" % count)
        # printing the entity tree
        if self.category == NOUN and self.wn.version == '3.1':
            print('\nEntity tree (4 levels deep):\n')
            self.synset_idx[NOUN].get('00001740').pp_tree(4)
        self.mode = UserLoop.MAIN_MODE

    def print_choices(self):
        print()
        for choice, description in self.choices:
            print("[%s]  %s" % (choice, description))


if __name__ == '__main__':

    wn_version = sys.argv[1]
    category = sys.argv[2]
    if not wn_version in ('1.5', '3.1'):
        exit("ERROR: unsupported wordnet version")

    wn = WordNet(wn_version, category)
    if expand(category) == NOUN:
        wn._add_nominal_basic_types()
    UserLoop(wn, category)
