# encoding: utf-8

"""Everything all in one convienent file."""

from web.dialect.route import route
from web.dialect.helper import Resource, Collection, method, render, require


class Person(Resource):
    def _get(self):
        return "Person details."

    def _post(self):
        # Often not supported!
        return "Create a child object."

    def _put(self):
        return "Replace or create this person."

    def _delete(self):
        return "Delete this person."


class People(Collection):
    __resource__ = Person

    def _get(self):
        return "List of people."

    def _post(self):
        return "Create new person."

    def _put(self):
        return "Replace all people."

    def _delete(self):
        return "Delete all people."


class Routed(object):
    __dispatch__ = 'route'

    @route('/')
    def index(self):
        return "Root handler."

    @route('/page/{name}')
    def page(self, name):
        return "Page handler for: " + name


class Root(object):
    people = People
    diz = Routed
    
    # The following is a static page definition.
    about = 'myapp.templates.about', dict()
    
    # This works, too!  In fact, you can use any registry-handleable value!
    readme = open('../README.textile', 'r')
    
    def __call__(self):
        """Handle "index" lookups."""
        return "Path: /"
    
    def index(self):
        """Handle calls to /index -- this is no longer the 'default' index lookup."""
        return "Path: /index"
    
    def template(self):
        context.log.warning("Returning template result.")
        return 'mako:./test.html', dict()
    
    @method.get
    def login(self):
        return "Present login form."
    
    @login.post
    def login(self, **data):
        # can call login.get() to explicitly call that handler.
        return "Actually log in."
    
    @render('mako:myapp.templates.details')
    @render('json:')  # used if request.format == 'json'
    def details(self):
        return dict(name="Bob", age=27)

    @require(predicate)
    def foo(self):
        return "We matched the predicate."

    @foo.require(other_predicate)
    def foo(self):
        return "We matched a different predicate."
    
    @foo.otherwise
    def foo(self):
        return "We didn't match anything.  :("
    
    def __getattr__(self, name):
        if name.isdigit():
            return lambda: "Numerical lookup!"
        
        raise AttributeError()



if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer

    HTTPServer('127.0.0.1', 8080, application=Application(Root)).start()
