class CorelexStatistics(object):

    """Store, update and print some statistics."""

    def __init__(self):
        self.total = 0
        self.is_singleton = 0
        self.has_cltype = 0
        self.no_cltype = 0

    def update(self, lemma, type_signature, corelex_type):
        #if '.' in type_signature:
        #    print(lemma, ':', type_signature, '-->', corelex_type)
        self.total += 1
        if '.' not in type_signature:
            self.is_singleton += 1
        if corelex_type == '-':
            self.no_cltype += 1
        else:
            self.has_cltype += 1

    def pp(self):
        def formatted(n):
            return "%8s" % "{:,}".format(n)
        singletons = formatted(self.is_singleton)
        polysemous = formatted(self.total - self.is_singleton)
        with_mapping = formatted(self.has_cltype - self.is_singleton)
        no_mapping = formatted(self.no_cltype)
        print("\nLoaded %d lemmas from semcor\n" % self.total)
        print("  lemmas with a singleton type:           %s" % singletons)
        print("  lemmas with a polysemous type:          %s" % polysemous)
        print("  lemmas with mapping to corelex type:    %s" % with_mapping)
        print("  lemmas without mapping to corelex type: %s\n" % no_mapping)


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
