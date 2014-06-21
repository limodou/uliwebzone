#coding=utf-8
from uliweb import expose, functions
from uliweb import expose, decorators, functions
from uliweb.orm import get_model, do_, NotFound



def userimage(obj):
      get_user_image = function('get_user_image')
      try:
            url = get_user_image(obj.posted_by)
      except NotFound:
            url = get_user_image()
      return url

@expose('/forumsEX')
def forumsEX():
	c = get_model('forumcategory')
 	forum = get_model('forum')
 	user = get_model('user')
	d = {'cate':{}}	
	
	for obj in c.all():
            	d['cate'].update({obj.name:obj.forums.all()})
	
	Topic = get_model('forumtopic')	
	top20 = Topic.all().order_by(Topic.c.id.desc()).limit(20)
	d['top20'] = top20
	response.template = "forumsEX_index.html"
	return d

