#coding=utf8
from uliweb.orm import *
from uliweb.utils.common import get_var

class Class_Teacher(Model):
    teacher = Reference('user', verbose_name='教师', required=True)
    weibo = Field(str, verbose_name='微博')
    blog = Field(str, verbose_name='博客')
    qq = Field(str, verbose_name='QQ号', max_length=20)
    description = Field(TEXT, verbose_name='介绍')
    
    def __unicode__(self):
        return unicode(self.teacher)
    
class Class_Category(Model):
    name = Field(str, verbose_name='名称', max_length=20, required=True)
    
    def __unicode__(self):
        return self.name
    
    class Table:
        fields = ['name']
    
class Class(Model):
    name = Field(str, verbose_name='名称', required=True, index=True)
    teachers = ManyToMany('user', verbose_name='教师', required=True)
    description = Field(TEXT, verbose_name='课程介绍', required=True)
    requirement = Field(TEXT, verbose_name='课程要求')
    link = Field(str, verbose_name='课件链接')
    attention_num = Field(int, verbose_name='关注人数')
    attention_users = ManyToMany('user', verbose_name='关注人')
    logo = Field(FILE, verbose_name='Logo')
    issue_num = Field(int, verbose_name='期数')
    create_date = Field(datetime.datetime, verbose_name='创建时间', auto_now_add=True)
    category = Reference('class_category', verbose_name='分类', required=True)
    
    def __unicode__(self):
        return self.name
    
    class AddForm:
        fields = ['name', 'teachers', 'description', 'requirement', 'link',
            'category']
    
    def get_lastest(self):
        P = Class_Phrase
        r = P.filter(P.c.issue==self.issue).filter(P.c.class_obj==self.id).order_by(P.c.issue.desc()).limit(1)
        if len(r) > 0:
            return r[0]
        else:
            return
        
    def get_image(self):
        from uliweb import functions
        
        if self.logo:
            return functions.get_href(self.logo)
        else:
            return functions.url_for_static('classes/default_class.png')
        
    class Table:
        fields = [
            {'name':'name'},
            {'name':'category', 'width':60},
            {'name':'teachers', 'width':150},
            {'name':'link', 'width':100},
            {'name':'issue_num', 'width':60},
        ]
        
    class EditForm:
        fields = ['name', 'teachers', 'description', 'requirement', 'link',
            'category']
    
class Class_Issue(Model):
    """
    按期数来区分
    """
    issue = Field(int, verbose_name='期数', default=1)
    class_obj = Reference('class', verbose_name='课程', required=True)
    teachers = ManyToMany('user', verbose_name='教师', required=True)
    begin_date = Field(datetime.datetime, verbose_name='开始时间', required=True)
    finish_date = Field(datetime.datetime, verbose_name='结束时间', required=True)
    need_num = Field(int, verbose_name='招生人数', required=True)
    students_num = Field(int, verbose_name='学生数')
    position = Field(str, verbose_name='上课地点', required=True)
    type = Field(CHAR, max_length=1, verbose_name='课程性质', choices=get_var('CLASSES/class_type'))
    fee = Field(str, verbose_name='收费说明')
    
    @classmethod
    def OnInit(cls):
        Index('cls_issue_idx', cls.c.class_obj, cls.c.issue, unique=True)
    
    class AddForm:
        fields = ['begin_date', 'finish_date', 'teachers', 'need_num',
            'position', 'type', 'fee']
            
    class EditForm:
        fields = ['begin_date', 'finish_date', 'teachers', 'need_num',
            'position', 'type', 'fee']

    class Table:
        fields = [
            {'name':'issue', 'width':45},
            {'name':'teachers'},
            {'name':'begin_date', 'width':100},
            {'name':'finish_date', 'width':100},
            {'name':'need_num', 'width':75},
            {'name':'position'},
            {'name':'type', 'width':75},
            {'name':'fee', 'width':90},
        ]
        
class Class_Info(Model):
    content = Field(TEXT, verbose_name='内容', required=True)
    issue = Field(int, verbose_name='期数', default=1)
    class_obj = Reference('class', verbose_name='课程', required=True)
    create_date = Field(datetime.datetime, verbose_name='创建时间', auto_now_add=True)
    
    @classmethod
    def OnInit(cls):
        Index('cls_info_idx', cls.c.class_obj, cls.c.issue)
        
class Class_StudyRecord(Model):
    issue = Field(int, verbose_name='期数', default=1)
    class_obj = Reference('class', verbose_name='课程', required=True)
    student = Reference('user', verbose_name='学生', required=True)
    score = Field(int, verbose_name='成绩')
    evaluate_level = Field(TEXT, verbose_name='评价级别', choices=get_var('CLASSES/evaluate_level'))
    evaluation = Field(TEXT, verbose_name='评语')
    
    @classmethod
    def OnInit(cls):
        Index('cls_std_idx', cls.c.class_obj, cls.c.issue)
        