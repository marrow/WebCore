# encoding: utf-8

"""Slightly more advanced example application."""


class Person:
    __dispatch__ = 'rest'
    
    def get(self):
        return "Person details."
    
    def post(self):
        # Often not supported!
        return "Create a child object."
    
    def put(self):
        return "Replace or create this person."
    
    def delete(self):
        return "Delete this person."


class Root:
    __dispatch__ = 'rest'
    __resource__ = Person
    
    def get(self):
        return "List of people."
    
    def post(self):
        return "Create new person."
    
    def put(self):
        return "Replace all people."
    
    def delete(self):
        return "Delete all people."



if __name__ == '__main__':
    from web.core.application import Application
    from marrow.server.http import HTTPServer

    HTTPServer('127.0.0.1', 8080, application=Application(Root)).start()
