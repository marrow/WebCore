#!/usr/bin/env python
# encoding: utf-8

"""A restful hello world application."""

import web.core

from web.core import Controller, url


class Child(Controller):
    def index(self):
        return url.compose('delete', confirm="yes")

    def hello(self, name="world"):
        return url.compose(name=name)


class Children(Controller):
    def __lookup__(self, id, *path, **data):
        web.core.request.path_info_pop()
        return Child(), path


class RootController(Controller):
    def index(self):
        return url.compose('list')

    def list(self):
        return url.compose('/child', 27)

    def secure(self):
        return url('/', protocol="https")

    def deep(self, path):
        return url() + '\n' + url.compose(path)

    child = Children()


if __name__ == '__main__':
    import logging
    from paste import httpserver
    from web.core import Application

    logging.basicConfig(level=logging.INFO)

    app = Application.factory(root=RootController, debug=True, **{
            'web.sessions': False,
            'web.widgets': False,
            'web.sessions': False,
            'web.profile': False,
            'web.static': False,
            'web.compress': False
        })

    httpserver.serve(app, host='127.0.0.1', port='8080')
