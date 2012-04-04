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
    creator = Reference('user', verbose_name='创建者', collection_name='user_tutorials')
    authors = ManyToMany('user', verbose_name='共同作者', nullable=False, collection_name='authors_tutorials')
    create_date = Field(datetime, verbose_name='创建时间', nullable=False, auto_now_add=True)
    modified_date = Field(datetime, verbose_name='修改时间', auto_now=True, auto_now_add=True)
    hits = Field(int, verbose_name='点击次数')
    votes = Field(int, verbose_name='支持票数')
    image = Field(FILE, max_length=255, verbose_name='封面图片')
    summary = Field(TEXT, verbose_name='介绍', default='', nullable=False)
    deleted = Field(bool, verbose_name='删除标志')
    
    def __unicode__(self):
        return self.title
    
    class AddForm:
        fields = ['title', 'authors', 'summary']
        
    class EditForm:
        fields = ['title', 'authors', 'summary']

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
    content = Field(TEXT, verbose_name='内容', default='', nullable=False)
    format = Field(CHAR, max_length=1, verbose_name='格式', choices=get_var('TUTORIALS/format'), default='1')
    html = Field(TEXT, verbose_name='显示内容', default='', nullable=False)
    modified_user = Reference('user', verbose_name='修改人', default=get_modified_user, auto=True, auto_add=True)
    modified_date = Field(datetime, verbose_name='修改时间', auto_now=True, auto_now_add=True)
    hits = Field(int, verbose_name='点击次数')
    votes = Field(int, verbose_name='支持票数')
    deleted = Field(bool, verbose_name='删除标志')
    
    def __unicode__(self):
        return self.title
    
    class AddForm:
        fields = ['title', 'content']
    
    class EditForm:
        fields = ['title', 'content']

    @classmethod
    def OnInit(cls):
        Index('tutchp_indx', cls.c.tutorial, cls.c.parent, cls.c.order)

class Tutorials_Chapters_Comments(Model):
    __verbose_name__ = '评论'
    
    chapter = Reference('tutorials_chapters', verbose_name='所属章节')
    parent = SelfReference(verbose_name='上级', collection_name='children_comments')
    anchor = Field(str, max_length=40, verbose_name='定位点')
    content = Field(TEXT, verbose_name='内容')
    vote = Field(int, verbose_name='投票')
    modified_user = Reference('user', verbose_name='留言人', default=get_modified_user, auto=True, auto_add=True)
    modified_date = Field(datetime, verbose_name='留言时间', auto_now=True, auto_now_add=True)
    deleted = Field(bool, verbose_name='删除标志')
    
    @classmethod
    def OnInit(cls):
        Index('tutchpcmt_indx', cls.c.chapter, cls.c.parent, cls.c.anchor)
    