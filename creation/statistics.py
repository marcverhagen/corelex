
counts = {}
bt_counts = {}
for line in open('corelex.tab'):
    (cl_class, words) = line.strip().split("\t")
    count = len(words.split())
    counts[count] = counts.get(count, 0) + 1
    bt_count = len(cl_class.split())
    bt_counts[bt_count] = bt_counts.get(bt_count, 0) + 1

print "SIZE OF CLASS"
for count in sorted(counts.keys()):
    print("%d %d" % (count, counts[count]))

print "BASIC TYPES IN CLASS"
for count in sorted(bt_counts.keys()):
    print("%d %d" % (count, bt_counts[count]))
