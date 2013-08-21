#coding=utf-8
from uliweb.orm import *
from uliweb.utils.common import get_var
from uliweb.i18n import ugettext_lazy as _

class Blog_Category(Model):
    name = Field(str, max_length=255, verbose_name=_('Category'))
    
    def __unicode__(self):
        return self.name
    
    class Table:
        fields = [
            'name',
        ]    
    
    class AddForm:
        fields = ['name']
        
    class EditForm:
        fields = ['name']
    
class Blog_Tag(Model):
    name = Field(str, max_length=255, verbose_name=_('Tag'))

    def __unicode__(self):
        return self.name
    
    class Table:
        fields = [
            'name',
        ]    
    
    class AddForm:
        fields = ['name']
        
    class EditForm:
        fields = ['name']
    
class Blog(Model):
    title = Field(str, max_length=255, verbose_name=_('Title'))
    content = Field(TEXT, verbose_name=_('Content'))
    publish_date = Field(datetime.datetime, verbose_name=_('Publish Date'), auto_now_add=True)
    author = Reference('user', verbose_name=_('Author'))
    category = Reference('blog_category', verbose_name=_('Category'))
    tags = ManyToMany('blog_tag', verbose_name=_('Tags'))
    enable_comment = Field(bool, verbose_name=_('Enable Comment'), default=True)
    
    class AddForm:
        fields = ['title', 'content', 'category', 'tags', 'enable_comment']
        
    class EditForm:
        fields = ['title', 'content', 'category', 'tags', 'enable_comment']
    
