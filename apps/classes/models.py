#coding=utf8
from uliweb.orm import *
from uliweb.utils.common import get_var

class Class_Teacher(Model):
    teacher = Reference('user', verbose_name='教师', required=True)
    description = Field(TEXT, verbose_name='介绍')
    
    def __unicode__(self):
        return unicode(self.teacher)
    
    class Table:
        fields = [
            {'name':'teacher'},
            {'name':'description', 'hidden':True},
        ]
        
    class ListTable:
        fields = [
            {'name':'user_id'},
            {'name':'teacher'},
            {'name':'description'},
            {'name':'image'},
        ]
    
    
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
    summary = Field(str, verbose_name='课程简介', required=True)
    requirement = Field(TEXT, verbose_name='课程要求')
    link = Field(str, verbose_name='课件链接')
    attention_num = Field(int, verbose_name='关注人数')
    attention_users = ManyToMany('user', verbose_name='关注人')
    logo = Field(FILE, verbose_name='Logo')
    issue_num = Field(int, verbose_name='总期数')
    create_date = Field(datetime.datetime, verbose_name='创建时间', auto_now_add=True)
    category = Reference('class_category', verbose_name='分类', required=True)
    order = Field(int, verbose_name='序号', hint="序号越大排列越靠前")
    
    def __unicode__(self):
        return self.name
    
    def get_url(self):
        return '<a href="/class/view/%d">%s</a>' % (self.id, self.name)
    
    class AddForm:
        fields = ['name', 'teachers', 'summary', 'description', 'requirement', 'link',
            'category', 'order']
    
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
            {'name':'order', 'width':60},
        ]
        
    class ListTable:
        fields = [
            {'name':'id'},
            {'name':'name'},
            {'name':'category', 'width':60},
            {'name':'teachers', 'width':150},
            {'name':'link', 'width':100},
            {'name':'issue_num', 'width':60},
            {'name':'summary'},
            {'name':'description'},
            {'name':'order'},
        ]
        
    class EditForm:
        fields = ['name', 'teachers', 'summary', 'description', 'requirement', 'link',
            'category', 'order']
    
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
    map = Field(str, verbose_name='地图')
    type = Field(CHAR, max_length=1, verbose_name='课程性质', choices=get_var('CLASSES/class_type'), required=True)
    fee = Field(str, verbose_name='收费说明')
    
    @classmethod
    def OnInit(cls):
        Index('cls_issue_idx', cls.c.class_obj, cls.c.issue, unique=True)
    
    class AddForm:
        fields = ['begin_date', 'finish_date', 'teachers', 'need_num',
            'position', 'map', 'type', 'fee']
            
    class EditForm:
        fields = ['begin_date', 'finish_date', 'teachers', 'need_num',
            'position', 'map', 'type', 'fee']

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
        
    class ListTable:
        fields = [
            {'name':'issue'},
            {'name':'teachers'},
            {'name':'begin_date'},
            {'name':'finish_date'},
            {'name':'need_num'},
            {'name':'students_num'},
            {'name':'position'},
            {'name':'type'},
            {'name':'fee'},
            {'name':'enroll'},
            {'name':'enrolled'},
        ]
    
class Class_Info(Model):
    title = Field(str, verbose_name='标题', required=True)
    content = Field(TEXT, verbose_name='内容', required=True)
    issue = Field(int, verbose_name='期数', default=1)
    class_obj = Reference('class', verbose_name='课程', required=True)
    create_date = Field(datetime.datetime, verbose_name='创建时间', auto_now_add=True)
    
    @classmethod
    def OnInit(cls):
        Index('cls_info_idx', cls.c.class_obj, cls.c.issue)
        
    class AddForm:
        fields = ['title', 'content']
            
    class EditForm:
        fields = ['title', 'content']
    
    class Table:
        fields = [
            {'name':'issue', 'width':100},
            {'name':'create_date', 'width':100},
            {'name':'title'},
            {'name':'content'},
        ]
    
    class ListTable:
        fields = [
            {'name':'issue', 'width':100},
            {'name':'create_date', 'width':100},
            {'name':'title'},
            {'name':'content'},
            {'name':'class_obj'},
        ]
    
class Class_StudyRecord(Model):
    issue = Field(int, verbose_name='期数', default=1)
    class_obj = Reference('class', verbose_name='课程', required=True)
    student = Reference('user', verbose_name='学生', required=True)
    score = Field(int, verbose_name='成绩')
    create_date = Field(datetime.datetime, verbose_name='报名时间', auto_now_add=True)
    evaluate_level = Field(TEXT, verbose_name='评价级别', choices=get_var('CLASSES/evaluate_level'))
    evaluation = Field(TEXT, verbose_name='评语')
    deleted = Field(bool, verbose_name='删除标志')
    
    @classmethod
    def OnInit(cls):
        Index('cls_std_idx', cls.c.class_obj, cls.c.issue, cls.c.student, unique=True)
        
    class QueryStudents:
        fields = [
            'student', 'image', 'name',
        ]