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

Callable references:
   If you configure CoreAuth, not through an INI file, but directly, you can pass in a callable object instead of passing a string reference.


A Basic Model
=============

The following is a basic SQLAlchemy Declarative model for user, group, and permission management.  You can save this to a file in your model package called ``auth.py`` and import its contents into your model's ``__init__.py`` to use it as-is.  If you used the graphical quick start tool and enabled authentication, you will already have a copy of this file in your project.

.. code-block:: python

   # encoding: utf-8

   import web

   from datetime import datetime

   from sqlalchemy import *
   from sqlalchemy.orm import *
   from sqlalchemy.ext.associationproxy import association_proxy

   from .base import Base


   __all__ = ['Account', 'account_groups', 'Group', 'group_permissions', 'Permission']



   class Account(Base):
       __tablename__ = 'accounts'
       __repr__ = lambda self: "Account(%s, '%s')" % (self.id, self.name)
    
       id = Column(String(32), primary_key=True)
       name = Column(Unicode(255), nullable=False)
       _password = Column('password', String(128))
    
       def _set_password(self, value):
           if value is None:
               self._password = None
               return
        
           import hashlib
           encoder = hashlib.new('sha512')
           encoder.update(value)
           self._password = encoder.hexdigest()
    
       password = synonym('_password', descriptor=property(lambda self: self._password, _set_password))
    
       groups = association_proxy('_groups', 'id')
    
       @property
       def permissions(self):
           perms = []
        
           for group in self._groups:
               for perm in group.permissions:
                   perms.append(perm)
        
           return set(perms)
    
       @classmethod
       def authenticate(cls, identifier, password=None, force=False):
           if not force and not password:
               return None
        
           try:
               user = cls.get(identifier)
        
           except:
               return None
        
           if force:
               return user.id, user
        
           import hashlib
           encoder = hashlib.new('sha512')
           encoder.update(password)
        
           if user.password is None or user.password != encoder.hexdigest():
               return None
        
           return user.id, user


   account_groups = Table('account_groups', Base.metadata,
                       Column('account_id', String(32), ForeignKey('accounts.id')),
                       Column('group_id', Unicode(32), ForeignKey('groups.id'))
               )


   class Group(Base):
       __tablename__ = 'groups'
       __repr__ = lambda self: "Group(%s, %r)" % (self.id, self.name)
       __str__ = lambda self: str(self.id)
       __unicode__ = lambda self: self.id
    
       id = Column(String(32), primary_key=True)
       description = Column(Unicode(255))
    
       members = relation(Account, secondary=account_groups, backref='_groups')
       permissions = association_proxy('_permissions', 'id')


   group_permissions = Table('group_perms', Base.metadata,
                       Column('group_id', Unicode(32), ForeignKey('groups.id')),
                       Column('permission_id', Unicode(32), ForeignKey('permissions.id'))
               )


   class Permission(Base):
       __tablename__ = 'permissions'
       __repr__ = lambda self: "Permission(%s)" % (self.id, )
       __str__ = lambda self: str(self.id)
       __unicode__ = lambda self: self.id
    
       id = Column(String(32), primary_key=True)
       description = Column(Unicode(255))
    
       groups = relation(Group, secondary=group_permissions, backref='_permissions')


Writing your Controllers
========================

You will need to write controllers to handle authentication, account creation, lost password recovery, and sign-out.  The following covers logging in and out.  Save this to a file called ``account.py`` in your controllers module, replacing YOURPROJECT with the name of your project's package.

.. code-block:: python

   # encoding: utf-8

   import web
   from web.auth import authenticate, deauthenticate
   from marrow.util.bunch import Bunch


   from YOURPROJECT import model as db


   __all__ = ['join', 'recover', 'login', 'logout', 'AccountMixIn']
   log = __import__('logging').getLogger(__name__)



   class JoinMethod(web.core.RESTMethod):
       def get(self):
           return "YOURPROJECT.templates.join", dict()
    
       def post(self, **kw):
           pass

   join = JoinMethod()


   class RecoverMethod(web.core.RESTMethod):
       def get(self):
           return "YOURPROJECT.templates.recover", dict()
    
       def post(self, **kw):
           pass

   recover = RecoverMethod()


   class LoginMethod(web.core.RESTMethod):
       def get(self, redirect=None):
           if redirect is None:
               referrer = web.core.request.referrer
               redirect = '/' if referrer.endswith(web.core.request.script_name) else referrer
        
           return "YOURPROJECT.templates.login", dict(redirect=redirect)
    
       def post(self, **kw):
           data = Bunch(kw)
        
           if not web.auth.authenticate(data.username, data.password):
               return "YOURPROJECT.templates.login", dict(redirect=kw['redirect'])
        
           if data.redirect:
               raise web.core.http.HTTPFound(location=data.redirect)
        
           raise web.core.http.HTTPFound(location='/')

   login = LoginMethod()
    

   def logout(self):
       web.auth.deauthenticate()
       raise web.core.http.HTTPSeeOther(location=web.core.request.referrer)


   class AccountMixIn(object):
       join = join
       recover = recover
       login = login
       logout = logout


Save the following to ``login.html`` in your templates folder:

.. code-block:: xml

   <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
   <html xmlns="http://www.w3.org/1999/xhtml"
           xmlns:py="http://genshi.edgewall.org/"
           xmlns:xi="http://www.w3.org/2001/XInclude">
    
       <xi:include href="${relative('YOURPROJECT.templates.master')}" />
    
       <head>
           <meta content="text/html; charset=UTF-8" http-equiv="content-type" py:replace="''" />
        
           <title>Login</title>
       </head>
    
       <body>
           <div class="content">
               <h1>Login</h1>
            
   			<form method="post" action="${web.request.script_name}">
   				<input type="hidden" name="redirect" value="${redirect}" />
				
   				<dl>
   					<dt>User Name:</dt>
   					<dd><input type="text" name="username" /></dd>
					
   					<dt>Password:</dt>
   					<dd><input type="password" name="password" /></dd>
					
   					<dt></dt>
   					<dd><input type="Submit" value="Login" /></dd>
   				</dl>
   			</form>
           </div>
       </body>
   </html>


Tying it All Together
=====================

Change your root controller's class definition to include the AccountMixIn class to make the login/logout/etc. methods available to the web:

.. code-block:: python

   from .account import AccountMixIn
   
   # ...
   
   class RootController(web.core.Controller, AccountMixIn):
      # ...


Authorization Predicates
========================

As every data structure and project requirement is different, WebAuth leaves predicate definition up to you.  If you are using the structure given above you may find the following predicates useful.  At the top of the ``root.py`` controller module add the following code:

.. code-block:: python

   from web.auth import authorize
   
   web.auth.in_group = web.auth.ValueIn.partial('groups')
   web.auth.has_permission = web.auth.ValueIn.partial('permissions')

This will create two new predicates, ``in_group`` and ``has_permission``, and register them globally.

To use these predicates to protect your controllers, you can use the ``authorize`` decorator:

.. code-block:: python

   class RootController(...):
      @authorize(web.auth.in_group('admin'))
      def admin_only(self):
         return "You are an administrator!"
      
      @authorize(web.auth.has_permission('modify'))
      def modify(self):
         return "You are allowed to modify things."

Or you can even use the predicates directly:

.. code-block:: python

   def hello(self):
      if web.auth.in_group('admin'):
         return "Hello administrator!"
      
      if web.auth.authenticated:
         return "Hello " + web.auth.user.name + "!"
      
      return "Hello world!"

See the API documentation for a description of the various predicates and predicate constructors.


Authorization in Templates
==========================

You have access to all standard and registered predicates from within your templates using the ``web.auth`` namespace.
