# encoding: utf-8

"""Template Rendering Extension

Rendering services for your application, extensions, and reusable components.

Context Additions: namespace, render()

Entry Points: marrow.templating


# Introduction

This extension provides a way for other components to ask for template files to be combined with data and rendered.

## Purpose

The template extension provides a mechanism to perform the following tasks:

* Render a template (defined by a path) using supplied data.

* Serialize supplied data into an encapsulation, transport, or interchange format, such as JSON.

* Allow application controllers to return a template path and data to use as the primary response to a request.

These tasks are independent of each-other, allowing you to use the extension for whole-page generated responses or
even content generation for use by other subsystems, such as e-mail messages.


## Requirements

### Python Packages

* [marrow.templating](https://github.com/marrow/templating/)

* an engine of your choice such as [`tenjin`](http://www.kuwata-lab.com/tenjin/) or
  [`mako`](http://www.makotemplates.org)

  
## Operation

During startup this extension registers a view for tuples and plain dictionaries.

When preparing the context on each request this extension adds two variables: a `namespace` dictionary and `render`
function. The namespace can be extended to provide variables to every template being rendered (by default a variable
called web, representing the context itself, will be made available to templates) and the render function may be
overridden.

If a controller returns a 2- or 3-tuple in the form `(str, dict[, dict])` a template whose name is given by the
string value will be rendered with data from the first dictionary, with engine settings provided by an optional second
dictionary. If a controller running on Python 3 returns a dictionary and has a return value annotation, that
annotation will be used as per the first tuple element of a tuple return.


# Usage

Before any template engines may be utilized you must first activate this extension. To do so add, at a minimum, an
empty template section to your configuration's `application.extensions` section. An example of this in YAML, with all
other configuration directives omitted, would be the following three lines::

	application:
	    extensions:
	        template:

See the next section for the allowable template extension configuration directives.

Once your application is configured to process template return types you can return 2- or 3-tuples from within your
controllers. An example controller would be::

	class Controller(object):
	    def hello(self, name="world"):
	        return 'mako:myapp.templates.hello', dict(name=name)

If you have defined a default template engine that component of the template path may be omitted. For a full reference
of the allowable template references see the [marrow.templating
documentation](https://github.com/marrow/templating/#4-acceptable-path-references).


## Configuration

The following configuration directives are supported:

`default`
:   The default template engine to utilize if no engine is explicitly defined in the template path being rendered.
    Setting a default means you won't need to prefix all of your template paths with an engine, potentially saving a
    a lot of space.  Remember, if you are writing a reusable component, *always* prefix your template paths with an
    engine!

`path`
:   An optional path to base relative template paths on.  If you define a path here then relative templates (e.g.
    `mako:./welcome.html`) will be relative to that path.  Reusable components should never use relative paths.

`override`
:   A dictionary mapping template path prefixes to their replacements, or lists of replacements. This is an advanced
    feature described in greater detail later, in a section entitled [Overriding Template Selection](#).

A more complete templating configuration example would then be::

	application:
	    extensions:
	        template:
	            default: mako
	            path: /path/to/use/for/relative/templates
	            override:
	                web.app.blog: myblog


## Features for Python 3

Under Python 3 (and Python 2 with an appropriate decorator) you may hard-code the template path for your controllers
using [function annotations](http://www.python.org/dev/peps/pep-3107/). This is especially useful for controller
methods that always return serialized data such as JSON; for example::

	class Controller(object):
	    def hello(self, name="world") -> 'json':
	        return dict(hello=name)

You may also define a proper template name::

	class Controller(object):
	    def hello(self, name="world") -> 'myapp.templates.hello':
	        return dict(name=name)


# Extending

## Adding Engines

This extension relies on an external adapter package called
[`marrow.templating`](https://github.com/marrow/templating/) to provide a unified interface to disparate template
engines. In order to extend this system with support for additional template engines or serializers, please read the
[appropriate section of the `marrow.templating`
manual](https://github.com/marrow/templating/#5-extending-marrow-templating).


## Template Namespace

Extensions may extend the global template namespace by adding attributes to the `namespace` context attribute during
the `prepare` callback. Extensions that do this must declare that they depend on the `template` extension by adding it
to their `uses` or `needs` class attribute. If template services are not **required** (listed in `uses`, not `needs`)
access to the namespace context attribute must be armoured against namespace not being present.

Creating an extension for your application for the purpose of extending the template namespace is not unusual. Below
is an example minimal extension that adds the operator module to all templates::

	class ApplicationExtension(object):
	    needs = ['template']
	    
	    def prepare(self, context):
	        context.namespace.operator = __import__('operator')


## Overriding Template Selection

If you define an override mapping (whose values may be a string or list of strings) then templates for the given
namespace will search there first.  For example::

	return 'mako:web.app.blog.template.comment', dict()

With the following override::

	override:
		web.app: mysite
	    web.app.blog: mysite.blog

The framework will try look for templates in this order:

* mysite.blog.template.comment

* mysite.template.comment

* web.app.blog.template.comment

Note that these overrides are prefix overrides; you can only replace from the beginning of the template path.  You can
also override the template engine: simply prefix your override value with the engine and a colon.  The deepest (most
specific) override is preferred over less-specific ones.


## Overriding Behaviour

Because the render function used internally by the template rendering extension is exposed via the context, as the
`render` attribute, you can both call it to render templates for use other than immediate return to the user and
override it with a function of your own.

Performing this task is accomplished just like extending the namespace: create an extension that defines a `prepare`
callback, and assign a new `render` attribute.  The original `render` function (not bound to the context) is available
via the following import:

	from web.ext.template.render import render

"""

# Standard Library Imports
from weakref import proxy
from functools import partial

# Third-Party Imports
from marrow.util.compat import basestring
from marrow.util.bunch import Bunch

# Local Imports
from web.core.response import registry
from web.ext.template.handler import template_handler, annotated_template_handler
from web.ext.template import render


class TemplateExtension(object):
    uses = ['locale']
    provides = ['template']
    
    class Namespace(object):
        def __contains__(self, name):
            return hasattr(self, name)
        
        def __iter__(self):
            return ((i, getattr(self, i)) for i in dir(self) if i[0] != '_')
    
    def __init__(self, default=None, path=None, override=None):
        """Executed to configure the extension."""
        super(TemplateExtension, self).__init__()
        
        if default and not hasattr(render._render, default):
            raise ValueError('"{0}" is not a valid engine, perhaps you need to install an adapter?'.format(default))
        
        render._render.default = default
        render.render.path = path
        
        if override:
            override = dict(override)  # we want a copy as a plain dictionary
            
            # Ensure that all single values become one-element lists.
            # Greatly simplifies the per-request code.
            for key in override:
                value = override[key]
                if isinstance(value, basestring):
                    override[key] = [value]
        
        render.render.overrides = override
    
    def start(self, context):
        """Register the template response handler."""
        registry.register(template_handler, tuple)
        registry.register(annotated_template_handler, dict)
        context.namespace = self.Namespace
    
    def prepare(self, context):
        context.namespace = context.namespace()
        context.namespace.web = proxy(context)
        context.render = partial(render.render, context)
