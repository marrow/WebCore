"""A log "prettifier" and JSON formatter for 'extra' data.

Adapts its defaults to execution context, such as use of Python's `-O` (`PYTHONOPTIMIZE`) "production" or `-X dev`
"development mode" by adjusting the verbosity of the output and default logging levels emitted. It also provides a more
verbose default format string which includes details like date and time, where Python's standard formatting does not.

By default, info-level and above are emitted. In "development mode" debug-level and above are enabled. When run with
optimizations, in "production mode", the default minimum level is warning and any JSON data is serialized compactly. Run
without, it is pretty-printed and emitted in an expanded form.

Will utilize `pygments` syntax highlighting if available and running interactively, without optimizations enabled.

Example logging "dictconfig":

```py
{
	'version': 1,
	'handlers': {
			'console': {
					'class': 'logging.StreamHandler',
					'formatter': 'json',
					'level': 'DEBUG' if __debug__ else 'INFO',
					'stream': 'ext://sys.stdout',
				}
		},
	'loggers': {
			'web': {
					'level': 'DEBUG' if __debug__ else 'WARN',
					'handlers': ['console'],
					'propagate': False,
				},
		},
	'root': {
			'level': 'INFO' if __debug__ else 'WARN',
			'handlers': ['console']
		},
	'formatters': {
			'json': {
					'()': 'web.core.pretty.PrettyFormatter',
				}
		},
}
```
"""

import datetime
import logging

from json import dumps
from os import environ
from sys import flags, stdin


_highlight = None

if __debug__ and (flags.dev_mode or stdin.isatty()):
	try:
		from pygments import highlight as _highlight
		from pygments.formatters import Terminal256Formatter
		from pygments.lexers.data import JsonLexer
		from pygments.lexers.python import PythonTracebackLexer
	except ImportError:
		pass


DEFAULT_PROPERTIES = logging.LogRecord('', '', '', '', '', '', '', '').__dict__.keys()


class PrettyFormatter(logging.Formatter):
	REPR_FAILED = 'REPR_FAILED'
	BASE_TYPES = (int, float, bool, bytes, str, list, dict)
	EXCLUDE = {  # TODO: Verify.
		'args', 'name', 'msg', 'levelname', 'levelno', 'pathname', 'filename',
		'module', 'exc_info', 'exc_text', 'lineno', 'funcName', 'created',
		'msecs', 'relativeCreated', 'thread', 'threadName', 'processName',
		'process', 'getMessage', 'message', 'asctime',
		'stack_info', 'SYM', 'C',
	}
	
	SYM = {
			'CRITICAL': '\033[30;48;5;196m \033[5m\U0001f514\033[25m\033[1;38;5;232m',
			'ERROR': '\033[30;48;5;208m \U0001f6ab\033[1;38;5;232m',
			'WARNING': '\033[30;48;5;220m \u26a0\ufe0f \033[1;38;5;232m',
			'INFO': '\033[30;48;5;39m \U0001f4ac\033[1;38;5;232m',
			'DEBUG': '\033[97;48;5;243m \U0001f4ad\033[1;38;5;255m',
			'TRACE': '\033[100m 👁‍🗨 \033[1;38;5;255m',
		}
	COLOURS = {
			'CRITICAL': '196',
			'ERROR': '208',
			'WARNING': '220',
			'INFO': '39',
			'DEBUG': '243',
			'TRACE': '0;90',
		}
	
	def __init__(self, highlight=None, indent=flags.dev_mode, **kwargs):
		if __debug__ and (flags.dev_mode or stdin.isatty()):
			format = "{SYM} {name} \033[0;38;5;{C};48;5;238m\ue0b0\033[38;5;255m {funcName} \033[30m\ue0b1\033[38;5;255m {lineno} \033[38;5;238;48;5;0m\ue0b0\033[m {message}"
		else:
			format = "{levelname}\t{name}::{funcName}:{lineno}\t{message}"
		
		super(PrettyFormatter, self).__init__(format, style='{')
		
		self.highlight = (__debug__ if highlight is None else highlight) and _highlight is not None
		self.indent = indent
	
	def _default(self, value):
		if hasattr(value, 'decode'):
			return value.decode('utf-8')
		
		if hasattr(value, 'as_json'):
			return value.as_json
		
		if hasattr(value, 'to_json'):
			return value.to_json()
		
		if hasattr(value, '__json__'):
			return value.__json__()
		
		try:
			return unicode(value)
		except:  # pylint:disable=bare-except
			try:
				return repr(value)
			except:  # pylint:disable=bare-except
				return self.REPR_FAILED
	
	def jsonify(self, record, **kw):
		extra = {}
		
		for attr, value in record.__dict__.items():
			if attr in self.EXCLUDE: continue
			extra[attr] = value
		
		if extra:
			try:
				return dumps(extra, skipkeys=True, sort_keys=True, default=self._default, **kw)
			except Exception as e:
				return dumps({'__error': repr(e)}, **kw)
		
		return ''
	
	def format(self, record):
		try:
			record.message = record.getMessage()
		except Exception as e:
			record.message = "Unable to retrieve log message: " + repr(e)
		
		record.SYM = self.SYM[record.levelname.upper()]
		record.C = self.COLOURS[record.levelname.upper()]
		parts = []
		
		try:
			parts.append(super(PrettyFormatter, self).formatMessage(record))
		except Exception as e:
			parts.append("Unable to format log message: " + repr(e))
		
		if record.exc_info:
			trace = self.formatException(record.exc_info)
			if __debug__ and (flags.dev_mode or stdin.isatty()):
				trace = _highlight(trace, PythonTracebackLexer(tabsize=4), Terminal256Formatter(style='monokai')).strip()
			parts.append(trace)
		
		if record.exc_text:
			parts.append(self.exc_text)
		
		if record.stack_info:
			parts.append(self.formatStack(record.stack_info))
		
		try:
			json = self.jsonify(
				record,
				separators = (', ' if not self.indent else ',', ': ') if __debug__ else (',', ':'),
				indent = "\t" if self.indent else None,
			)
			if flags.dev_mode or stdin.isatty():
				json = _highlight(json, JsonLexer(tabsize=4), Terminal256Formatter(style='monokai')).strip()
			json = "\n".join(json.split('\n')[1:-1])  # Strip off the leading and trailing lines.
			if json: parts.append(json)
		except Exception as e:
			parts.append("JSON serialization failed: " + repr(e))
		
		return "\n".join(i.strip() for i in parts)
