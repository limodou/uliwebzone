#coding=utf-8
from uliweb import expose, functions, validators
from uliweb.orm import get_model
from sqlalchemy import and_
from uliweb.utils.date import now
import math

@expose('/class')
class ClassView(object):
    def __init__(self):
        from uliweb import request
        
        self.model = get_model('class')
        self.model_info = get_model('class_info')
        self.model_issue = get_model('class_issue')
        self.model_teacher = get_model('class_teacher')
        self.model_study = get_model('class_studyrecord')
        self.class_id = int(request.GET.get('class_id', 0))
        
        def link(value, obj):
            if value:
                return '<a href="%s">%s</a>' % (value, u'查看课件')
            else:
                return ''
        
        self.convert_link = link
        
    @expose('')
    def index(self):
        """
        课程展示首页
        """
        classes_view = self._get_classes_view()
        infos_view = self._get_infos_view()
        return {'infos':infos_view.objects(), 'classes':classes_view.objects()}
    
    def _get_classes_view(self):
        """
        Return a ListView object
        """
        condition = None
        
        page = int(request.values.get('page', 1)) - 1
        rows = settings.CLASSES.get('rows', 10)
        
        view = functions.ListView(self.model, 
            pageno=page, 
            rows_per_page=rows,
            order_by=[self.model.c.order.desc(), self.model.c.create_date.desc()],
            meta='ListTable',
        )
        return view

    def _get_infos_view(self):
        """
        Return a ListView object
        """
        condition = None
        
        page = int(request.values.get('page', 1)) - 1
        rows = settings.CLASSES.get('rows', 10)
        
        view = functions.ListView(self.model_info, 
            pageno=page, 
            rows_per_page=rows,
            order_by=self.model_info.c.create_date.desc(),
            meta='ListTable',
        )
        return view
    
    def _get_teachers_view(self):
        """
        Return a ListView object
        """
        condition = None
        
        page = int(request.values.get('page', 1)) - 1
        rows = settings.CLASSES.get('rows', 10)
        
        def user_id(value, obj):
            return obj._teacher_
        
        def image(value, obj):
            return functions.get_user_image(obj.teacher)
        
        def blog(value, obj):
            return '<a href="%s">%s</a>' % (obj.blog, obj.blog)
        
        fields_convert_map = {
            'user_id':user_id,
            'image':image,
            'blog':blog,
        }
        
        view = functions.ListView(self.model_teacher, 
            pageno=page, 
            rows_per_page=rows,
            fields_convert_map=fields_convert_map,
            meta='ListTable',
        )
        return view
    
    def classes(self):
        """
        显示课程清单
        """
        view = self._get_classes_view()
        view.query()
        pages = int(math.ceil(1.0*view.total/view.rows_per_page))
        return {
            'objects':view.objects(),
            'pagination':functions.create_pagination(request.url, view.total, view.pageno+1, view.rows_per_page),
        }

    def infos(self):
        """
        显示消息清单
        """
        view = self._get_infos_view()
        view.query()
        pages = int(math.ceil(1.0*view.total/view.rows_per_page))
        return {
            'objects':view.objects(),
            'pagination':functions.create_pagination(request.url, view.total, view.pageno+1, view.rows_per_page),
        }
        
    def teachers(self):
        """
        返回teacher数据
        """
        view = self._get_teachers_view()
        return json(view.json())
        
    def view(self, class_id):
        """
        查看课程
        """
        obj = self.model.get_or_notfound(int(class_id))
        
        fields_convert_map={
            'link':self.convert_link,
        }
        
        view = functions.DetailView(self.model, obj=obj,
            fields_convert_map=fields_convert_map,
        )
        
        return view.run()
    
    def _position(self, value, obj):
        if obj.map:
            map = u' <a href="%s" target="_blank"><i class="icon-share"></i>查看地图</a>' % obj.map
        else:
            map = ''
        return '%s%s' % (value, map)
    
    def _issue(self, value, obj):
        return value
    
    def _get_student(self, obj):
        """
        根据issue对象，获得当前用户studyrecord记录
        """
        from uliweb import request
        
        return self.model_study.get(
                (self.model_study.c.student==request.user.id) & 
                (self.model_study.c.class_obj==obj._class_obj_) & 
                (self.model_study.c.issue==obj.issue)
            )
        
    def _enroll(self, obj):
        """
        报名状态：-2 已结束 -1 未登录 -3 人员已满， 1 已经报名 0 尚未报名
        """
        if obj.need_num == obj.students_num:
            return -3
        date = now()
        if date >= obj.begin_date:
            return -2
        if not request.user:
            return -1

        row = self._get_student(obj)
        if row and row.deleted == False:
            return 0
        else:
            return 1
        
    def _enrolled(self, obj):
        """
        是否已经报名
        """
        row = self.model_study.get(and_(
            self.model_study.c.class_obj==obj._class_obj_, 
            self.model_study.c.issue==obj.issue,
            self.model_study.c.student==request.user.id))
        if row and row.deleted==False:
            return True
        else:
            return False
    
    
    def query_classissues(self):
#        page = int(request.values.get('page', 1)) - 1
        rows = 5
        condition = self.model_issue.c.class_obj == self.class_id
       
    
        def enroll(value, obj):
            return self._enroll(obj)
            
        def enrolled(value, obj):
            return self._enrolled(obj)
            
        view = functions.ListView(self.model_issue,
#            pageno=page, 
            rows_per_page=rows,
            condition=condition,
            order_by=[self.model_issue.c.issue.desc()],
            fields_convert_map={
                'issue':self._issue, 
                'position':self._position,
                'enroll':enroll,
                'enrolled':enrolled,
                },
            meta='ListTable',
            )
        return json(view.json())
        
    def query_classinfos(self):
        page = int(request.values.get('page', 1)) - 1
        rows = 5
        condition = self.model_info.c.class_obj == self.class_id

        view = functions.ListView(self.model_info,
            pageno=page, rows_per_page=rows,
            condition=condition,
            order_by=[self.model_info.c.create_date.desc()],
            fields_convert_map={'issue':self._issue},
            )
        return json(view.json())
    
    def enroll(self):
        """
        报名处理
        """
        
        issue = int(request.POST.get('issue'))
        class_id = int(request.POST.get('class_id'))
        obj = self.model_issue.get(
            and_(self.model_issue.c.class_obj==class_id, 
                self.model_issue.c.issue==issue), for_update=True)

        row = self._get_student(obj)
        if row and not row.deleted:
            return json({'success':False, 'message':'你已经报过名了！'})
        
        if obj.students_num < obj.need_num:
            obj.students_num += 1
            obj.save()
            if not row:
                row = self.model_study(
                    issue=issue,
                    class_obj=class_id,
                    student=request.user.id,
                )
            else:
                row.deleted = False
                row.create_date = now()
            row.save()
            d = obj.to_dict()
            d['enrolled'] = True
            return json({'success':True, 'message':'报名成功！', 'data':d})
        else:
            return json({'success':False, 'message':'对不起，报名人数已经满了，请等下期再报名！'})
        
    def unenroll(self):
        """
        取消报名处理
        """
        
        issue = int(request.POST.get('issue'))
        class_id = int(request.POST.get('class_id'))
        obj = self.model_issue.get(
            and_(self.model_issue.c.class_obj==class_id, 
                self.model_issue.c.issue==issue), for_update=True)
    
        row = self.model_study.get(and_(
            self.model_study.c.class_obj==class_id, 
            self.model_study.c.issue==issue,
            self.model_study.c.student==request.user.id))

        if not row:
            return json({'success':False, 'message':'你尚未报名，无法取消！'})
        
        obj.students_num -= 1
        obj.save()
        row.delete(delete_fieldname='deleted')
        row.save()
        d = obj.to_dict()
        d['enrolled'] = False
        return json({'success':True, 'message':'取消成功！', 'data':d})
    
    def students(self):
        issue = int(request.POST.get('issue'))
        class_id = int(request.POST.get('class_id'))

        condition = (self.model_study.c.issue==issue) & (self.model_study.c.class_obj==class_id)
        
        def image(value, obj):
            return functions.get_user_image(obj.student, 20)
        
        def name(value, obj):
            return unicode(obj.student)
        
        view = functions.ListView(self.model_study,
            condition=condition,
            pagination=False,
            order_by=[self.model_study.c.create_date],
            fields_convert_map={'image':image, 'name':name},
            meta='QueryStudents',
            )
        return json(view.json())
        
@expose('/class/admin/class')
class ClassAdminView(object):
    def __init__(self):
        self.model = get_model('class')
        
        def link(value, obj):
            if value:
                return '<a href="%s">%s</a>' % (value, u'查看')
            else:
                return ''

        self.convert_link = link
        
    def __begin__(self):
        functions.require_login()
        
        if not functions.has_role(request.user, 'teacher', 'superuser'):
            error("你没有权限访问此页面")
    
    def _get_list_view(self):
        from uliweb.utils.generic import ListView
        
        if functions.has_role(request.user, 'superuser'):
            condition = None
        else:
            condition = self.model.teachers.in_(request.user.id)
        
        view = ListView(self.model, pagination=False, 
            condition=condition,
            order_by=[self.model.c.order.desc(), self.model.c.create_date.desc()],
            fields_convert_map={'link':self.convert_link}
        )
        return view
        
    @expose('')
    def index(self):
        """
        课程管理页面
        """
        
        view = self._get_list_view()
        fields_list = view.table_info['fields_list']
        return {'fields':fields_list}
    
    def query(self):
        """
        返回课程列表
        """
        view = self._get_list_view()
        return json(view.json())
        
    def add(self):
        """
        添加课程
        """
        from uliweb.utils.generic import AddView
        
        def get_url(id):
            return url_for(self.__class__.index)
        
        def get_form_field(name):
            from uliweb.form import SelectField
            if name == 'teachers':
                return SelectField('教师', multiple=True, help_string='添加除你之外的教师', datatype=int)
        
        def pre_save(data):
            if request.user.id not in data['teachers']:
                data['teachers'].append(request.user.id)
                
        view = AddView(self.model, ok_url=get_url, 
            get_form_field=get_form_field,
            pre_save=pre_save,
            form_args={'title':'添加新课程'})
        return view.run()
    
    def view(self, id):
        """
        显示课程
        """
        obj = self.model.get_or_notfound(int(id))
        
        fields_convert_map={'link':self.convert_link}
        
        issue_view = ClassIssueAdminView()
        fields = issue_view._get_fields()
        
        view = functions.DetailView(self.model, obj=obj,
            fields_convert_map=fields_convert_map,
            template_data={'fields':fields},
        )
        
        return view.run()
    
    def edit(self, id):
        """
        修改课程
        """
        from uliweb.utils.generic import EditView, ReferenceSelectField
        
        obj = self.model.get_or_notfound(int(id))

        def get_form_field(name, obj):
            if name == 'teachers':
                return ReferenceSelectField('user', label='教师', multiple=True, required=True, query=obj.teachers)
        
        view = EditView(self.model, ok_url=url_for(self.__class__.view, id=obj.id), 
            obj=obj,
            get_form_field=get_form_field,
            form_args={'title':'修改课程'})
        return view.run()
    
    def delete(self, id):
        from uliweb.utils.generic import DeleteView
        
        obj = self.model.get_or_notfound(int(id))
        view = DeleteView(self.model, obj=obj)
        return view.run(json_result=True)
    
@expose('/class/admin/category')
class ClassCategoryAdminView(object):
    def __init__(self):
        self.model = get_model('class_category')
        
    def __begin__(self):
        functions.require_login()
        
        if not functions.has_role(request.user, 'superuser'):
            error("你没有权限访问此页面")

    @expose('')
    def index(self):
        from uliweb.utils.generic import ListView
        
        view = ListView(self.model)
        fields_list = view.table_info['fields_list']
        return {'fields':fields_list}
    
    def query(self):
        from uliweb.utils.generic import ListView
        
        view = ListView(self.model, pagination=False)
        return json(view.json())
        
    def add(self):
        from uliweb.utils.generic import AddView

        view = AddView(self.model, success_data=True)
        return view.run(json_result=True)
        
    def edit(self, id):
        from uliweb.utils.generic import EditView
        
        obj = self.model.get_or_notfound(int(id))
        view = EditView(self.model, obj=obj, success_data=True)
        return view.run(json_result=True)
        
    def delete(self, id):
        from uliweb.utils.generic import DeleteView
        
        obj = self.model.get_or_notfound(int(id))
        view = DeleteView(self.model, obj=obj)
        return view.run(json_result=True)
        
@expose('/class/admin/issue')
class ClassIssueAdminView(object):
    def __init__(self):
        from uliweb import request
        
        self.model = get_model('class_issue')
        self.class_id = int(request.GET.get('class_id', 0))
        self.condition = self.model.c.class_obj == self.class_id
        
    def __begin__(self):
        functions.require_login()
        
        if not functions.has_role(request.user, 'teacher', 'superuser'):
            error("你没有权限访问此页面")
    
    def _position(self, value, obj):
        if obj.map:
            map = u' <a href="%s" target="_blank"><i class="icon-share"></i>查看地图</a>' % obj.map
        else:
            map = ''
        return '%s%s' % (value, map)
    
    def _get_fields(self):
        view = functions.ListView(self.model)
        return view.table_info['fields_list']
        
    @expose('')
    def index(self):
        return {'fields':self._get_fields()}
    
    def query(self):
        def issue(value, obj):
            return value
        
        page = int(request.values.get('page', 1)) - 1
        rows = 5
        view = functions.ListView(self.model,
            pageno=page, rows_per_page=rows,
            condition=self.condition,
            order_by=[self.model.c.issue.desc()],
            fields_convert_map={'issue':issue, 'position':self._position},
            )
        return json(view.json())
        
    def add(self):
        from sqlalchemy.sql import func
        
        def pre_save(data):
            issue, = self.model.filter(self.model.c.class_obj==self.class_id).values_one(func.max(self.model.c.issue))
            data['issue'] = (issue or 0)+1
            data['class_obj'] = self.class_id
            
        def post_created_form(fcls, model):
            fcls.teachers.choices = [('', '')]
            fcls.map.validators.append(validators.IS_URL)
            
        def post_save(obj, data):
            obj.class_obj.issue_num += 1
            obj.class_obj.save()

        def success_data(obj, data):
            from uliweb.utils.generic import get_field_display
            
            d = obj.to_dict()
            d['teachers'] = get_field_display(self.model, 'teachers', obj)
            d['position'] = self._position(d['position'], obj)
            d['type'] = get_field_display(self.model, 'type', obj)
            return d
        
        view = functions.AddView(self.model,
            pre_save=pre_save,
            post_save=post_save,
            post_created_form=post_created_form,
            template_data={'class_id':self.class_id},
            success_data=success_data,
            )
        return view.run(json_result=True)
        
    def edit(self, id):
        def success_data(obj, data):
            from uliweb.utils.generic import get_field_display
            
            d = obj.to_dict()
            d['teachers'] = get_field_display(self.model, 'teachers', obj)
            d['position'] = self._position(d['position'], obj)
            d['type'] = get_field_display(self.model, 'type', obj)
            return d
           
        def post_created_form(fcls, model, obj):
            fcls.teachers.query = obj.teachers
            fcls.map.validators.append(validators.IS_URL)
        
        obj = self.model.get_or_notfound(int(id))
        view = functions.EditView(self.model, obj=obj, 
            template_data={'class_id':self.class_id},
            post_created_form=post_created_form,
            success_data=success_data,
            )
        return view.run(json_result=True)
        
    def delete(self, id):
        def pre_delete(obj):
            obj.class_obj.issue_num -= 1
            obj.class_obj.save()
            
        obj = self.model.get_or_notfound(int(id))
        view = functions.DeleteView(self.model, obj=obj,
            pre_delete=pre_delete,
        )
        return view.run(json_result=True)

@expose('/class/admin/info')
class ClassInfoAdminView(object):
    def __init__(self):
        from uliweb import request
        
        self.model = get_model('class_info')
        self.class_id = int(request.GET.get('class_id', 0))
        self.condition = self.model.c.class_obj == self.class_id
        
    def __begin__(self):
        functions.require_login()
        
        if not functions.has_role(request.user, 'teacher'):
            error("你没有权限访问此页面")
    
    def query(self):
        def issue(value, obj):
            return value
        
        page = int(request.values.get('page', 1)) - 1
        rows = 5
        view = functions.ListView(self.model,
            pageno=page, rows_per_page=rows,
            condition=self.condition,
            order_by=[self.model.c.create_date.desc()],
            fields_convert_map={'issue':issue},
            )
        return json(view.json())
        
    def add(self):
        from sqlalchemy.sql import func
        
        def pre_save(data):
            issue, = self.model.filter(self.model.c.class_obj==self.class_id).values_one(func.max(self.model.c.issue))
            data['issue'] = (issue or 0)+1
            data['class_obj'] = self.class_id
            
        def success_data(obj, data):
            from uliweb.utils.generic import get_field_display

            d = obj.to_dict()
            d['content'] = get_field_display(self.model, 'content', obj)
            return d
        
        view = functions.AddView(self.model,
            pre_save=pre_save,
            template_data={'title':'添加新的课程动态'},
            success_data=success_data,
            )
        response.template = 'GenericView/ajax_add.html'
        return view.run(json_result=True)
        
    def edit(self, id):
        def success_data(obj, data):
            from uliweb.utils.generic import get_field_display
            
            d = obj.to_dict()
            d['content'] = get_field_display(self.model, 'content', obj)
            return d
           
        obj = self.model.get_or_notfound(int(id))
        view = functions.EditView(self.model, obj=obj, 
            template_data={'title':'修改课程动态'},
            success_data=success_data,
            )
        response.template = 'GenericView/ajax_edit.html'
        return view.run(json_result=True)
        
    def delete(self, id):
        obj = self.model.get_or_notfound(int(id))
        view = functions.DeleteView(self.model, obj=obj)
        return view.run(json_result=True)

@expose('/class/admin/teacher')
class ClassTeacherView(object):
    def __begin__(self):
        #return functions.require_login()
        #
        pass
        
    def __init__(self):
        self.model = functions.get_model('class_teacher')
        
    def __begin__(self):
        functions.require_login()
        
        if not functions.has_role(request.user, 'superuser'):
            error("你没有权限访问此页面")
    
    def _get_view(self):
        """
        Return a ListView object
        """
        condition = None
        
        def blog(value, obj):
            return '<a href="%s">%s</a>' % (value, value)
        
        fields_convert_map = {'blog':blog}
        
        view = functions.ListView(self.model, 
#            pageno=page, 
#            rows_per_page=rows,
            pagination=False,
            condition=condition,
            fields_convert_map=fields_convert_map,
        )
        return view
        
    def _get_fields(self):
        """
        Return list fields info, and it'll be used in angularjs template
        """
        view = functions.ListView(self.model)
        return view.table_info['fields_list']
        
    @expose('')
    def index(self):
        return {'fields':self._get_fields()}
    
    def query(self):
        view = self._get_view()
        return json(view.json())
        
    def add(self):
        def pre_save(data):
            pass
            
        def post_created_form(fcls, model):
            fcls.teacher.choices = [('', '')]
            
        def post_save(obj, data):
            pass
    
        def success_data(obj, data):
            d = obj.to_dict()
            d['teacher'] = unicode(obj.teacher)
            return d
        
        view = functions.AddView(self.model,
#            pre_save=pre_save,
#            post_save=post_save,
            post_created_form=post_created_form,
#            template_data={},
            success_data=success_data,
            )
        response.template = 'GenericView/ajax_add.html'
        return view.run(json_result=True)
        
    def view(self, id):
        """
        Show the detail of object. Template will receive an `object` variable 
        """
        obj = self.model.get_or_notfound(int(id))
        fields_convert_map = {}
        view = functions.DetailView(self.model, 
            obj=obj,
#            fields_convert_map=fields_convert_map,
        )
        return view.run()
        
    def edit(self, id):
        def success_data(obj, data):
            d = obj.to_dict()
            d['teacher'] = unicode(obj.teacher)
            return d
           
        def post_created_form(fcls, model, obj):
            User = get_model('user')
            fcls.teacher.query = User.filter(User.c.id==obj._teacher_)
        
        obj = self.model.get_or_notfound(int(id))
        view = functions.EditView(self.model, 
            obj=obj, 
#            template_data={'class_id':self.class_id},
            post_created_form=post_created_form,
            success_data=success_data,
            )
        response.template = 'GenericView/ajax_edit.html'
        return view.run(json_result=True)
        
    def delete(self, id):
        def pre_delete(obj):
            pass
            
        obj = self.model.get_or_notfound(int(id))
        view = functions.DeleteView(self.model, 
            obj=obj,
#            pre_delete=pre_delete,
        )
        return view.run(json_result=True)
    