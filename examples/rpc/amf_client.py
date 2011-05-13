from pyamf.remoting.client import RemotingService


gw = RemotingService('http://127.0.0.1:8080/')
service = gw.getService('test')

print service.hello('AMF')
print service.hello()
