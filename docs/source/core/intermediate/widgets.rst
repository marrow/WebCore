***************************
Widgets and Form Generation
***************************

.. contents:: Table of Contents
   :depth: 2
   :local:



WebCore has support for ToscaWidgets middleware.  To enable this, add the following to your
configuration:

.. code-block:: ini

    web.widgets = toscawidgets
    web.widgets.prefix = /_tw
    web.widgets.inject = True
    web.widgets.serve = True

Note, however, that this support has been deprecated.  Use of a less invasive widget and
form generation system is recommended.  
`ToscaWidgets2 <http://toscawidgets.org/documentation/tw2.core/>`_ and 
`marrow.tags <https://github.com/marrow/marrow.tags>`_ are both viable alternatives that
require little to no support from the host framework..
