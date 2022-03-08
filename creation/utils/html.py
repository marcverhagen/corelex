import os

import cltypes
from wordnet import expand, POINTER_SYMBOLS

class RelationsWriter(object):

    def __init__(self, corelex_version, basic_type_relations):
        self.corelex_version = corelex_version
        self.btr = basic_type_relations
        self.html_dir = "data/corelex-%s-relations-%ss-basic-types" \
                        % (self.corelex_version, expand(self.btr.category))
                        #% (self.btr.version, expand(self.btr.category))
        self.rels_dir = os.path.join(self.html_dir, 'rels')
        self.index_file = os.path.join(self.html_dir, "index.html")
        self.basic_types = cltypes.get_basic_types(self.btr.version)

    def write(self):
        self._ensure_directories()
        with open(self.index_file, 'w') as fh:
            categories = self.btr.distribution.get_categories()
            fh.write("<html>\n")
            self._write_head(fh)
            fh.write("<body>\n")
            self._write_symbol_table(fh, categories)
            fh.write("<table cellpadding=5 cellspacing=0 border=1>\n")
            fh.write("<tr align=center>\n")
            fh.write("  <td>&nbsp;</td>\n")
            fh.write("  <td>&nbsp;</td>\n")
            for cat in categories:
                fh.write("  <td width=30>%s</td>\n" % cat)
            fh.write("</tr>\n")
            for pair in sorted(self.btr.btrels2):
                cells = self.btr.btrels2[pair]
                cell_categories = set([cell.category for cell in cells])
                bt1, bt2 = pair
                fh.write("<tr align=left>\n")
                name = "%s-%s" % (bt1, bt2)
                fh.write("  <td><a href=rels/%s.html><code>%s</code></a></td>\n"
                         % (name, name))
                fh.write("  <td>%s - %s</td>\n"
                         % (_full_name(bt1), _full_name(bt2)))
                for cat in categories:
                    val = "&check;" if cat in cell_categories else "&nbsp;"
                    fh.write("  <td align=center>%s</td>\n" % val)
                fh.write("</tr>\n")
                self._write_relation(bt1, bt2, name, cells)
            fh.write("</table>\n")

    def _write_symbol_table(self, fh, categories):
        fh.write("<table cellpadding=5 cellspacing=0 border=1>\n")
        # there are 12 categoeirs and I want them in two columns
        for i in range(6):
            cat1 = categories[i]
            cat2 = categories[i+6]
            fh.write("<tr align=left>\n")
            fh.write("  <td>%s</td>\n" % cat1)
            fh.write("  <td>%s</td>\n" % POINTER_SYMBOLS.get(cat1))
            fh.write("  <td>%s</td>\n" % cat2)
            fh.write("  <td>%s</td>\n" % POINTER_SYMBOLS.get(cat2))
            fh.write("</tr>\n")
        fh.write("</table><p/>\n")

    def _write_head(self, fh):
        fh.write("<head>\n")
        fh.write("<style>\n")
        fh.write("a:link { text-decoration: none; }\n")
        fh.write("a:visited { text-decoration: none; }\n")
        fh.write("a:hover { text-decoration: underline; }\n")
        fh.write("a:active { text-decoration: underline; }\n")
        fh.write(".blue { color: blue; }\n")
        fh.write(".green { color: green; }\n")
        fh.write("dd { margin-bottom: 20px; }\n")
        fh.write("code { font-size: larger; }\n")
        fh.write("</style>\n</head>\n")

    def _ensure_directories(self):
        if not os.path.exists(self.html_dir):
            os.makedirs(self.html_dir)
            os.makedirs(self.rels_dir)

    def _write_relation(self, bt1, bt2, name, cells):
        fname = os.path.join(self.rels_dir, name + '.html')
        with open(fname, 'w') as fh:
            fh.write("<html>\n")
            self._write_head(fh)
            fh.write("<body>\n")
            fh.write("<h2>%s-%s</h2>\n" % (bt1, bt2))
            self._write_pair_description(fh, bt1, bt2)
            fh.write('<p>Relations:')
            for cell in cells:
                fh.write(" [<a href=#%s>%s</a>]"
                         % (cell.category, POINTER_SYMBOLS.get(cell.category)))
            fh.write('</p>')
            for cell in cells:
                fh.write("<a name=%s></a>\n" % cell.category)
                fh.write("<p>&bullet; %s  (%s)</p>\n"
                         % (POINTER_SYMBOLS.get(cell.category), cell.category))
                rels = self.btr.allrels[name]
                grouped_rels = {}
                for rel in rels:
                    # If we skip this test we get a problem when, for example,
                    # we have <ss1 #s ss2> and <ss2 %s ss1>. In that case the
                    # results will also show <ss1 %s ss2> and <ss2 #s ss1>.
                    if rel[1] == cell.category:
                        source = rel[3]
                        target = rel[4]
                        grouped_rels.setdefault(source.id, [source, []])
                        grouped_rels[source.id][1].append(target)
                fh.write("<blockquote>\n<dl>\n")
                for synset_id in grouped_rels:
                    source, targets = grouped_rels[synset_id]
                    fh.write("  <dt>%s</dt>\n" % source.as_html())
                    fh.write("  <dd>\n")
                    for target in targets:
                        fh.write("%s<br/>" % target.as_html())
                    fh.write("  </dd>\n")
                fh.write("</dl>\n</blockquote>\n")

    def _write_pair_description(self, fh, bt1, bt2):
        fh.write('<p>{')
        for offset, synset in self.basic_types.get(bt1):
            fh.write(' %s' % synset)
        fh.write(' } &bullet; {')
        for offset, synset in self.basic_types.get(bt2):
            fh.write(' %s' % synset)
        fh.write('}</p>\n')


def _full_name(basic_type):
    return cltypes.BASIC_TYPES.get(basic_type)
