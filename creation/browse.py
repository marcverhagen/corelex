"""

Command line browser for WordNet, includes added CoreLex basic types for nouns.

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
    system will always be in a particular mode, which on initialization is the
    main mode. Each mode is associated with a method and that method does three
    things:

    1. Perform some action. For example, in synset mode the synset is printed to
       the terminal. This action can be empty.

    2. Print choices for next steps to the terminal. This tells the user what
       the next action in the user loop can be. This sollicits user input. If
       the next mode is the main mode than no choices need to be given since the
       main mode starts with printing choices.

    3. Determine what the next mode is given the user response. This includes
       changing the mode if needed.

    """

    MAIN_MODE = 'MAIN_MODE'
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
                self._main_mode()
            elif self.mode == UserLoop.WORD_MODE:
                self._word_mode()
            elif self.mode == UserLoop.SYNSET_MODE:
                self._synset_mode()
            elif self.mode == UserLoop.STATS_MODE:
                self._stats_mode()
    
    def _main_mode(self):
        self._action_print_choices(search(self.category), stats(), end())
        choice = input(UserLoop.PROMPT)
        if choice == 'q':
            exit()
        elif choice.startswith('s '):
            self._action_search(choice)
        elif choice == 'a':
            self.mode = UserLoop.STATS_MODE
        else:
            print("Not a valid choice")

    def _word_mode(self):
        self._action_print_synsets()
        self._action_print_choices(search(self.category), home(), end())
        choice = input(UserLoop.PROMPT)
        if choice == 'q':
            exit()
        if choice == 'h':
            self.mode = UserLoop.MAIN_MODE
        elif choice.startswith('s '):
            self._action_search(choice)
        elif choice.isdigit() and int(choice) in [m[0] for m in self.mapping]:
            # use the choice to save the synset before changing the mode
            self.synset = self.mapping_idx[int(choice)]
            self.mode = UserLoop.SYNSET_MODE
        else:
            print("Not a valid choice")

    def _synset_mode(self):
        self.synset.pp()
        self._action_print_choices(back(), search(self.category), home(), end())
        choice = input(UserLoop.PROMPT)
        if choice == 'b':
            self.mode = UserLoop.WORD_MODE
        elif choice.startswith('s '):
            self._action_search(choice)
        elif choice == 'h':
            self.mode = UserLoop.MAIN_MODE
        elif choice == 'q':
            exit()
        elif choice.isdigit() and int(choice) in self.synset.mappings:
            self.synset = self.synset.mappings[int(choice)]

    def _stats_mode(self):
        self._action_print_statistics()
        self.mode = UserLoop.MAIN_MODE

    def _action_search(self, choice):
        search_term = choice[2:].strip().replace(' ', '_')
        if search_term in self.lemma_idx[self.category]:
            self.search_term = search_term
            self.mode = UserLoop.WORD_MODE
        else:
            print("Not in WordNet")

    def _action_print_synsets(self):
        word = self.lemma_idx[self.category].get(self.search_term)
        self.synsets = [self.wn.get_synset(self.category, off) for off in word.synsets]
        self.mapping = list(enumerate(self.synsets))
        self.mapping_idx = dict(self.mapping)
        print("%s\n" % bold(self.search_term))
        for count, synset in self.mapping:
            print("[%d]  %s" % (count, synset.as_formatted_string()))

    def _action_print_statistics(self):
        print('Synsets without hypernyms:\n')
        count = 0
        for synset in self.synset_idx[self.category].values():
            if not synset.hypernyms():
                count += 1
                print(synset)
        print("\nNumber of synsets without hypernym: %d\n" % count)
        # printing the entity tree
        if self.category == NOUN and self.wn.version == '3.1':
            print('\nEntity tree (4 levels deep):\n')
            self.synset_idx[NOUN].get('00001740').pp_tree(4)

    def _action_print_choices(self, *args):
        print()
        for choice, description in args:
            print(">> %-6s  -  %s" % (choice, description))


def home():
    return ('h', 'home')

def stats():
    return ('a', 'show statistics')

def end():
    return ('q', 'quit')

def back():
    return ('b', 'back to the word')

def search(category):
    return ('s ' + category, 'search for the word')


if __name__ == '__main__':

    wn_version = sys.argv[1]
    category = sys.argv[2]
    if not wn_version in ('1.5', '3.1'):
        exit("ERROR: unsupported wordnet version")

    wn = WordNet(wn_version, add_basic_types=True)
    UserLoop(wn, category)
