
class Distribution(object):

    """A Distribution has counts and probabilities for all categories. In addition,
    you can ask a Distribution to calculate its chi-square statistic."""
    
    def __init__(self, name):
        self.name = name
        self.counts = {}
        self.probabilities = {}
        self.observations = 0
        self.categories = 0
        self.df = None               # degree of freedom (number_of_categories - 1)
        self.null_hypothesis = None  # to be set to a Distribution
        self.X2_table = None         # table with observed and expected values
        self.X2_statistic = None     # the statistic that we are after

    def __str__(self):
        return "<Distribution %s categories=%s observations=%s>" \
            % (self.name, self.categories, self.observations)

    def get_count(self, value):
        return self.counts.get(value, 0)

    def get_probability(self, value):
        return self.probabilities.get(value, 0)

    def get_categories(self):
        return sorted(self.counts.keys())

    def add(self, value, count):
        self.counts[value] = self.counts.get(value, 0) + count

    def finish(self):
        self.observations = sum(self.counts.values())
        self.categories = len(self.counts.values())
        self.df = self.categories - 1 
        for value, count in self.counts.items():
            self.probabilities[value] = count / self.observations

    def chi_squared(self, distribution):
        self.null_hypothesis = distribution
        self.X2_table = {}
        for cat in self.null_hypothesis.get_categories():
            self.X2_table[cat] = ChiSquaredCell(cat, self, distribution)
        self.X2_statistic = sum([c.component() for c in self.X2_table.values()])
        return self.X2_statistic

    def pp(self):
        print(self)
        count = 0
        for value in sorted(self.counts):
            if count % 6 == 0:
                print()
            count += 1
            print("   %3s  %.5f" % ( value, self.probabilities[value]), end='')
        print('\n')

    def pp2(self):
        print(self, '\n')
        x2 = '' if self.X2_statistic is None else "%.2f" % self.X2_statistic
        print("   X2 = %s\n" % x2)
        for cell in self.X2_table.values():
            print('  ', cell)
        print('\n')

        

class ChiSquaredCell(object):

    def __init__(self, cat, distribution, null_hypothesis):
        self.category = cat
        self.observed = distribution.get_count(cat)
        self.expected = null_hypothesis.get_probability(cat) * distribution.observations

    def component(self):
        """The chi-square component of the cell."""
        return ((self.observed - self.expected) ** 2) / self.expected

    def __str__(self):
        return "[%3s   %6d   %7s   %8s   %8s ]" \
            % (self.category, self.observed, "%4.2f" % self.expected,
               "%5.2f" % (self.observed - self.expected), "%5.2f" % self.component())




def count_classes():
    """Old method for some basic statistics, uses the wrong filenames."""
    
    counts = {}
    bt_counts = {}
    for line in open('corelex.tab'):
        (cl_class, words) = line.strip().split("\t")
        count = len(words.split())
        counts[count] = counts.get(count, 0) + 1
        bt_count = len(cl_class.split())
        bt_counts[bt_count] = bt_counts.get(bt_count, 0) + 1

    print("SIZE OF CLASS")
    for count in sorted(counts.keys()):
        print("%d %d" % (count, counts[count]))

    print("BASIC TYPES IN CLASS")
    for count in sorted(bt_counts.keys()):
        print("%d %d" % (count, bt_counts[count]))
