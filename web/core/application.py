# encoding: utf-8

"""The base WSGI application definition.

Applications which use the WebCore framework plug into this base application.
"""

import types
import paste
import web

from webob import Request, Response
from web.core import middleware
from web.core.dialects import Dialect
from marrow.util.object import load_object


__all__ = ['Application']
log = __import__('logging').getLogger(__name__)


class Application(object):
    """A WSGI-compliant application base.

    This implements the basics nessicary to function as a WSGI application.

    Additionally, if you need more than a simple WSGI application (which can
    be used with other WSGI components) and would like a full-stack
    environment, you can use the factory method to create a complete
    environment.
    """

    def __init__(self, root=None, config=dict()):
        self.app = self
        self.root = root
        self.config = config

        web.core.config.update(config)

        if not isinstance(self.root, Dialect) and not hasattr(self.root, '__call__'):
            raise TypeError('Root controller must be dialect subclass or executable.')

        if not isinstance(self.root, Dialect):
            log.warning("Non-dialect root controller specified.")
            log.warning("We will assume %r is a raw WSGI application, which is probably wrong.", self.root)

    @classmethod
    def middleware(cls):
        """Generate a sorted dependency graph of middleware.

        Might not be the most efficient implementation, but it works and is only run on startup.

        The @web.core.middleware.middleware decorator can be used to register middleware.

        This allows you to inject middleware at any point in the stack and even override default
        layers (while still maintaining dependency graph resolution).
        """

        queue = [i for i in middleware.registry if i.after is None]
        satisfied = []
        available = [i.name for i in middleware.registry]

        while queue:
            obj = queue.pop(0)
            satisfied.append(obj.name)

            log.debug("Loading middleware: %r", obj)
            yield obj

            for obj in middleware.registry:
                if obj.name in satisfied or obj in queue:
                    continue

                if isinstance(obj.after, list):
                    deps = [(i in satisfied) for i in obj.after if i in available]
                    if not all(deps):
                        continue
                elif obj.after is "*" and queue:  # pragma: no cover -- this works, but profiling can't be tested
                    continue
                elif obj.after not in satisfied:
                    continue

                queue.append(obj)

    @classmethod
    def factory(cls, gconfig=dict(), root=None, **config):
        """Build a full-stack framework around this WSGI application."""

        log = __import__('logging').getLogger(__name__ + ':factory')
        log.info("Preparing WebCore WSGI middleware stack.")

        # Define the configuration earlier to allow the root controller's __init__ to use it.
        web.core.config = gconfig.copy()
        web.core.config.update(config)

        config = web.core.config

        root = config.get('web.root', root)
        log.debug("Root configured as %r.", root)

        # Find, build, and configure our basic Application instance.
        if isinstance(root, basestring):
            config['web.root.package'] = root.split('.', 1)[0]
            log.debug("Loading root controller from '%s'.", root)
            root = load_object(root)

        if isinstance(root, type):
            root = root()

        if not isinstance(root, Dialect) and not hasattr(root, '__call__'):
            raise ValueError("The root controller must be defined using package dot-colon-notation or direct reference and must be either a WSGI app or Dialect.")

        config['web.root'] = root

        app = cls(root, config)
        base_app = app

        for mware in cls.middleware():
            app = mware(app, config)

        base_app.app = app

        log.info("WebCore WSGI middleware stack ready.")

        return app

    def __call__(self, environment, start_response):
        environment['web.app'] = self.app
        environment['web.base'] = environment.get('SCRIPT_NAME', '')

        try:
            if 'paste.registry' in environment:
                environment['paste.registry'].register(web.core.request, Request(environment))
                environment['paste.registry'].register(web.core.response, Response(request=web.core.request))

                if 'beaker.cache' in environment:
                    environment['paste.registry'].register(web.core.cache, environment['beaker.cache'])

                if 'beaker.session' in environment:
                    environment['paste.registry'].register(web.core.session, environment['beaker.session'])

            if environment['PATH_INFO'] == '/_test_vars':
                paste.registry.restorer.save_registry_state(environment)
                start_response('200 OK', [('Content-type', 'text/plain')])
                return ['%s' % paste.registry.restorer.get_request_id(environment)]

            # Treat non-Dialects as plain WSGI apps
            if not isinstance(self.root, Dialect):
                return self.root(environment, start_response)

            content = self.root(web.core.request._current_obj())
        except web.core.http.HTTPException, e:
            environment['paste.registry'].register(web.core.response, e)
            return e(environment, start_response)

        if isinstance(content, Response):
            return content(environment, start_response)

        # Tuples are handled by the templating middleware
        if isinstance(content, tuple):
            return content

        if isinstance(content, (list, types.GeneratorType)):
            web.core.response.app_iter = content
        elif isinstance(content, unicode):
            web.core.response.unicode_body = content
        elif content is not None:
            web.core.response.body = content

        return web.core.response(environment, start_response)
