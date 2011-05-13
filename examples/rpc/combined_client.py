from xmlrpclib import ServerProxy, Error
import logging

from pyamf.remoting.client import RemotingService


path = 'http://127.0.0.1:8080/gateway'
gw = RemotingService(path)
service = gw.getService('test')

print service.hello('AMF')
print service.hello()

server = ServerProxy("http://127.0.0.1:8080/rpc")

print server.test.hello()
print server.test.hello('XML-RPC')
