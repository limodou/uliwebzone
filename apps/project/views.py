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
    
import re
re_at = re.compile(u'@[a-zA-Z0-9_\u4E00-\u9FFF\.]+')
def forumpost_post_save(sender, instance, created, data, old_data):
    """
    处理论坛发贴时当有@用户时发送消息进行通知
    """
    from uliweb.orm import get_model
    from uliweb import request
    
    content = instance.content
    User = get_model('user')
    
    message = u"""用户 %s 在论坛提到了你，查看: <a href="/forum/id/%d">%s</a>""" % (unicode(instance.posted_by), instance.id, unicode(instance.topic.subject))
    for x in re_at.findall(content):
        user = User.get(User.c.username==x[1:])
        if user and user.id != request.user.id:
            functions.send_message(instance.posted_by, user, message, type='2')
    