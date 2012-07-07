# encoding: utf-8

from unittest import TestCase
from webob import Request
from nose.tools import raises, eq_
from web.core import Application, Controller
from web.core.templating import template
from web.core import templating


class RootController(Controller):
    @template('templates.test')
    def decorator(self):
        return dict()

    @template('templates.test')
    def decorator_simple(self):
        return b'test data'

    def tuple(self):
        return 'templates.test', dict(), dict()

    def variables(self):
        return 'templates.variables', dict()

    def unicode(self):
        return 'templates.unicode', dict(), {'genshi.default_encoding': None}

    def unicode_template(self):
        return u'templates.test', dict()

    def unicode_mako(self):
        return 'mako:templates.unicode_mako', dict()

    def registry(self):
        return 'templates.registry', dict()

    def bad(self):
        return object(), 'bar'

    def relative(self):
        return 'templates.relativetest', dict()


test_config = {'debug': True, 'web.widgets': False, 'web.sessions': False, 'web.compress': False, 'web.static': False}


class TestTemplates(TestCase):
    app = Application.factory(root=RootController, **test_config)

    def setup(self):
        self.__registry = list(templating.registry)

    def teardown(self):
        templating.registry = self.__registry

    def test_decorator(self):
        """Test decorator template generation."""
        response = Request.blank('/decorator').get_response(self.app)

        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.body == '<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>It works!</h1></body></html>'

    def test_decorator_simple(self):
        """Test returning a bytestring instead of template args from a decorated method."""
        response = Request.blank('/decorator_simple').get_response(self.app)

        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.body == b'test data'

    def test_tuple(self):
        """Test """
        response = Request.blank('/tuple').get_response(self.app)

        eq_(response.status, "200 OK")
        eq_(response.content_type, "text/html")
        assert response.body == '<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>It works!</h1></body></html>'

    def test_unicode(self):
        response = Request.blank('/unicode').get_response(self.app)

        eq_(response.status, "200 OK")
        eq_(response.content_type, "text/html")
        eq_(response.charset, "UTF-8")
        assert response.unicode_body == u'<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>© 2009</h1></body></html>'

    def test_unicode_template(self):
        response = Request.blank('/unicode_template').get_response(self.app)

        assert response.status == "200 OK"
        assert response.content_type == "text/html"
        assert response.body == '<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>It works!</h1></body></html>'

    def test_unicode_body(self):
        # This test was mostly added to test the middleware's ability to handle
        # a unicode return value from the renderer
        response = Request.blank('/unicode_mako').get_response(self.app)

        eq_(response.status, "200 OK")
        eq_(response.content_type, "text/html")
        eq_(response.charset, "UTF-8")
        eq_(response.unicode_body, u'<html><body><h1>© 2009</h1></body></html>')

    def test_template_globals(self):
        response = Request.blank('/variables').get_response(self.app)

        eq_(response.status, "200 OK")
        eq_(response.content_type, "text/html")
        assert response.body == '<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>It works!</h1></body></html>'

    def test_registry(self):
        templating.registry.append(lambda: {'var1': 123, 'var2': 456})
        response = Request.blank('/registry').get_response(self.app)

        eq_(response.status, "200 OK")
        eq_(response.content_type, "text/html")
        eq_(response.body, '<html xmlns="http://www.w3.org/1999/xhtml"><body>123 456</body></html>')

    @raises(TypeError, ValueError)
    def test_exception(self):
        Request.blank('/bad').get_response(self.app)

    def test_relative(self):
        response = Request.blank('/relative').get_response(self.app)
        eq_(response.body, '<html xmlns="http://www.w3.org/1999/xhtml"><body>subpackage/test.html</body></html>')

    def test_translator(self):
        environ = {'web.translator': lambda x: x.swapcase()}
        response = Request.blank('/tuple', environ=environ).get_response(self.app)
        eq_(response.body, '<html xmlns="http://www.w3.org/1999/xhtml"><body><h1>It works!</h1></body></html>')
