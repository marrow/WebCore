from wsgiref.simple_server import make_server
from pyramid.config import Configurator
from pyramid.response import Response
from waitress import serve as serve_
 
def hello(request):
    return Response('Hello %(name)s!' % request.matchdict)
 
if __name__ == '__main__':
    config = Configurator()
    config.add_route('hello', '/hello/{name}')
    config.add_view(hello, route_name='hello')
    app = config.make_wsgi_app()
    serve_(app, host='127.0.0.1', port=8080, threads=4)

