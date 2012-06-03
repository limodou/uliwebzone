#coding=utf8
from par.pyPEG import *
import re
import types
from par import SimpleVisitor
from par.md import MarkdownGrammar, MarkdownHtmlVisitor, MarkdownTextVisitor

_ = re.compile

r = re.compile(r'^\[\[\s*#(\d*)\s*\]\]')

class TutVisitor(MarkdownHtmlVisitor):
    tag_class = {
        'table':'table',
        'p':'tutorial_p',
        'pre':'prettyprint pre-scrollable linenums',
    }
    
    def __init__(self, template=None, tag_class=None, grammar=None, title='Untitled', max_id=1):
        super(TutVisitor, self).__init__(template, tag_class, grammar, title)
        self.max_id = max_id

    def visit_paragraph(self, node):
        def f(match):
            _id = match.group(1)
            if _id:
                _id = int(_id)
            else:
                _id = self.max_id
                self.max_id += 1
            return '<a href="#" rel="%d" class="comment_point"></a>' % _id
        return r.sub(f, node)
    
class RevealVisitor(MarkdownHtmlVisitor):
    def __init__(self, template=None, tag_class=None, grammar=None):
        super(RevealVisitor, self).__init__(template, tag_class, grammar=grammar)
        self.section2 = False
        self.section3 = False
        
    def visit_title2(self, node):
        b = ''
        if self.section3:
            b = '</section>\n'
        if self.section2:
            b = b + '</section>\n<section>\n'
        else:
            b = b + '<section>\n'
        self.section2 = True
        self.section3 = False
        return b + self.tag('h2', node.find('title_text').text)
    
    def visit_title3(self, node):
        b = ''
#        if self.section2:
#            b = '</section>\n'
        if self.section3:
            b = b + '</section>\n<section>\n'
        else:
            b = b + '<section>\n'
        self.section3 = True
        return b + self.tag('h3', node.find('title_text').text)

    def __end__(self):
        text = super(RevealVisitor, self).__end__()
        if self.section3:
            text += '</section>\n'
        if self.section2:
            text += '</section>\n'
        return text
        
class TutCVisitor(MarkdownTextVisitor):
    def __init__(self, grammar=None):
        super(TutCVisitor, self).__init__(grammar)
        self.max_id = 0
        
    def visit_paragraph(self, node):
        b = r.match(node)
        if not b:
            node = '[[#]] ' + node
        else:
            _id = b.group(1)
            self.max_id = max(self.max_id, int(_id))
        return node
    
    def visit_line(self, node):
        self.paragraph.append(self.visit(node))
        return ''
        
class TutTextVisitor(MarkdownTextVisitor):
    def __init__(self, max_id, grammar):
        super(TutTextVisitor, self).__init__(grammar)
        self.max_id = max_id + 1
        self.paragraph = []
        
    def visit_paragraph(self, node):
        def f(match):
            _id = match.group(1)
            if _id:
                _id = int(_id)
            else:
                _id = self.max_id
                self.max_id += 1
            return '[[#%d]]' % _id
        return r.sub(f, node)

    def visit_line(self, node):
        self.paragraph.append(self.visit(node))
        return ''
    
if __name__ == '__main__':
    text = """
## Web的挑战
* 前端展示
* 后端处理
* 异步处理
* 批量处理

## 前端展示 ##
### html5 ###
増加了更多的语义，如article, section, sidebar, header, footer等，増加了视频支持，本地存储，canvas，websocket等。 http://slides.html5rocks.com

```
<!DOCTYPE html>
```
"""
    g = MarkdownGrammar()
    result, rest = g.parse(text, resultSoFar=[], skipWS=False)
#    print rest.encode('gbk'), result[0].render()
#    t = TutCVisitor(g)
#    new_text = t.visit(result, True)
#    print new_text, t.max_id
    
#    result, rest = g.parse(new_text, resultSoFar=[], skipWS=False)
    print rest.encode('gbk'), result[0].render()
    result = RevealVisitor(grammar=g).visit(result, True)
#    result = TutTextVisitor(t.max_id, g).visit(result, True)
    print 'xxxxxxxxxxxxxx', result
    