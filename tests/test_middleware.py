# encoding: utf-8

import web
from web.core import Application

from common import PlainController, WebTestCase


test_config = {
        'web.debug': False,
        'web.templating': False,
        'web.config': False,
        'web.widgets': False,
        'web.sessions': False,
        'web.compress': True,
        'web.profile': True,
        
        'web.auth': True,
        'web.auth.enable': True,
        'web.auth.setup.method': 'form, cookie',
        'web.auth.form.authenticate.user.data': 'visitor:open_sesame',
        'web.auth.cookie.secret': 'magical wiki',
        
        'web.static': True,
        'web.static.path': '/tmp'
    }



class RootController(PlainController):
    def index(self, *args, **kw):
        return "success"


class TestMiddleware(WebTestCase):
    app = Application.factory(root=RootController, **test_config)
    
    def test_index(self):
        # self.assertResponse('/', body="success")
        pass
