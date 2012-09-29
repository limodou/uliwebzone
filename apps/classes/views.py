#coding=utf-8
from uliweb import expose, functions
from uliweb.orm import get_model

@expose('/class')
class ClassView(object):
    def __init__(self):
        self.model = get_model('class')
        
    @expose('')
    def index(self):
        """
        课程展示首页
        """
        Info = get_model('class_info')
        dynamic_messages = Info.all().order_by(Info.c.create_date.desc()).limit(10)
        
        classes = self.model.all().order_by(self.model.c.create_date.desc()).limit(10)
        return {'dynamic_messages':dynamic_messages, 'classes':classes}
    
@expose('/class/admin/class')
class ClassAdminView(object):
    def __init__(self):
        self.model = get_model('class')
        
        def link(value, obj):
            if value:
                return '<a href="%s">%s</a>' % (value, u'查看课件')
            else:
                return ''

        self.convert_link = link
    
    def _get_list_view(self):
        from uliweb.utils.generic import ListView
        
        if functions.has_role(request.user, 'superuser'):
            condition = None
        else:
            condition = self.model.teachers.in_(request.user.id)
        
        view = ListView(self.model, pagination=False, 
            condition=condition,
            fields_convert_map={'link':self.convert_link}
        )
        return view
        
    @expose('')
    def index(self):
        """
        课程管理页面
        """
        
        view = self._get_list_view()
        fields_list = view.table_info()['fields_list']
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
        添加课程
        """
        from uliweb.utils.generic import EditView, ReferenceSelectField
        
        obj = self.model.get_or_notfound(int(id))

        def get_form_field(name, obj):
            if name == 'teachers':
                return ReferenceSelectField('user', label='教师', multiple=True, required=True, query=obj.teachers)
        
        view = EditView(self.model, ok_url=url_for(self.__class__.index), 
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
        
    @expose('')
    def index(self):
        from uliweb.utils.generic import ListView
        
        view = ListView(self.model)
        fields_list = view.table_info()['fields_list']
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
        
    def _get_fields(self):
        view = functions.ListView(self.model)
        return view.table_info()['fields_list']
        
    @expose('')
    def index(self):
        return {'fields':self._get_fields()}
    
    def query(self):
        def issue(value, obj):
            return value
        
        view = functions.ListView(self.model, pagination=False, 
            condition=self.condition,
            fields_convert_map={'issue':issue},
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

        def success_data(obj, data):
            from uliweb.utils.generic import get_field_display
            
            d = obj.to_dict()
            d['teachers'] = get_field_display(self.model, 'teachers', obj)
            return d
        
        view = functions.AddView(self.model,
            pre_save=pre_save,
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
            return d
           
        def post_created_form(fcls, model, obj):
            fcls.teachers.query = obj.teachers
        
        obj = self.model.get_or_notfound(int(id))
        view = functions.EditView(self.model, obj=obj, 
            template_data={'class_id':self.class_id},
            post_created_form=post_created_form,
            success_data=success_data,
            )
        return view.run(json_result=True)
        
    def delete(self, id):
        obj = self.model.get_or_notfound(int(id))
        view = functions.DeleteView(self.model, obj=obj)
        return view.run(json_result=True)
