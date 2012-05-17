# encoding: utf-8

"""Allow a single method to return different data formats."""

from web.dialect.helper import render, condition


class Root(object):
    @render('mako:myapp.templates.details')
    @render('json:')  # used if request.format == 'json'
    def details(self):
        return dict(name="Bob", age=27)
    
    @condition(predicate)
    def foo(self):
        return "We matched the predicate."
    
    @foo.condition(other_predicate)
    def foo(self):
        return "We matched a different predicate."



if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer

    HTTPServer('127.0.0.1', 8080, application=Application(Root)).start()
