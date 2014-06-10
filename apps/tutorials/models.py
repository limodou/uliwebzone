#coding=utf8

from uliweb.orm import *
from uliweb.i18n import ugettext_lazy as _
from datetime import datetime
from uliweb.utils.common import get_var

def get_modified_user():
    from uliweb import request
    
    return request.user.id

class Tutorials(Model):
    __verbose_name__ = '教程'
    
    title = Field(str, max_length=255, verbose_name='标题', nullable=False, required=True)
    creator = Reference('user', verbose_name='创建者', collection_name='creator_tutorials')
    authors = ManyToMany('user', verbose_name='共同作者', nullable=False, collection_name='authors_tutorials')
    create_date = Field(datetime, verbose_name='创建时间', nullable=False, auto_now_add=True)
    modified_user = Reference('user', verbose_name='修改人', collection_name="user_tutorials")
    modified_date = Field(datetime, verbose_name='修改时间')
    hits = Field(int, verbose_name='点击次数')
    votes = Field(int, verbose_name='支持票数')
    image = Field(FILE, max_length=255, verbose_name='封面图片')
    summary = Field(TEXT, verbose_name='介绍', default='', nullable=False)
    deleted = Field(bool, verbose_name='删除标志')
    last_comment_user = Reference('user', verbose_name='最后评论人')
    last_comment_date = Field(datetime, verbose_name='最后评论时间')
    comments_count = Field(int, verbose_name='评论条数', default=0, server_default='0')
    
    def __unicode__(self):
        return self.title
    
    class AddForm:
        fields = ['title', 'authors', 'summary']
        
    class EditForm:
        fields = ['title', 'authors', 'summary']
        
    class Table:
        fields = ['id', 'title', 'author', 'image', 'modified_date', 'comments_count',
            'summary', 'hits',
            ]

    def get_image(self):
        from uliweb import functions
        
        if self.image:
            return functions.get_href(self.image)
        else:
            return functions.url_for_static('tutorials/default_book.png')
    
class Tutorials_Chapters(Model):
    __verbose_name__ = '章节'
    
    tutorial = Reference('tutorials', verbose_name='所属教程', collection_name='turotial_chapters')
    parent = SelfReference(verbose_name='上级章节', collection_name='children_chapters')
    title = Field(str, max_length=255, verbose_name='标题', required=True)
    order = Field(int, verbose_name='顺序号')
    content = Field(TEXT, verbose_name='内容', default='', nullable=False, required=True)
    format = Field(CHAR, max_length=1, verbose_name='格式', choices=get_var('TUTORIALS/format'), default='2')
    render = Field(CHAR, max_length=1, verbose_name='渲染器', choices=get_var('TUTORIALS/render'), default='1')
    html = Field(TEXT, verbose_name='显示内容', default='', nullable=False)
    modified_user = Reference('user', verbose_name='修改人')
    modified_date = Field(datetime, verbose_name='修改时间')
    hits = Field(int, verbose_name='点击次数')
    votes = Field(int, verbose_name='支持票数')
    deleted = Field(bool, verbose_name='删除标志')
    chars_count = Field(int, verbose_name='字节数', default=0, server_default='0')
    comments_count = Field(int, verbose_name='评论条数', default=0, server_default='0')
    #enable_para_comment = Field(bool, verbose_name='是否打开段落评论', default=True)
    theme = Field(CHAR, max_length=1, verbose_name='代码块样式', choices=get_var('TUTORIALS/theme'), default='1')
    linenum = Field(bool, verbose_name='行号显示')
    scrollable = Field(bool, verbose_name='代码滚动')
    
    def __unicode__(self):
        return self.title
    
    class AddForm:
        fields = ['title', 'content', 'format', 'render', 'theme', 'scrollable']
    
    class EditForm:
        fields = ['title', 'content', 'format', 'render', 'theme', 'scrollable']

    @classmethod
    def OnInit(cls):
        Index('tutchp_indx', cls.c.tutorial, cls.c.parent, cls.c.order)

class Tutorials_Chapters_Comments(Model):
    __verbose_name__ = '评论'
    
    chapter = Reference('tutorials_chapters', verbose_name='所属章节')
    parent = SelfReference(verbose_name='上级', collection_name='children_comments')
    anchor = Field(int, verbose_name='定位点', default=0)
    content = Field(TEXT, verbose_name='内容', required=True)
    vote = Field(int, verbose_name='投票')
    modified_user = Reference('user', verbose_name='留言人', default=get_modified_user, auto=True, auto_add=True)
    modified_date = Field(datetime, verbose_name='留言时间', auto_now=True, auto_now_add=True)
    deleted = Field(bool, verbose_name='删除标志')
    
    class AddForm:
        fields = ['content']
    
    @classmethod
    def OnInit(cls):
        Index('tutchpcmt_indx', cls.c.chapter, cls.c.parent, cls.c.anchor)
    
class Tutorials_Albums(Model):
    __verbose_name__ = '像册'
    
    tutorial = Reference('tutorials', verbose_name='所属教程', collection_name='turotial_images')
    filename = Field(FILE, verbose_name='图片')
    created_on = Field(datetime, verbose_name='创建时间', auto_now_add=True)
    
class Tutorials_Category(Model):
    __verbose_name__ = '分类'
    name = Field(str, max_length=255, verbose_name='类名', required=True)
    created_on = Field(datetime, verbose_name='创建时间', auto_now_add=True)
    tutorials = ManyToMany('Tutorials', verbose_name='教程', nullable=False, collection_name='authors_tutorials')
