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
	top20 = Topic.filter(Topic.c.closed==0).order_by(Topic.c.id.desc()).limit(20)
	d['top20'] = top20
	response.template = "forumsEX_index.html"
	return d

@expose('/forumsEX/topic/<id>')
def topic(id):
	c = get_model('forumcategory')
 	forum = get_model('forum')
 	user = get_model('user')
	d = {}	
	
        Post = get_model('forumpost')	
	Topic = get_model('forumtopic')	
	topic = Topic.get(int(id))
	Topic.filter(Topic.c.id==int(id)).update(num_views=Topic.c.num_views+1)

	d['topic'] = topic
	response.template = "forumsEX_topic.html"
	Posts        = Post.filter(Post.c.topic==int(id))
	post1 = Post.filter(Post.c.topic==int(id)).filter(Post.c.parent==None)
	d['post1'] = list(post1)[0]
	d['posts'] = Posts

	return d

