#!/usr/bin/env python
# encoding: utf-8

from xmlrpclib import ServerProxy

try:
    import jsonrpclib
except ImportError:
    print 'You need to install jsonrpclib to run this example.'
    raise

try:
    from pyamf.remoting.client import RemotingService
except ImportError:
    print 'You need to install PyAMF to run this example.'
    raise


gw = RemotingService('http://127.0.0.1:8080/gateway')
service = gw.getService('test')
print service.hello()
print service.hello('AMF')

server = ServerProxy("http://127.0.0.1:8080/rpc")
print server.test.hello()
print server.test.hello('XML-RPC')

server = jsonrpclib.Server("http://127.0.0.1:8080/jsonrpc", version='1.0')
print server.test.hello()
print server.test.hello('JSON-RPC')
