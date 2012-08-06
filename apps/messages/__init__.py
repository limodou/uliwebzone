from uliweb.orm import get_model

def send_message(from_, to_, message, type='3'):
    Message = get_model('message')
    
    obj = Message(type=type, message=message, sender=from_, user=to_)
    obj.save()
    
    #only user send message will create sended message
    if type == '3':
        obj = Message(type=type, message=message, sender=from_, user=to_, send_flag='s')
        obj.save()