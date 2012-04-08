#coding=utf-8
from uliweb import expose, functions
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
        
        def post_created_form(fcls, model, obj):
            fcls.authors.html_attrs['url'] = '/users/search'
            fcls.authors.choices = [('', '')]
        
        view = AddView(self.model, ok_url=get_url, pre_save=pre_save, 
            post_created_form=post_created_form)
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

        def post_created_form(fcls, model, obj):
            fcls.authors.html_attrs['url'] = '/users/search'
            fcls.authors.query = obj.authors.all()
        
        obj = self.model.get_or_notfound(int(id))
        view = EditView(self.model, ok_url=url_for(TutorialView.view, id=id), 
            obj=obj, pre_save=pre_save, post_created_form=post_created_form)
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
        
        def get_chapters(parent=None, parent_num='', objects=objects):
            index = 1
            for row in objects:
                if row._parent_ == parent:
                    cur_num = parent_num + str(index)
                    yield cur_num, row
                    index += 1
        return {'object':obj, 'objects':get_chapters}
    
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
            data['content'] = self._prepare_content(data['content'])
            
        template_data = {'object':obj}
        view = AddView(self.model_chapters, ok_url=get_url, pre_save=pre_save,
            template_data=template_data)
        return view.run()
        
    def view_chapter(self, id):
        """
        查看教程
        """
#        from uliweb.utils.generic import DetailView
        from tut_parser import TutGrammar, TutVisitor
        
        obj = self.model_chapters.get_or_notfound(int(id))
        if obj.deleted:
            flash('此章节已经被删除！')
            return redirect(url_for(TutorialView.read, id=obj._tutorial_))
        
#        view = DetailView(self.model_chapters, obj=obj)
#        return view.run()

        g = TutGrammar()
        result, rest = g.parse(obj.content, resultSoFar=[], skipWS=False)
        t = TutVisitor()
        content = t.visit(result)
        return {'object':obj, 'content':content, 'titles':t.titles}
    
    def _prepare_content(self, text):
        """
        对文本进行预处理，对每个段落识别[[#]]标记，计算最大值，同时如果不存在，
        则自动添加[[#]]
        """
        from tut_parser import TutGrammar, TutCVisitor, TutTextVisitor
        
        g = TutGrammar()
        result, rest = g.parse(text, resultSoFar=[], skipWS=False)
        t = TutCVisitor()
        new_text = t.visit(result)
        result, rest = g.parse(new_text, resultSoFar=[], skipWS=False)
        result = TutTextVisitor(t.max_id).visit(result)
        return result
        
    def edit_chapter(self, id):
        """
        编辑章节
        """
        from uliweb.utils.generic import EditView
    
        obj = self.model_chapters.get_or_notfound(int(id))
        
        def pre_save(obj, data):
            data['content'] = self._prepare_content(data['content'])
        
        view = EditView(self.model_chapters, 
            ok_url=url_for(TutorialView.view_chapter, id=id), 
            obj=obj, pre_save=pre_save)
        return view.run()
    
    def delete_chapter(self, id):
        """
        删除章节
        删除时，如果有子结点，则子结点的父结点应变成当前结点的父结点
        """
        obj = self.model_chapters.get_or_notfound(int(id))
        tutorial = obj.tutorial
        count = obj.comments_count
        parent = obj._parent_
        
        #修改所有子结点的父结点
        obj.children_chapters.update(parent=parent)
        
        #删除当前章节
        obj.delete()
        
        #删除所属教程的评论数目
        tutorial.comments_count = max(0, tutorial.comments_count-count)
        tutorial.save()
        
        #跳转回教程展示页面
        return redirect(url_for(TutorialView.read, id=tutorial.id))
    
    def view_paragraph_comments(self, cid):
        """
        view_paragraph_comments/<cid>?para=pid
        显示某个段落的评论
        """
        
        _id = int(cid)
        pid = int(request.GET.get('para', 0))
        objects = self.model_comments.filter(
            (self.model_comments.c.chapter==_id) & 
            (self.model_comments.c.anchor==pid) &
            (self.model_comments.c.deleted==False)
        )
        
        def get_objects(objects):
            for row in objects:
                yield self._get_comment_data(row)
                
        return {'objects':get_objects(objects), 'object_id':_id, 'pid':pid}
    
    def _get_comment_data(self, obj, data=None):
        from uliweb.utils.timesince import timesince
        from uliweb.utils.textconvert import text2html
        from uliweb.orm import NotFound
        d = {}
        try:
            obj.modified_user
        except NotFound:
            obj.modified_user = None
            obj.save()
            
        print 'xxxxxxxxxxxxxxxxxxxxxx', obj.id, obj.modified_user
        d['username'] = unicode(obj.modified_user)
        d['image_url'] = functions.get_user_image(obj.modified_user, size=20)
        d['date'] = timesince(obj.modified_date)
        d['content'] = text2html(obj.content)
        return d
        
    def add_paragraph_comment(self, cid):
        """
        添加某个段落的评论
        """
        from uliweb.utils.generic import AddView
        
        default_data = {'chapter':int(cid), 'anchor':int(request.GET.get('para'))}
        view = AddView(self.model_comments, success_data=self._get_comment_data, 
            default_data=default_data)
        return view.run(json_result=True)
    
    def get_paragraph_comments_count(self, cid):
        """
        获得某个章节每个paragraph评论的数目
        返回结果为：
        
        {id1:count1, id2:count2,...}
        """
        from uliweb.orm import do_
        from sqlalchemy.sql import select, func, and_
        
        query = select([func.count(1), self.model_comments.c.anchor], 
            and_(self.model_comments.c.chapter==int(cid),
                self.model_comments.c.deleted==False)).group_by(self.model_comments.c.anchor)
        d = {}
        for row in do_(query):
            d[row[1]] = row[0]
        return json(d)
    
    def change_titles_order(self, id):
        """
        修改教程的顺序
        id为教程id
        """
        from json import loads
        
        d = {}
        for x in loads(request.POST['data']):
            d[int(x['id'])] = {'parent':x['parent'] or None, 'order':x['order']}
        for row in self.model_chapters.filter(self.model_chapters.c.tutorial==int(id)):
            if row.id in d:
                row.parent = d[row.id]['parent']
                row.order = d[row.id]['order']
                row.save()
        return json({'success':True})