#coding=utf-8
from uliweb import expose
from uliweb.orm import get_model

@expose('/tutorial')
class TutorialView(object):
    def __init__(self):
        self.model = get_model('tutorials')
        self.model_chapters = get_model('tutorials_chapters')
        self.model_comments = get_model('tutorials_chapters_comments')
        
    @expose('')
    def index(self):
        """
        教程显示首页
        """
        from uliweb.utils.generic import ListView

        condition = (self.model.c.deleted==False)
        
        view = ListView(self.model, condition=condition, order_by=self.model.c.modified_date.desc())
        return {'objects':view.objects()}

    def add(self):
        """
        添加新教程
        """
        from uliweb.utils.generic import AddView
        
        def get_url(**kwargs):
            return url_for(TutorialView.view, **kwargs)
        
        def pre_save(data):
            data['creator'] = request.user.id
            if request.user.id not in data['authors']:
                data['authors'].append(request.user.id)
            
        view = AddView(self.model, ok_url=get_url, pre_save=pre_save)
        return view.run()
    
    def view(self, id):
        """
        查看教程
        """
        from uliweb.utils.generic import DetailView
        
        obj = self.model.get_or_notfound(int(id))
        if obj.deleted:
            flash('教程已经被删除！')
            return redirect(url_for(TutorialView.index))
        
        view = DetailView(self.model, obj=obj)
        return view.run()
    
    def edit(self, id):
        """
        编辑教程
        """
        from uliweb.utils.generic import EditView

        def pre_save(obj, data):
            if request.user.id not in data['authors']:
                data['authors'].append(request.user.id)

        obj = self.model.get_or_notfound(int(id))
        view = EditView(self.model, ok_url=url_for(TutorialView.view, id=id), obj=obj, pre_save=pre_save)
        return view.run()
        
    def delete(self, id):
        """
        删除教程
        """
        from uliweb.utils.generic import DeleteView
        
        class MyDelete(DeleteView):
            def delete(self, obj):
                obj.deleted = True
                obj.save()
                
        obj = self.model.get_or_notfound(int(id))
        view = MyDelete(self.model, ok_url=url_for(TutorialView.index), 
            obj=obj)
        return view.run()
        
    def read(self, id):
        """
        阅读教程
        """
        obj = self.model.get_or_notfound(int(id))
        objects = list(self.model_chapters.filter(self.model_chapters.c.tutorial == obj.id).order_by(self.model_chapters.c.parent, self.model_chapters.c.order))
        
        def get_chapters(objects, parent=None, level=0, parent_num=''):
            index = 1
            for row in objects:
                if row._parent_ == parent:
                    cur_num = parent_num + str(index)
                    yield level, cur_num, row
                    for x in get_chapters(objects, row.id, level+1, cur_num+'.'):
                        yield x
                    index += 1
        return {'object':obj, 'objects':get_chapters(objects)}
    
    def add_chapter(self, t_id):
        """
        増加章节, t_id为教程id
        """
        from uliweb.utils.generic import AddView
        from sqlalchemy.sql import func
        
        obj = self.model.get_or_notfound(int(t_id))

        def get_url(**kwargs):
            return url_for(TutorialView.view_chapter, **kwargs)
        
        def pre_save(data):
            if 'parent' in request.GET:
                data['parent'] = int(request.GET.get('parent'))
            data['tutorial'] = int(t_id)
            order, = self.model_chapters.filter(self.model_chapters.c.tutorial==int(t_id)).values_one(func.max(self.model_chapters.c.order))
            data['order'] = order+1 if order>0 else 1
            
        template_data = {'object':obj}
        view = AddView(self.model_chapters, ok_url=get_url, pre_save=pre_save,
            template_data=template_data)
        return view.run()
        
    def view_chapter(self, id):
        """
        查看教程
        """
#        from uliweb.utils.generic import DetailView
        from par import WikiGrammar, WikiHtmlVisitor
        
        obj = self.model_chapters.get_or_notfound(int(id))
        if obj.deleted:
            flash('此章节已经被删除！')
            return redirect(url_for(TutorialView.read, id=obj._tutorial_))
        
#        view = DetailView(self.model_chapters, obj=obj)
#        return view.run()

        g = WikiGrammar()
        result, rest = g.parse(obj.content, resultSoFar=[], skipWS=False)
        tag_class = {
            'table':'table',
        }
        content = WikiHtmlVisitor('', tag_class).visit(result)
        return {'object':obj, 'content':content}
    
    def edit_chapter(self, id):
        """
        编辑章节
        """
        from uliweb.utils.generic import EditView
    
        obj = self.model_chapters.get_or_notfound(int(id))
        view = EditView(self.model_chapters, ok_url=url_for(TutorialView.view_chapter, id=id), obj=obj)
        return view.run()
    