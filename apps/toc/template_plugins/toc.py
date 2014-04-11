def call(app, var, env):
    a = []
    a.append('toc/toc.js')
    b = []
    b.append('toc/toc.css')
    return {'bottomlinks':a, 'toplinks':b, 'depends':['jquery']}
