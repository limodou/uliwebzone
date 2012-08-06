#coding=utf-8

from uliweb.orm import *
from uliweb.utils.common import get_var

class Message(Model):
    __verbose_name__ = u'消息'
    
    type =  Field(CHAR, verbose_name='消息类别', max_length=1, choices=get_var('MESSAGES/MESSAGE_TYPE'))   
    message = Field(TEXT, verbose_name='内容')
    user = Reference('user', verbose_name='用户', collection_name='user_messages')
    read_flag = Field(bool, verbose_name='阅读标志')
    create_date = Field(datetime.datetime, verbose_name='创建时间', auto_now=True, auto_now_add=True)
    sender = Reference('user', verbose_name='创建人')
    send_flag = Field(CHAR, max_length=1, verbose_name='发送标志', default='r') #'s' 发送， 'r' 接收

    def __unicode__(self):
        return self.message
    
    class Table:
        fields = [
            'message',
            'type',
            'user',
            'read_flag',
            'create_date',
            'sender',
            'id',
            'send_flag',
            'user_image',
        ]
    
    @classmethod
    def OnInit(cls):
        Index('msg_idx', cls.c.user, cls.c.read_flag)
    