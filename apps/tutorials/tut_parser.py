from par.pyPEG import *
import re
import types
from par import WikiHtmlVisitor, SimpleVisitor

_ = re.compile

class TutGrammar(dict):
    def __init__(self):
        peg, self.root = self._get_rules()
        self.update(peg)
        
    def _get_rules(self):
        #basic
        def ws(): return _(r'\s+')
        def space(): return _(r'[ \t]+')
        def eol(): return _(r'\r\n|\r|\n')
        def seperator(): return _(r'[\.,!?\-$ \t\^]')
    
        #hr
        def hr(): return _(r'\-{4,}'), -2, blankline
    
        #paragraph
        def blankline(): return 0, space, eol
        def identifer(): return _(r'[a-zA-Z_][a-zA-Z_0-9]*', re.U)
        def literal(): return _(r'u?r?"[^"\\]*(?:\\.[^"\\]*)*"', re.I|re.DOTALL)
        def literal1(): return _(r"u?r?'[^'\\]*(?:\\.[^'\\]*)*'", re.I|re.DOTALL)
        def escape_string(): return '\\', _(r'.')
        def op_string(): return _(r'\*|_|~~|\^|,,')
        def op(): return [(-1, seperator, op_string), (op_string, -1, seperator)]
        def string(): return _(r'[^\\\*_\^~ \t\r\n`,]+', re.U)
        def code_string_short(): return '`', _(r'[^`]*'), '`'
        def code_string(): return '{{{', _(r'[^\}\r\n$]*'), '}}}'
        def default_string(): return _(r'\S+', re.U)
        def anchor(): return _(r'\[\['), 0, space, _(r'#'), _(r'\d*'), 0, space, _(r'\]\]')
        def word(): return [anchor, literal, literal1, escape_string, code_string, code_string_short, op, link, string, default_string]
        def words(): return word, -1, [space, word]
        def line(): return words, eol
        def paragraph(): return -2, line, -1, blankline
    
        #pre
        def pre_alt(): return _(r'<code>'), _(r'.+?(?=</code>)', re.M|re.DOTALL), _(r'</code>'), -2, blankline
        def pre_normal(): return _(r'\{\{\{'), 0, space, eol, _(r'.+?(?=\}\}\})', re.M|re.DOTALL), _(r'\}\}\}'), -2, blankline
        def pre(): return [pre_alt, pre_normal]
    
        
        #subject
        def title_text(): return _(r'.+(?= =)', re.U)
#        def subject(): return _(r'\s*.*'), eol, _(r'(?:=|-){4,}'), -2, eol
        def title1(): return _(r'= '), title_text, _(r' ='), -2, eol
        def title2(): return _(r'== '), title_text, _(r' =='), -2, eol
        def title3(): return _(r'=== '), title_text, _(r' ==='), -2, eol
        def title4(): return _(r'==== '), title_text, _(r' ===='), -2, eol
        def title5(): return _(r'===== '), title_text, _(r' ====='), -2, eol
        def title6(): return _(r'====== '), title_text, _(r' ======'), -2, eol
        def title(): return [title6, title5, title4, title3, title2, title1]
    
        #table
        def table_column(): return -2, [space, escape_string, code_string_short, code_string, op, link, _(r'[^\\\*_\^~ \t\r\n`,\|]+', re.U)], _(r'\|\|')
        def table_line(): return _(r'\|\|'), -2, table_column, eol
        def table(): return -2, table_line, -1, blankline
    
        #lists
        def list_leaf_content(): return words, eol
        def list_indent(): return space
        def bullet_list_item(): return list_indent, _(r'\*'), space, list_leaf_content
        def number_list_item(): return list_indent, _(r'#'), space, list_leaf_content
        def list_item(): return [bullet_list_item, number_list_item]
        def list(): return -2, list_item, -1, blankline
    
        #quote
        def quote_line(): return space, line
        def quote(): return -2, quote_line, -1, blankline
            
        #links
        def protocal(): return [_(r'http://'), _(r'https://'), _(r'ftp://')]
        def direct_link(): return protocal, _(r'[\w\d\-\.,@\?\^=%&:/~+#]+')
        def image_link(): return protocal, _(r'.*?(?:\.png|\.jpg|\.gif|\.jpeg)')
        def alt_direct_link(): return _(r'\['), 0, space, direct_link, space, _(r'[^\]]+'), 0, space, _(r'\]')
        def alt_image_link(): return _(r'\['), 0, space, direct_link, space, image_link, 0, space, _(r'\]')
        def mailto(): return 'mailto:', _(r'[a-zA-Z_0-9-@/\.]+')
        def link(): return [alt_image_link, alt_direct_link, image_link, direct_link, mailto], -1, space
        
        #article
        def article(): return 0, ws, -1, [hr, title, pre, table, list, quote, paragraph]
    
        peg_rules = {}
        for k, v in ((x, y) for (x, y) in locals().items() if isinstance(y, types.FunctionType)):
            peg_rules[k] = v
        return peg_rules, article
    
    def parse(self, text, root=None, skipWS=False, **kwargs):
        if not text:
            return ''
        if text[-1] not in ('\r', '\n'):
            text = text + '\n'
        return parseLine(text, root or self.root, skipWS=skipWS, **kwargs)

class TutVisitor(WikiHtmlVisitor):
    tag_class = {
        'table':'table',
        'p':'tutorial_p',
        'pre':'prettyprint pre-scrollable linenums',
    }

    def visit_paragraph(self, node):
        return self.tag('p', self.visit(node).rstrip())
    
    def visit_anchor(self, node):
        if node[0]:
            _id = int(node[2])
        else:
            _id = self.max_id
            self.max_id += 1
        return '<a href="#" rel="%d" class="comment_point"></a>' % _id

r = re.compile(r'\[\[\s*#(\d*)\s*\]\]')
class TutCVisitor(SimpleVisitor):
    def __init__(self):
        self.max_id = 0
        
    def visit_paragraph(self, node):
        content = self.visit(node)
        b = r.match(content)
        if not b:
            content = '[[#]]' + content
        return content
        
    def visit_anchor(self, node):
        _id = int(node[2])
        self.max_id = max(self.max_id, _id)
        return '[[#%d]]' % _id

class TutTextVisitor(SimpleVisitor):
    def __init__(self, max_id):
        self.max_id = max_id + 1
        
    def visit_anchor(self, node):
        if len(node) == 4:
            _id = int(node[2])
        else:
            _id = self.max_id
            self.max_id += 1
        return '[[#%d]]' % _id
    
