********************************
Authentication and Authorization
********************************

.. contents:: Table of Contents


Getting Ready
=============

Before we get started with the nitty gritty code you'll need to do a little planning first. You'll need to answer the following:

* How do you identify users?  E-mail address, username, numerical ID?  Do you use multiple values (composite keys) to identify users?
* What form does authorization need to take?  Group membership, more detailed permissions or roles?

The answers to these questions will determine how far from this chapter you will have to vary your own code.  All of the examples in this chapter assume declarative SQLAlchemy and a fairly simple user/group structure.  This is mainly for the sake of brevity.


Configuring CoreAuth
====================

To enable CoreAuth in your application, define the following in your INI file (or pass as an argument to ``Application.factory``):

.. code-block:: ini

   web.auth = True

CoreAuth requires that Beaker sessions be enabled.

The following are descriptions of the configuration values and their defaults:

``web.auth.triggers`` (default: ``401``)
   A comma-separated list of HTTP status codes that will trigger redirection to the login form.

``web.auth.name`` (default: ``uid``)
   The name of the session variable to store the user identifier upon successful login.

``web.auth.lookup`` (no default; **required**)
   A reference to a callable that transforms the session stored identifier into a usable user object.
   
   The callable must accept at least one argument, the identifier stored in the session, and return an object or ``None``.

``web.auth.authenticate`` (default: ``None``)
   If supplied, this callable will be used to perform authentication.  It must have the same signature as the ``web.auth.authenticate`` function, and return a tuple of ``(identifier, object)`` or ``None``.

``web.auth.handler`` (default: ``/login``)
   The path to redirect to if authentication is needed.

``web.auth.internal`` (default: ``False``)
   Perform an internal redirect (vs. HTTPTemporaryRedirect) when authentication is needed.  This allows for the preservation of HTTP POST variables.

Both ``web.auth.lookup`` and ``web.auth.authenticate`` accept the following syntax for defining a callable:

Direct reference:
   ``package.subpkg.mod:callable``

Static method reference:
   ``package.subpkg.mod:Class.method``

Callable reference:
   If you configure CoreAuth, not through an INI file, but directly, you can pass in a callable object instead of passing a string reference.


A Basic Model
=============

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


Writing your Controllers
========================

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


Tying it All Together
=====================

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


Authorization Predicates
========================

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.


Authorization in Templates
==========================

Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur. Excepteur sint occaecat cupidatat non proident, sunt in culpa qui officia deserunt mollit anim id est laborum.
