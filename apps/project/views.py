#coding=utf-8
from uliweb import expose, functions

@expose('/')
def index():
    return redirect('/forum')

def post_save(sender, instance, created, data, old_data):
    """
    用来处理教程某个章节被评论时发送消息通知的处理
    """
    from uliweb import request
    from uliweb.utils.textconvert import text2html
    
    authors = instance.chapter.tutorial.authors.ids()
    if request.user.id in authors:
        authors.remove(request.user.id)
    
    message = u"""<p>%s 评论了教程 《<a href="/tutorial/view_chapter/%d">%s</a>》</p>
%s
""" % (unicode(instance.modified_user), instance._chapter_, unicode(instance.chapter),
    text2html(instance.content))
    functions.send_message(request.user, authors, message, type='2')