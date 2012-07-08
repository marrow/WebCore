try:
    from pyamf.remoting.client import RemotingService
except ImportError:
    print 'You need to install PyAMF to run this example.'
    raise


gw = RemotingService('http://127.0.0.1:8080/')
service = gw.getService('test')

print service.hello('AMF')
print service.hello()
