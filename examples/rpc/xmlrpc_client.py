#!/usr/bin/env python
# encoding: utf-8

from xmlrpclib import ServerProxy


server = ServerProxy("http://127.0.0.1:8080")

print server.hello()
print server.hello('XML-RPC')
