def call(app, var, env):
    a = []
    a.append('pageslide/jquery.pageslide.css')
    b = []
    b.append('pageslide/jquery.pageslide.js')
    return {'toplinks':a, 'bottomlinks':b, 'depends':['jquery']}
