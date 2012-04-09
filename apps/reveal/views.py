#coding=utf-8

from uliweb import expose

@expose('/test')
def test():
    return {}