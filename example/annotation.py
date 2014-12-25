# encoding: utf-8

"""Basic class-based demonstration application.

Applications can be as simple or as complex and layered as your needs dictate.
"""


class Root(object):
	def __init__(self, context):
		self._ctx = context
	
	def mul(self, a: int = None, b: int = None) -> 'json':
		"""Multiply two values together and return the result via JSON.
		
		Python 3 function annotations are used to ensure that the arguments are integers. This requires the
		functionality of web.ext.cast:CastExtension.
		
		The return value annotation is handled by web.ext.template:TemplateExtension and may be the name of
		a serialization engine or template path.  (The trailing colon may be omitted for serialization when used
		this way.)
		
		There are several ways to execute this method:
		
		* POST http://localhost:8080/mul
		* GET http://localhost:8080/mul?a=27&b=42
		* GET http://localhost:8080/mul/27/42
		
		The latter relies on the fact we can't descend past a callable method so the remaining path elements are
		used as positional arguments, whereas the others rely on keyword argument assignment from a form-encoded
		request body or query string arguments.  (Security note: any data in the request body takes presidence over
		query string arguments!)
		
		If your editor has difficulty syntax highlighting this file, you may be interested in:
		
			https://github.com/davidbonnet/python.tmbundle
		"""
		
		if not a and not b:
			return dict(message="Pass arguments a and b to multiply them together!")
		
		return dict(answer=a * b)


if __name__ == '__main__':
	from web.core.application import Application
	from web.ext.template import TemplateExtension
	from web.ext.cast import CastExtension
	
	Application(Root, extensions=[TemplateExtension(), CastExtension()]).serve('waitress')
