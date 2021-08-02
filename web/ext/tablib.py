"""The base extension providing request, response, and core views."""

from logging import getLogger

from tablib import Dataset, UnsupportedFormat
from tablib.formats import registry as _formatters

from ..core.typing import AccelRedirect, Any, ClassVar, Context, Response, Tags, Iterable, check_argument_types


MAPPING = {
		'text/csv': 'csv',
		'text/tsv': 'tsv',
		'text/html': 'html',
		'text/json': 'json',
		'application/json': 'json',
		'application/x-tex': 'latex',
		'application/vnd.oasis.opendocument.spreadsheet': 'ods',
		'text/x-rst': 'rst',
		'application/vnd.ms-excel': 'xls',
		'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
		'text/x-yaml': 'yaml',
		'text/yaml': 'yaml',
		'application/yaml': 'yaml',
	}


class TablibExtension:
	"""Extension to register views capable of handling content negotiation for tablib datasets."""
	
	provides: ClassVar[Tags] = {'tablib'}  # Export these symbols for use as dependencies.
	
	_log: Logger = getLogger(__name__)
	
	def __init__(self):
		assert check_argument_types()
	
	def start(self, context:Context) -> None:
		assert check_argument_types()
		if __debug__: self._log.debug("Registering Tablib return value handlers.")
		
		context.view.register(Dataset, self.render)
	
	def render(self, context:Context, result:Dataset) -> bool:
		assert check_argument_types()
		if __debug__: self._log.trace("Negotiating tablib.Dataset retrieval.", extra=context.extra)
		
		mime = context.request.best_match(MAPPING.keys())
		
		context.response.content_type = mime
		
		try:
			context.response.body = result.export(MAPPING[mime])
		except UnsupportedFormat as e:
			context.response = HTTPNotAcceptable("Must be one of: " + ", ".join(sorted(MAPPING.keys())))
		
		return True
