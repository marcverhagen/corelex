def index_file(wn_dir, version, cat):
    """Return the relative path of the file in the WordNet distribution."""
    if version == '1.5':
        subdir = 'wn15/DICT/'
        fname = "%s.IDX" % cat.upper()
    else:
        subdir = 'DICT/'
        fname = "index.%s" % cat
    return wn_dir + subdir + fname


def data_file(wn_dir, version, cat):
    """Return the relative path of the file in the WordNet distribution."""
    if version == '1.5':
        subdir = 'wn15/DICT/'
        fname = "%s.DAT" % cat.upper()
    else:
        subdir = 'DICT/'
        fname = "data.%s" % cat
    return wn_dir + subdir + fname

def sense_file(wn_dir, version):
    """Return the relative path of the index.sense file in the WordNet distribution."""
    if version == '1.5':
        subdir = 'wn15/DICT/'
        fname = "index.sense"
    else:
        subdir = 'DICT/'
        fname = "index.sense"
    return wn_dir + subdir + fname


def flatten(some_list):
    result = []
    for element in some_list:
        if isinstance(element, list):
            result.extend(flatten(element))
        else:
            result.append(element)
    return result


# for more color codes see
# https://gist.github.com/chrisopedia/8754917

BLACK = '\u001b[30m'
WHITE = '\u001b[37m'
GRAY = '\u001b[1;37m'

RED = '\u001b[31m'
GREEN = '\u001b[32m'
YELLOW = '\u001b[33m'
BLUE = '\u001b[34m'
MAGENTA = '\u001b[35m'
CYAN = '\u001b[36m'

BOLD = '\u001b[1m'
UNDERLINE = '\u001b[4m'

RESET = '\u001b[0m'


def blue(text):
    return "%s%s%s" % (BLUE, text, RESET)

def green(text):
    return "%s%s%s" % (GREEN, text, RESET)

def red(text):
    return "%s%s%s" % (RED, text, RESET)

def cyan(text):
    return "%s%s%s" % (CYAN, text, RESET)

def magenta(text):
    return "%s%s%s" % (MAGENTA, text, RESET)

def yellow(text):
    return "%s%s%s" % (YELLOW, text, RESET)

def bold(text):
    return "%s%s%s" % (BOLD, text, RESET)

def boldgreen(text):
    return "%s%s%s%s" % (BOLD, GREEN, text, RESET)


if __name__ == '__main__':

    print(blue('blue'))
    print(green('green'))
    print(red('red'))
    print(magenta('magenta'))
    print(cyan('cyan'))
    print(yellow('yellow'))
    
