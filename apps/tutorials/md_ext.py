def code_comment(visitor, items):
    """
    Format:
        
        [[code-comment(target=pre element id)]]:
            key : value
            key : value
            
        or:
            
        [[code-comment(pre element id)]]:
            key : value
            key : value
        
    """
    from uliweb import json_dumps
    
    txt = []
    data = {}
    txt.append('<script type="text/code-comment">')
    for x in items:
        d = {}
        for line in x['body'].splitlines():
            if line.strip():
                k, v = line.split(':', 1)
                k = k.strip()
                if '=' in v:
                    title, v = v.split('=', 1)
                    title = title.strip()
                else:
                    title = k
                v = visitor.parse_text(v.strip(), 'article')
                d[k] = {'title':title, 'content':v}
        if len(x['kwargs']) == 1 and x['kwargs'].keys()[0] != 'target':
            key = x['kwargs'].keys()[0]
        else:
            key = x['kwargs'].get('target', '')
        if key in data:
            data[key] = data[key].update(d)
        else:
            data[key] = d
    txt.append(json_dumps(data))
    txt.append('</script>')
    return '\n'.join(txt)

def new_code_comment(visitor, block):
    """
    Format:
        
        {% code-comment target=pre element id %}
        key : value
        key : value
        {% endcode-comment %}    
        
        or
        
        {% code-comment pre element id %}
        key : value
        key : value
        {% endcode-comment %}    
        
    """
    from uliweb import json_dumps
    
    if 'new' in block:
        
        txt = []
        data = {}
        txt.append('<script type="text/code-comment">')
        d = {}
        for line in block['body'].splitlines():
            if line.strip():
                k, v = line.split(':', 1)
                k = k.strip()
                if '=' in v:
                    title, v = v.split('=', 1)
                    title = title.strip()
                else:
                    title = k
                v = visitor.parse_text(v.strip(), 'article')
                d[k] = {'title':title, 'content':v}
        if len(block['kwargs']) == 1 and block['kwargs'].keys()[0] != 'target':
            key = block['kwargs'].keys()[0]
        else:
            key = block['kwargs'].get('target', '')
        if key in data:
            data[key] = data[key].update(d)
        else:
            data[key] = d
        txt.append(json_dumps(data))
        txt.append('</script>')
        return '\n'.join(txt)
    else:
        return code_comment(visitor, block)

