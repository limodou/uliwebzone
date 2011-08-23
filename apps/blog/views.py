#coding=utf-8
from uliweb import expose
from uliweb.orm import get_model

@expose('/blog')
class BlogView(object):
    def __init__(self):
        self.model = get_model('blog')
        
    def list(self):
        from uliweb.utils.generic import ListView
        
        pageno = request.GET.get('page', 0)
        
        view = ListView(self.model, pageno=pageno, order_by=self.model.c.publish_date.desc())
        return {'blogs':view.query(), 'view':view, 'count':view.query().count()}
    
    def add(self):
        from uliweb.utils.generic import AddView
        
        view = AddView(self.model, url_for(BlogView.list), default_data={'author':request.user.id})
        return view.run()

    def delete(self, id):
        from uliweb.utils.generic import DeleteView
        
        def validator(obj):
            if obj.author != request.user.id:
                return _("You can't delete this article, because you are not the author") 
            
        obj = self.model.get(int(id))
        view = DeleteView(self.model, url_for(BlogView.list), obj=obj,
            validator=validator)
        return view.run()