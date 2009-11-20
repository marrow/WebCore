**************************
Web Application Components
**************************

Any sufficiently advanced application is split into discrete and independently verifiable components.  In WebCore most of these components are WSGI middleware layers; they are given the opportunity to process the request coming from the user before your application is called, and process the result returned by your application before it reaches the user.

Internal to your own application we recommend Model, View, Controller (MVC) separation.

.. contents:: Table of Contents
   :depth: 2
   :local:


Model, View, Controller
=======================

MVC is a software architecture that separates the components of the application: the model represents the business logic or data; the view represents the user interface; and the controller manages user input or, in some cases, the application flow.  This form of separation has become the de-facto standard not just for web applications, but for desktop software as well.


Why MVC?
--------

There are several core reasons why MVC is beneficial compared to more liberal "tag soup" solutions where code is mixed with presentation:

* Code with distinct, separate goals is much easier to maintain.
* Components can be re-written without impact to the other areas of the application.
* It becomes easy to create additional views on the same data (e.g. pretty HTML, RSS, XML interchange).
* It is easier to perform unit and functional testing of the components.  (Testing also makes rewriting easier.)

One very important point about MVC, especially if you come from a background of other MVC frameworks, is that what you believe MVC to be is probably wrong.  Here are a few excellent articles you can read to get a more complete understanding of this separation:

* http://blog.dmcinsights.com/series/understanding-mvc/
* http://blog.astrumfutura.com/archives/373-The-M-in-MVC-Why-Models-are-Misunderstood-and-Unappreciated.html
* http://articles.techrepublic.com.com/5100-10878_11-1049862.html


Controller
----------

Controllers are the glue that take a user request, perform some action based on the input, and combines modelled data with a view for presentation back to the user.  In the simplest case, a "hello world" example, the controller takes no input and always returns the same view:

.. code-block:: python

   def index(self):
      return "project.templates.hello", dict()

Obviously real-world controllers would be slightly more complicated, returning data (from a model) to the template, accepting input, validating form data (using the model), and generally doing anything you can do in Python, because it **is** Python.  Controllers are, however, the least re-usable component of any web application, hardest to test thoroughly, and most prone to breaking if any of the other components change.

Keep your controllers light-weight, specific, and avoid duplicating the functionality of the other layers.  Your controller should not be a mutated model.


Understanding Object Dispatch
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

WebCore takes one of several different approaches to finding which controller to use.  The default, and probably the quickest to get started with, is object dispatch.  When a request comes in for a certain URL, the URL is split into components at each ``/`` character.  The object dispatch dialect then attempts to find the most specific controller available using the following logic:

1. Set the current item to be the root controller.
2. If there are no parts remaining, attempt to call the ``index`` method and return, or continue if there is no ``index`` method.
3. Pop the next part of the beginning of the path and look up an attribute in the current item by that name, setting the current item to this attribute.
4. If the current item isn't protected (prefixed with an underscore)...

   1. If it's an instance of another dialect, pass the request off to it.
   2. If it's an object dispatch controller, go back to step 2.
   3. If it's a method, call it and return.

5. If there is a method in the previous item called ``default``, call it and return.
6. If there is a method in the previous item called ``lookup``, call it, set the list of remaining parts to the returned value, and go back to step 2.
7. Nothing has worked, return a 404 Not Found error.


Protected Methods
^^^^^^^^^^^^^^^^^

WebCore adheres to the de-facto standard to mark attributes (including methods) as private by prefixing the name of the attribute with an underscore.  While Python itself does not enforce single underscore prefixes (and barely enforces double underscore prefixes) WebCore will prevent access to all attributes that feature the prefix.  You can still use underscore-prefixed path elements, however, as the value will be passed to a valid controller method, the ``default`` method, or ``lookup`` method, if defined.


Arguments
^^^^^^^^^

GET and POST variables are automatically decoded and passed to your controller as keyword arguments, with POST taking precedence.  Elements that occur multiple times in the query string or POST body will be transformed into a list of values automatically.  (No need for PHP's list argument style of using a ``[]`` suffix.)

If there are remaining path elements, they are passed as positional arguments.


Advanced Dispatch
^^^^^^^^^^^^^^^^^

There are four methods you can define in your controller class to effect the dispatch process:

``__before__``
   Called before the request method.  You can use this method to filter the arguments passed to the request method or otherwise execute code beforehand, e.g. to perform controller-wide authorization.
   
   .. code-block:: python
   
      class Foo(Controller):
          def __before__(self, *args, **kw):
              # Perform your actions here...
              # Finally, allow superclasses to modify the arguments as well...
              return super(Foo, self).__before__(*args, **kw)

``__after__``
   Called after the request method.  You can use this to filter the data passed to the template, change the template, or perform other actions as desired.  As per ``__before__`` with the first positional argument being the result of the controller call.

``default``
   If present this method will be called if no valid attribute can be found for the current path element.  This method is passed the remaining path elements (including the one that triggered the call to ``default``) as positional arguments and the GET/POST data as keyword arguments.  The default method is treated as a standard controller method.

``lookup``
   If present this method will be called if no valid attribute can be found for the current path element, and only if no ``default`` method is available.  This method directly alters the dispatch mechanism allowing you to redirect the path of attribute descent.
   
   The most common use of this method is to allow for RESTful dispatch of model objects.  The ``lookup`` method is passed the remaining path elements as positional arguments and GET/POST data as keyword arguments.  This method should return a 2-tuple of a new controller to continue descent through and a tuple or list of remaining path elements.
   
   For more information, see the :ref:`dispatch-section` chapter.


Model
-----

The model is responsible for storing all data, period.  This can mean data stored in a relational database, browser session, or cache.  The model is also responsible for all rules, restraints, and access and behaviour requirements for this data, such as input validation, formatting, and business logic.

"Now wait just a moment!" you may be telling the screen, or paper, if you have a dead tree copy of this document, "Shouldn't logic be put in the controller?"  Yes and no.  The model doesn't just represent mere data, it represents the entire system for which that data is useful.

For more information see the :ref:`databases-section` section and Sessions & Caching in this chapter.


View
----

For more information see the :ref:`templating-section` section.


Sessions & Caching
==================


Debugging
=========


Static Files
============


Compression
===========


