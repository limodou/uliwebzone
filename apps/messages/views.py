#coding=utf-8
from uliweb import expose, functions, settings
from uliweb.orm import get_model

def __begin__():
    return functions.require_login()

def _get_key(user_id):
    return '__cache_keys__:message_number:user=%d' % user_id

def _del_key(user_id):
    cache = functions.get_cache()
    cache.delete(_get_key(user_id))

@expose('/messages')
class MessageView(object):
    
    def __init__(self):
        self.model = get_model('message')
        
    def list(self):
        from uliweb import request
        from uliweb.utils.generic import ListView
        from uliweb.utils.common import get_choice
        import math
        
        pageno = int(request.values.get('page', 1)) - 1
        rows_per_page=int(request.values.get('rows', settings.get_var('MESSAGES/PAGE_NUMS', 10)))

        read_flag = request.GET.get('read', '')
        type_flag = request.GET.get('type', '')
        
        condition = None
        condition = (self.model.c.user == request.user.id) & condition
        condition = (self.model.c.send_flag == 'r') & condition
        
        if read_flag:
            condition = (self.model.c.read_flag == bool(read_flag=='1')) & condition
            
        if type_flag:
            condition = (self.model.c.type == type_flag) & condition

        def create_date(value, obj):
            from uliweb.utils.timesince import timesince
            return timesince(value)
        
        def user_image(value, obj):
            return functions.get_user_image(obj.sender, size=20)
        
        def message(value, obj):
            return value
        
        fields_convert_map = {'create_date':create_date, 
            'user_image':user_image,
            'message':message}
        
        view = ListView(self.model, condition=condition, 
            order_by=[self.model.c.create_date.desc()],
            rows_per_page=rows_per_page, pageno=pageno,
            fields_convert_map=fields_convert_map)
        view.query()
        
        result = {}
        result['read_flag'] = read_flag
        result['type_flag'] = type_flag
        result['message_type_name'] = get_choice(settings.get_var('MESSAGES/MESSAGE_TYPE'), type_flag, '全部类型')
        
        pages = int(math.ceil(1.0*view.total/rows_per_page))
        
#        result['page'] = pageno+1
#        result['total'] = view.total
#        result['pages'] = pages
        result['pagination'] = functions.create_pagination(request.url, view.total, pageno+1, rows_per_page)
        result['objects'] = list(view.objects())
        ids = []
        for row in result['objects']:
            ids.append(row._obj_.id)
        self.model.filter(self.model.c.id.in_(ids)).update(read_flag=True)
        _del_key(request.user.id)
        return result

    def read(self):
        id = request.POST.get('id')
        obj = self.model.get((self.model.c.id==int(id)) & (self.model.c.user==request.user.id) & (self.model.c.send_flag=='r'))
        if obj:
            obj.read_flag = not obj.read_flag
            obj.save()
            return json({'success':True, 'read':obj.read_flag})
        else:
            return json({'success':False, 'error':'你无权处理或记录没找到'})
        
    def delete(self):
        id = request.POST.get('id')
        obj = self.model.get((self.model.c.id==int(id)) & (self.model.c.user==request.user.id))
        if obj:
            obj.delete()
            return json({'success':True})
        else:
            return json({'success':False, 'error':'你无权处理或记录没找到'})

    def read_all(self):
        self.model.filter((self.model.c.read_flag==False) & (self.model.c.user==request.user.id) & (self.model.c.send_flag=='r')).update(read_flag=True)
        _del_key(request.user.id)
        return redirect(url_for(MessageView.list))
    
    def delete_all(self):
        send_flag = request.GET.get('send_flag', 'r')
        condition = self.model.c.send_flag == send_flag
        if send_flag == 'r':
            condition = (self.model.c.user==request.user.id) & condition
        else:
            condition = (self.model.c.sender==request.user.id) & condition
        self.model.filter(condition).remove()
        _del_key(request.user.id)
        if send_flag == 'r':
            return redirect(url_for(MessageView.list))
        else:
            return redirect(url_for(MessageView.sended_list))
        
    def send(self):
        from forms import SendMessageForm
        from uliweb.core.html import Tag
        from sqlalchemy.sql import select,func
        from uliweb.utils.textconvert import text2html
        
        User = get_model('user')
        form = SendMessageForm()
        if request.method == 'GET':
            SendMessageForm.users.choices = []
            return {'form':form.build, 'ok':False}
        if request.method == 'POST':
            flag = form.validate(request.POST)
            if flag:
                u = get_model('user')
                for u in form.users.data:
                    _id = int(u)
                    user = User.get(_id)
                    
                    functions.send_message(request.user, user, text2html(form.message.data))
                flash(_('Send message successful!'))
                return redirect(url_for(MessageView.sended_list))
            else:
                #process select values
                choices = []
                for u in form.users.data:
                    _id = int(u)
                    user = User.get(_id)
                    if user:
                        choices.append((str(user.id), unicode(user)))
                SendMessageForm.users.choices = choices
                if '_' in form.errors:
                    message = form.errors['_']
                else:
                    message = _('There are something wrong, please fix them')
                flash(message, 'error')
                return {'form':form.build, 'ok':False}

    def reply(self):
        """
        """
        from uliweb.utils.textconvert import text2html

        user = request.POST.get('user')
        if not user:
            error('没有指定用户，无法回复')
            
        message = request.POST.get('message')
        
        functions.send_message(request.user, int(user), text2html(message))
        return json({'success':True})
        
    def view(self):
        """
        消息详细信息显示
        """
        
        from uliweb.utils.generic import DetailView
        
        id = request.GET.get('id', '0')
        obj = self.model.get(int(id))
        
        fields = ({'name':'sender','verbose_name':'发送者'},
                {'name':'user','verbose_name':'接收者'},
                'create_date',
                'message',)
        layout = [
                '-- 消息详细信息 --',
                ('sender','user','create_date'),
                ('message'),
                ]
        
        view = DetailView(self.model, obj=obj, fields=fields, layout=layout)
        return view.run()
   
    def sended_list(self):
        from uliweb import request
        from uliweb.utils.generic import ListView
        from uliweb.utils.common import get_choice
        import math
        
        pageno = int(request.values.get('page', 1)) - 1
        rows_per_page=int(request.values.get('rows', settings.get_var('MESSAGES/PAGE_NUMS', 10)))

        read_flag = request.GET.get('read', '')
        type_flag = request.GET.get('type', '')
        
        condition = None
        condition = (self.model.c.sender == request.user.id) & condition
        condition = (self.model.c.send_flag == 's') & condition
        
        if read_flag:
            condition = (self.model.c.read_flag == bool(read_flag=='1')) & condition
            
        if type_flag:
            condition = (self.model.c.type == type_flag) & condition

        def create_date(value, obj):
            from uliweb.utils.timesince import timesince
            return timesince(value)
        
        def user_image(value, obj):
            return functions.get_user_image(obj.user, size=20)
        
        def message(value, obj):
            return value
        
        fields_convert_map = {'create_date':create_date, 
            'user_image':user_image,
            'message':message}
        
        view = ListView(self.model, condition=condition, 
            order_by=[self.model.c.create_date.desc()],
            rows_per_page=rows_per_page, pageno=pageno,
            fields_convert_map=fields_convert_map)
        view.query()
        
        result = {}
        result['read_flag'] = read_flag
        result['type_flag'] = type_flag
        result['message_type_name'] = get_choice(settings.get_var('MESSAGES/MESSAGE_TYPE'), type_flag, '全部类型')
        
        pages = int(math.ceil(1.0*view.total/rows_per_page))
        
#        result['page'] = pageno+1
#        result['total'] = view.total
#        result['pages'] = pages
        result['pagination'] = functions.create_pagination(request.url, view.total, pageno+1, rows_per_page)
        result['objects'] = view.objects()
        return result

@expose('/messages/number')
def messages_number():
    from uliweb import request
    
    message = get_model('message')

    if not request.user:
        return json({'success':False, 'data':''})
        
    cache = functions.get_cache()
    key = _get_key(request.user.id)
    x = cache.get(key, None)
    if not x:
        condition = None
        condition = (message.c.user == request.user.id) & condition
        condition = (message.c.read_flag == False) & condition
        condition = (message.c.send_flag == 'r') & condition
            
        x = message.filter(condition).count()
        
        cache.set(key, x)
    
    return json({'success':True, 'data':x})

def post_save(sender, instance, created, data, old_data):
    from uliweb import request
    
    _del_key(instance._user_)
    
def pre_delete(sender, instance):
    from uliweb import request
    
    _del_key(instance._user_)
    