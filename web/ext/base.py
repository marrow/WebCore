"""The base extension providing request, response, and core views."""

from collections import namedtuple
from collections.abc import Generator
from datetime import datetime
from io import IOBase
from logging import Logger, getLogger
from mimetypes import init, add_type, guess_type
from os.path import expandvars
from pathlib import Path, PurePosixPath
from re import compile as re
from time import mktime, gmtime
from xml.etree import ElementTree as ET
from xml.dom import minidom

from uri import URI
from webob import Request, Response

from ..core.util import Bread, Crumb, nop, safe_name
from ..core.typing import AccelRedirect, Any, ClassVar, Context, Response, Tags, Iterable, check_argument_types


HTML_LIKE = re(r"<!DOCTYPE html>|</?\s*[a-z-][^>]*\s*>|(\&(?:[\w\d]+|#\d+|#x[a-f\d]+);)")  # "Likely HTML" heuristic.


class BaseExtension:
	"""Base framework extension.
	
	This extension is not meant to be manually constructed or manipulated; use is automatic.
	"""
	
	first: ClassVar[bool] = True  # Must occur as early as possible in callback lists.
	always: ClassVar[bool] = True  # Always enabled.
	provides: ClassVar[Tags] = {'base', 'request', 'response'}  # Export these symbols for use as dependencies.
	uses: ClassVar[Tags] = {'timing.prefix', 'waf'}  # Ensure correct callback ordering for this sensitive core extension.
	
	_log: Logger = getLogger(__name__)
	
	sendfile: bool
	accel: AccelRedirect = None
	
	def __init__(self, sendfile:bool=False, accel:AccelRedirect=None):
		"""Initialize the WebCore web framework's underlying base extension.
		
		This accepts two arguments relating to the delivery of "open file handles" with resolvable names. Use of this
		functionality will impact the security context of file access, as the Python application's open file handle
		will go unused; the FELB will have to open the file itself, and so must have access.
		
		Due to these external restrictions, and potential information disclosure described below, these are not
		enabled by default.
		
		* `sendfile:bool=False`
		  
		  For any named open file handle processed via the `render_file` view, emit an `X-Sendfile` header containing
		  the resolved on-disk path to that file. When placed behind an appropriate front-end load balancer (FELB) the
		  front-end will deliver the file efficiently, permitting the application to process the next request more
		  rapidly. By default this is not emitted as without a FELB the header may contain sensitive or personally
		  identifying information.
		
		* `accel:AccelRedirect=None`
		  
		  A 2-tuple in the form `(base_path, base_uri)` where `base_path` may be a `str` or `Path` instance, and
		  `base_uri` may be a `str`, `PurePosixPath`, or `URI`. These represent the path prefix to remove from the
		  file handle's path, indicating the "document root" as visible to the FELB, and the base internal URI Nginx
		  will match to an `internal` server or location block, which will then resolve to that "document root".
		
		Both of these solutions obscure the true on-disk path to the file and do not permit direct access, only access
		via the application. This compares to utilization of an HTTP redirection to an externally-accessible location
		directive, which would be capture-able and bypass the application on subsequent requests.
		"""
		
		assert check_argument_types()
		
		self.sendfile = sendfile
		
		if accel is not None:  # Store normal forms and expand to absolute on-disk paths.
			self.accel = Path(expandvars(str(accel[0]))).expanduser().resolve(), URI(accel[1])
	
	def start(self, context:Context) -> None:
		"""Prepare the basic Application state upon web service startup.
		
		This registers core view handlers for most language-standard types that might be returned by an endpoint. It
		also ensures YAML has a registered mimetype.
		
		This adds a descriptor to the context for use during the request cycle:
		
		* `remainder`
		  Retrieve a `PurePosixPath` instance representing the remaining `request.path_info`.
		
		* `extra`
		  A dictionary of "extras" to include in logging statements. This dictionary forms the basis for the request-
		  local shallow copy.
		"""
		
		assert check_argument_types()
		if __debug__: self._log.debug("Registering core return value handlers.")
		
		# This prepares the mimetypes registry, and adds values typically missing from it.
		init()
		add_type('text/x-yaml', 'yml')
		add_type('text/x-yaml', 'yaml')
		
		# Register the core views supported by the base framework.
		register = context.view.register
		register(type(None), self.render_none)  # Special annotation case.
		register(Response, self.render_response)
		register(bytes, self.render_binary)
		register(str, self.render_text)
		register(IOBase, self.render_file)
		register(Generator, self.render_generator)
		register(ET.Element, self.render_element_tree_element)
		register(minidom.Document, self.render_minidom)
		
		# Track the remaining (unprocessed) path elements.
		context.remainder = property(lambda self: PurePosixPath(self.request.path_info))
		
		context.extra = {}
	
	def prepare(self, context:Context) -> None:
		"""Add the usual suspects to the context.
		
		This prepares the `web.base` WSGI environment variable (initial `SCRIPT_NAME` upon reaching the application)
		and adds the following to the `RequestContext`:
		
		* `id`
		  An identifier for this request. Based on the MongoDB "ObjectID" structure, using the hardware MAC address as
		  the "machine identifier".
		
		* `request`
		  A `webob.Request` instance encompassing the active WSGI request.
		
		* `response`
		  A `webob.Response` object prepared from the initial request, to be populated for delivery to the client.
		
		* `path`
		  An instance of `Bread`, a type of `list` which permits access to the final element by the attribute name
		  `current`. This represents the steps of dispatch processing from initial request through to final endpoint.
		
		* `extra`
		  A dictionary of "extras" to include in logging statements. Contributions or modifications made within the
		  request processing life cycle are limited to that request.
		"""
		
		assert check_argument_types()
		
		context.extra['req'] = str(context.id)
		if __debug__: self._log.debug("Preparing request context.", extra=context.extra)
		
		# Bridge in WebOb `Request` and `Response` objects.
		# Extensions shouldn't rely on these, using `environ` where possible instead; principle of least abstraction.
		req = context.request = request = Request(context.environ)
		context.response = Response(request=request)
		context.response.content_type = None
		
		# This naturally elides extraneous leading and trailing slashes.
		req.remainder = context.request.path_info.strip('/').split('/')
		
		# Record the initial path representing the point where a front-end web server bridged to us.
		context.environ['web.base'] = request.script_name
		
		# Track the "breadcrumb list" of dispatch through distinct controllers.
		context.path = Bread()
	
	def dispatch(self, context:Context, crumb:Crumb) -> None:
		"""Called as dispatch descends into a tier.
		
		The base extension uses this to maintain the "current path" and ensure path elements are migrated from the
		WSGI `PATH_INFO` into `SCRIPT_NAME` as appropriate.
		"""
		
		assert check_argument_types()
		request = context.request
		
		if __debug__:
			extras = context.extra.copy()
			extras.update(crumb.as_dict)
			for k in ('handler', 'origin'): extras[k] = safe_name(extras[k]) # Sanitize a value to make log-safe.
			self._log.trace("Handling dispatch event.", extra=extras)  # Emit.
		
		consumed = ('', ) if not crumb.path or request.path_info_peek() == '' else crumb.path.parts
		
		nConsumed = 0  # The number of 
		if consumed:  # Migrate path elements consumed from the `PATH_INFO` to `SCRIPT_NAME` WSGI environment variables.
			for element in consumed:
				if element == request.path_info_peek():  # WebOb itself skips repeated separators.
					request.path_info_pop()  # But *will* shift them into SCRIPT_NAME for us, too, if present.
					nConsumed += 1
				else:  # The dispatcher has deviated. We abandon hope.
					break
		
		# Update the breadcrumb list.
		context.path.append(crumb)
		
		# Lastly, update the remaining path element list.
		request.remainder = request.remainder[nConsumed:]  # If nothing consumed, shallow copy.
	
	def render_none(self, context:Context, result:None) -> bool:
		"""Render empty responses.
		
		Applies a zero-length binary body to the response.
		"""
		
		assert check_argument_types()
		if __debug__: self._log.trace("Applying literal None value as empty response.", extra=context.extra)
		
		if not context.response.content_type: context.response.content_type = 'text/plain'
		context.response.body = b''
		del context.response.content_length
		
		return True
	
	def render_response(self, context:Context, result:Response) -> bool:
		"""Allow direct returning of WebOb `Response` instances.
		
		Replaces the `response` attribute of the context with a new `Response` instance.
		"""
		
		assert check_argument_types()
		if __debug__: self._log.trace(f"Replacing context.response object with: {result!r}", extra=context.extra)
		
		context.response = result
		
		return True
	
	def render_binary(self, context:Context, result:bytes) -> bool:
		"""Return binary responses unmodified.
		
		Assign a single-element iterable containing the binary value as the WSGI body value in the response.
		"""
		
		assert check_argument_types()
		if __debug__: self._log.trace(f"Applying {len(result)}-byte binary value.", extra=context.extra)
		
		context.response.app_iter = iter((result, ))  # This wraps the binary string in a WSGI body iterable.
		
		return True
	
	def render_text(self, context:Context, result:str) -> bool:
		"""Return textual responses, encoding as needed.
		
		Assign Unicode text to the response.
		"""
		
		assert check_argument_types()
		if __debug__: self._log.trace(f"Applying {len(result)}-character text value.", extra=context.extra)
		
		resp = context.response
		context.response.text = result
		if not resp.content_type: resp.content_type = 'text/html' if HTML_LIKE.search(result) else 'text/plain'
		
		return True
	
	def render_file(self, context:Context, result:IOBase) -> bool:
		"""Extract applicable metadata from returned open file handles, and deliver the file content to the client.
		
		If configured to do so, this will cause additional headers to be emitted to instruct a front-end load balancer
		(FELB) to deliver the on-disk data more directly.
		"""
		# TODO: https://pythonhosted.org/xsendfile/howto.html#using-nginx-as-front-end-server
		
		assert check_argument_types()
		
		anonymous: bool = not getattr(result, 'name', '')
		path: Optional[Path] = None if anonymous else Path(result.name).expanduser().resolve()
		response: Response = context.response
		
		result.seek(0, 2)  # Seek to the end of the file.
		response.content_length = result.tell()  # Report file length.
		result.seek(0)  # Seek back to the start of the file.
		
		if __debug__:
			self._log.trace(f"Applying a {response.content_length}-byte file-like object: {result!r}", extra={
					'path': '<anonymous>' if anonymous else str(path),
					**context.extra
				})
		
		if not anonymous:  # We can retrieve information like modification times, and likely mimetype.
			response.conditional_response = True
			
			modified = mktime(gmtime(path.stat().st_mtime))
			response.last_modified = datetime.fromtimestamp(modified)
			response.etag = str(modified)
			
			if not response.content_type:
				ct, ce = guess_type(result.name)
				if not ct: ct = 'application/octet-stream'  # Ultimate fallback for unknown binary data.
				response.content_type, response.content_encoding = ct, ce
			
			if self.sendfile:
				response.headers['X-Sendfile'] = str(path)
			
			if self.accel:
				prefix, root = self.accel
				if str(path).startswith(str(prefix)):
					response.headers['X-Accel-Redirect'] = str(root / path.relative_to(prefix))
		
		elif not response.content_type:
			response.content_type = 'application/octet-stream'
		
		response.body_file = result
		
		return True
	
	def render_generator(self, context:Context, result:Generator) -> bool:
		"""Attempt to serve generator responses through stream encoding while protecting against None values.
		
		This allows for direct use of cinje template functions, which are generators, as returned views.
		"""
		
		assert check_argument_types()
		if __debug__: self._log.trace(f"Applying an unknown-length generator: {result!r}", extra=context.extra)
		
		if not context.response.content_type:
			log.warn("Populate context.response.content_type when utilizing generator responses; assuming HTML.")
			response.content_type = 'text/html'
		
		context.response.encoding = 'utf-8'
		context.response.app_iter = (
				(i.encode('utf-8') if isinstance(i, bytes) else str(i))  # Stream encode Unicode chunks.
				for i in result if i is not None  # Skip None values.
			)
		
		return True
	
	def render_element_tree_element(self, context:Context, result:ET.Element) -> bool:
		"""Render an ElementTree Element into the response.
		
		Automatically utilizes the pending response's `charset`, defaulting to UTF-8. The response mimetype defaults
		to `application/xml` if left unspecified, using a `utf-8` encoding. However, this view detects the rendering
		path to use based on the second component of the type, which must resolve to `xml` or `html`.
		"""
		
		assert check_argument_types()
		if __debug__: self._log.trace(f"Applying an ElementTree object: {result!r}", extra=context.extra)
		
		if not (ct := context.response.content_type):
			ct = context.response.content_type = 'application/xml'
			context.response.charset = 'utf-8'
		
		method = ct.partition('/')[1].partition('+')[0]  # text/html, text/xml, application/xml, text/xml+rss, ...
		assert method in ('xml', 'html')  # The second MIME type component must always resolve to 'xml' or 'html'.
		
		context.response.body = ET.tostring(
				result,
				encoding = context.response.charset,
				method = method,
				xml_declaration = (method == 'xml')
			)
		
		return True
	
	def render_minidom(self, context:Context, result:minidom.Document) -> bool:
		"""Render a 'minidom' Document into the response.
		
		Automatically utilizes the pending response's `charset`, defaulting to UTF-8.
		"""
		
		assert check_argument_types()
		if __debug__: self._log.trace(f"Applying a MiniDOM object: {result!r}", extra=context.extra)
		
		if not context.response.content_type:
			context.response.content_type = 'text/xml' if __debug__ else 'application/xml'
			context.response.charset = 'utf-8'
		
		context.response.body = (result.toprettyxml if __debug__ else result.toxml)(encoding=context.response.charset)
		
		return True
