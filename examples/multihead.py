# encoding: utf-8

"""Allow a single method to return different data formats."""

from web.dialect.helper import render, condition


class Root(object):
    @render('mako:./multihead.html')  # default if no extension
    @render('mako:./multihead.html', 'html')  # /details.html
    @render('mako:./multihead.xml', 'xml')  # /details.xml
    @render('json:')  # /details.json
    @render('bencode:')  # /details.bencode
    @render('yaml:')  # /details.yaml
    def details(self):
        return dict(name="Bob", age=27)
    
    @condition(False)
    def foo(self):
        return "We matched the predicate."
    
    @foo.condition(True)
    def foo(self):
        return "We matched a different predicate."



if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer

    HTTPServer('127.0.0.1', 8080, application=Application(Root)).start()
