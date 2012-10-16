# encoding: utf-8

"""Basic class-based demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""


class Root(object):
    def __init__(self, context):
        self._ctx = context

    def mul(self, a: int = None, b: int = None) -> 'json':
        if not a and not b:
            return dict(message="Pass arguments a and b to multiply them together!")

        return dict(answer=a * b)


if __name__ == '__main__':
    from marrow.server.http import HTTPServer
    
    from web.core.application import Application
    from web.ext.template import TemplateExtension
    from web.ext.cast import CastExtension

    HTTPServer('127.0.0.1', 8080, application=Application(Root, dict(extensions=dict(
            template = TemplateExtension(),
            typecast = CastExtension()
        )))).start()
