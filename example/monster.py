# encoding: utf-8

"""Everything all in one convienent file.

Non-functional until the helpers get worked on a bit more.
"""

from web.dialect.route import route
from web.dialect.helper import Resource, Collection, method, render, require

from marrow.util.object import load_object as load


# REST Resources

class Person(Resource):
    def get(self):
        return "Person details."

    def post(self):
        # Often not supported!
        return "Create a child object."

    def put(self):
        return "Replace or create this person."

    def delete(self):
        return "Delete this person."


class People(Collection):
    __resource__ = Person

    def get(self):
        return "List of people."

    def post(self):
        return "Create new person."

    def put(self):
        return "Replace all people."

    def delete(self):
        return "Delete all people."


# Efficient URL Routing

class Routed(object):
    __dispatch__ = 'route'

    @route('/')
    def index(self):
        return "Root handler."

    @route('/page/{name}')
    def page(self, name):
        return "Page handler for: " + name


# Object Dispatch (and root)

class Root(object):
    # Attach the REST resource collection and routed "sub-directories".
    people = People
    diz = Routed
    
    # We can easily load from another module without cluttering globals.
    foo = load('myapp.controllers.foo:FooController')
    
    # The following is a static page definition.
    about = 'myapp.templates.about', dict()
    
    # This works, too!  In fact, you can use any registry-handleable value!
    readme = open('../README.textile', 'r')
    
    def __init__(self, context):
        self._ctx = context

    def __call__(self):
        """Handle "index" lookups."""
        return "Path: /"
    
    def index(self):
        """Handle calls to /index -- this is no longer the 'default' index lookup."""
        return "Path: /index"
    
    def template(self):
        self._ctx.context.log.warning("Returning template result.")
        return 'mako:./test.html', dict()
    
    # If HTTP verbs are your thing...
    
    @method.get
    def login(self):
        return "Present login form."
    
    @login.post
    def login(self, **data):
        # can call login.get() to explicitly call that handler.
        return "Actually log in."
    
    # Or conditional template / serializer usage based on filename extension:

    @render('mako:myapp.templates.details')
    @render('json:')  # used if request.format == 'json'
    def details(self):
        return dict(name="Bob", age=27)

    # Or straight-up if/elif/else:

    @require(predicate)
    def foo(self):
        return "We matched the predicate."

    @foo.require(other_predicate)
    def foo(self):
        return "We matched a different predicate."
    
    @foo.otherwise
    def foo(self):
        return "We didn't match anything.  :("
    
    # If you need to be able to dynamically load the next path element...

    def __getattr__(self, name):
        if name.isdigit():
            return lambda: "Numerical lookup!"
        
        raise AttributeError()
    
    # Or dynamically redirect object dispatch, possibly consuming *multiple* path elements...

    def __lookup__(self, *parts, **data):
        return Controller(), ()



if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer

    HTTPServer('127.0.0.1', 8080, application=Application(Root)).start()
