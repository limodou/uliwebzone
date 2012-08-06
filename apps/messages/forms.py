#coding=utf-8
from uliweb.form import *
from uliweb.i18n import ugettext_lazy as _
from uliweb.utils.generic import RemoteField,ReferenceSelectField

class SendMessageForm(Form):
    form_buttons = Button(value=_('Send'), type='submit', _class="btn btn-primary")
    users = SelectField(label=_('Receiver'), multiple=True, html_attrs={'url':'/users/search'}, required=True)
    message = TextField(label=_('Message'), required=True, default = '')
