from uliweb.orm import get_model

def send_message(from_, to_, message, type='3'):
    """
    Send message
    :para to_: can be a list
    """
    Message = get_model('message')
    
    if not isinstance(to_, (tuple, list)):
        to_ = [to_]
    for x in to_:
        obj = Message(type=type, message=message, sender=from_, user=x)
        obj.save()
    
    #only user send message will create sended message
    if type == '3':
        obj = Message(type=type, message=message, sender=from_, user=to_, send_flag='s')
        obj.save()