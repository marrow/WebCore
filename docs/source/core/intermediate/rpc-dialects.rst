.. _rpc-section:

************
RPC Dialects
************

.. contents:: Table of Contents


XML-RPC
=======

XML-RPC is a simpler version of its "big brother", `SOAP <http://www.w3.org/TR/soap/>`_.
WebCore implements its `official specification <http://xmlrpc.scripting.com/spec.html>`_ with a few extras.

WebCore uses the :mod:`xmlrpclib` module from the Python standard library, so it also supports the following protocol
extensions:

* Support for <nil> (null, or None; controlled by the ``__allow_none__`` controller attribute)
* Support for <i8> (64-bit integers)

The following extensions, however, are currently **NOT** supported:

* Multicall
* Introspection

Example controller
------------------

.. code-block:: python

   from xmlrpclib import Fault

   from web.rpc.xml import XMLRPCController


   class ExampleController(XMLRPCController):
       def hello(self, name):
           return 'Hello, %s!' % name
      
       def add(self, x, y):
           return x + y

        def return_some_error(self):
           raise Fault(123, "Some error")

Controller attributes
---------------------

You can change the following options by setting their values directly on your controller class.

======================= ================================================================ ===================
Attribute               Meaning                                                          Default value
======================= ================================================================ ===================
``__allow_none__``      Use ``<nil>`` where None is given, else omit the value entirely. ``False``
``__max_body_length__`` Maximum size of the incoming request (in bytes).                 ``4194304`` (=4 Mb)

                        If the request body exceeds this size, a 411 HTTP error is
                        returned.
======================= ================================================================ ===================

Error handling
--------------

WebCore attempts to follow the de facto
`XML-RPC error coding specification <http://xmlrpc-epi.sourceforge.net/specs/rfc.fault_codes.php>`_ whenever possible.
However, as pointed out earlier, the introspection API from this specification has not been implemented.

To return specific XML-RPC Faults, you can raise the :class:`xmlrpclib.Fault` exception and give it the error code you
want. See the example controller for details.

If your application code (either the controller method, ``__before__`` or ``__after__``) raises any other exception,
WebCore returns an a Fault with code -32500 (Application Error).


JSON-RPC
========

The WebCore JSON-RPC implementation conforms to the
`v1.0 version of the specification <http://json-rpc.org/wiki/specification>`_

Example controller
------------------

.. code-block:: python

   from web.rpc.jsonrpc import JSONRPCController


   class ExampleController(JSONRPCController):
       def hello(self, name):
           return 'Hello, %s!' % name
      
       def add(self, x, y):
           return x + y

Error handling
--------------

When an exception is raised from your application code (either the controller method, ``__before__`` or ``__after__``),
WebCore returns a 500 HTTP error code along with a JSON-RPC error response, where the return value is ``null`` and
the error value is an object containing the following attributes:

* name: ``"JSONRPCError"``
* code: ``100``
* message: <the received exception converted into a string>
* error: <formatted traceback from the exception if ``web.core.config.debug`` is ``True``, else ``"Not disclosed."``>


AMF-RPC
=======

WebCore's AMF-RPC is an implementation of Flash Remoting, used by both `Flash <https://www.adobe.com/flashplatform/>`_
and `Flex <https://www.adobe.com/products/flex.html>`_ from Adobe Systems Incorporated. To use it, you need to have
the latest version of `PyAMF <pypi.python.org/pypi/PyAMF>`_ installed.

Example controller
------------------

.. code-block:: python

   from web.rpc.amf import AMFController


   class ExampleController(AMFController):
       def hello(self, name):
           return 'Hello, %s!' % name
      
       def add(self, x, y):
           return x + y

Error handling
--------------

If your application raises an error, the exception is converted into a string on the server end, and a remoting error
is raised on the client. For PyAMF clients, the exception raised is :class:`pyamf.remoting.RemotingError`.


Nesting RPC controllers
=======================

It is often necessary to compose your RPC service of several different controllers. One such reason is maintaining a
clear structure and separation of concerns. In such cases, you can "nest" your controllers within each other in a
treelike fashion, as many levels deep as you want. You cannot, however, nest an RPC controller inside one of different
type.

.. code-block:: python

   from web.rpc.xml import XMLRPCController
   

   class ChildController(XMLRPCController):
       def some_child_method(self):
           return 'hello from child'

   class ParentController(XMLRPCController):
       child = ChildController()

       def some_parent_method(self):
           return 'hello from parent'

To execute ``some_child_method`` in this example, you'd point your RPC client to the **topmost parent** controller.
The name of the remote method would then be ``child.some_child_method``, while the parent's counterpart would simply be
``some_parent_method``.


Exposing RPC methods via multiple mechanisms
============================================

Exposing the same code via several different RPC mechanisms is easy. All you have to do is put your code in a plain
class and use it as a mix-in with the RPC controller classes. This allows you to eliminate any duplication of code.

.. code-block:: python

   from web.rpc.amf import AMFController
   from web.rpc.xml import XMLRPCController
   from web.core import Controller
   
   
   class ExampleRPCMixin(object):
       def hello(self, name):
           return 'Hello, %s!' % name
      
       def add(self, x, y):
           return x + y

   class ExampleXMLRPCController(XMLRPCController, ExampleRPCMixin): pass
   class ExampleAMFController(AMFController, ExampleRPCMixin): pass
   
   class RootController(Controller):
       xmlrpc_example = ExampleXMLRPCController()
       amf_example = ExampleAMFController()
