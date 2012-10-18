#coding=utf8

from uliweb import functions

def teacher(user):
    """
    是否是教师角色
    """
    Teacher = functions.get_model('class_teacher')
    obj = Teacher.get(Teacher.c.teacher == user.id)
    return bool(obj)
