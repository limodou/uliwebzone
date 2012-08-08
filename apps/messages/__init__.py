from uliweb.orm import get_model
import re

def send_message(from_, to_, message, type='3'):
    """
    Send message
    :para to_: can be a list
    """
    Message = get_model('message')
    
    if not isinstance(to_, (tuple, list)):
        to_ = [to_]
    for x in to_:
        if not isinstance(x, (int, long)):
            x = x.id
        if not isinstance(from_, (int, long)):
            from_ = from_.id
        
        obj = Message(type=type, message=message, sender=from_, user=x)
        obj.save()
    
        #only user send message will create sended message
        if type == '3':
            obj = Message(type=type, message=message, sender=from_, user=x, send_flag='s')
            obj.save()
            
re_at = re.compile(u'@[a-zA-Z0-9_\u4E00-\u9FFF\.]+')
def parse_user(text):
    from uliweb.orm import get_model
    from uliweb import request
    
    User = get_model('user')
    
    for x in re_at.findall(text):
        user = User.get(User.c.username==x[1:])
        if user and user.id != request.user.id:
            yield user
    
