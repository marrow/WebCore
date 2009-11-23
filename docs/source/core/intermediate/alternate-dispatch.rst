.. _dispatch-section:

*****************************
Alternate Dispatch Mechanisms
*****************************

.. contents:: Table of Contents


CRUD Dispatch
=============

Create, read, update and delete, the four basic functions of persistent storage, is easily modelled using WebCore.

First, create a class that represents a resource:

.. code-block:: python

   class Resource(web.core.Controller):
       def __init__(self, id):
           "Load up the database record for this instance."
           self.record = model.Resource.get(id)
           super(Resource, self).__init__()
      
       def index(self):
           pass # ... read
      
       def delete(self):
           pass # ...
      
       def update(self):
           pass # ...

Now to list records, create new ones, and access specific records, you create a top-level controller:

.. code-block:: python

   class Resources(web.core.Controller):
       def index(self):
           pass # ... list
      
       def create(self):
           pass # ...
      
       def __lookup__(self, id, *args, **kw):
           "Load up the appropriate Resource controller and keep going from there."
           web.core.request.path_info_pop() # we consume one path element
           return Resource(id), args

Now requests like the following will work (if you map Resources to 'resource' in your root controller):

* ``http://localhost:8080/resource/`` -- list
* ``http://localhost:8080/resource/create`` -- create
* ``http://localhost:8080/resource/27/`` -- read
* ``http://localhost:8080/resource/27/delete`` -- delete
* ``http://localhost:8080/resource/27/update`` -- update


REST Dispatch
=============

REST stands for "Representational State Transfer", a way of applying a distinct set of methods to "resources".  In HTTP these methods are: GET, PUT, POST, and DELETE.  Each has a distinct meaning in one of two contexts: (from `Wikipedia <http://en.wikipedia.org/wiki/REST#HTTP_examples>`_)

``http://example.com/resources/``
   ``GET``
      **List** the members of the collection, complete with their member URIs for further navigation. For example, list all the cars for sale.
   
   ``PUT``
      **Replace** the entire collection with another collection.
   
   ``POST``
      **Create** a new entry in the collection where the ID is assigned automatically by the collection. The ID created is usually included as part of the data returned by this operation.
   
   ``DELETE``
      **Delete** the entire collection.

``http://example.com/resources/resid``
   ``GET``
      **Retrieve** a representation of the addressed member of the collection expressed in an appropriate MIME type
      
   ``PUT``
      **Update** the addressed member of the collection or **create** it with the specified ID.
   
   ``POST``
      Treats the addressed member as a collection in its own right and creates a new subordinate of it.
   
   ``DELETE``
      **Delete** the addressed member of the collection.

You may notice the similarity to the previous section's CRUD layout, and is, in fact, a more specific example of it.  WebDAV is an example of a complete system written with this structure.  To implement RESTful services in WebCore you use a combination of the techniques described by CRUD and a helper class.

The RESTMethod helper class understands all HTTP verbs: get, put, post, delete, head, trace, and options, with head and options written for you.

Form Processing
---------------

At its most light-weight, the RESTMethod helper class allows you to create a separation between the presentation of a form and the processing of the data returned by the form.  Take the following example controller:

.. code-block:: python

   class SignInMethod(web.core.RESTMethod):
      def get(self):
         reutrn "myapp.templates.signin", dict()
      
      def post(self, username, password):
         # handle form input
   
   class RootController(web.core.Controller):
       login = SignInMethod()


XML-RPC Dispatch
================

TBD.


Flex AMF Dispatch
=================

TBD.
