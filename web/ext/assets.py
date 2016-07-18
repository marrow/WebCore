# encoding: utf-8

"""WebCore WebAssets integration."""

from __future__ import unicode_literals

from pkg_resources import resource_filename
from marrow.package.host import PluginManager

try:
	from webassets import Bundle
	from webassets.env import Environment, Resolver
	from webassets.loaders import YAMLLoader
	from webassets.filter import Filter, register_filter

except ImportError:
	raise ImportError('You must install the "webassets" package to use this extension.')

from web.core.compat import str, unicode


# Conditionally register additional WebAssets filters, if the packages are installed.

try:
	from dukpy.webassets import BabelJS
except ImportError:
	pass
else:
	register_filter(BabelJS)


try:
	from metapensiero.pj.api import _calc_file_names, translates
except ImportError:
	pass
else:
	@register_filter
	class JavaScripthon(Filter):
		name = 'javascripthon'
		
		_options = {}
		
		def __init__(self, stage3=False):
			"""To enable async features, set stage3 to True."""
			self.stage3 = stage3
		
		def unique(self):
			return (self.stage3, )
		
		def input(self, _in, out, source_path, output_path, **kw):
			src_text = _in.read()
			dst_filename, map_filename, src_relpath, map_relpath = _calc_file_names(source_path, output_path, None)
			
			js_text, src_map = translates(src_text, True, src_relpath, enable_es6=True,
					enable_stage3=self.stage3)
			
			out.write(js_text)


__all__ = ['Bundle', 'WebAssetsExtension']








def boolean(value, truthy=frozenset(('t', 'true', 'y', 'yes', 'on', '1'))):
	if not isinstance(value, (str, unicode)):
		return value
	
	return value.strip().lower() in truthy


def text(value):
	if isinstance(value, str):
		return value.decode('utf-8')
	
	return value


class PackageResolver(Resolver):
	def search_for_source(self, ctx, item):
		package, _, path = item.rpartition(':')
		
		if not package:
			return super(PackageResolver).search_for_source(ctx, item)
		
		return self.consider_single_directory(resource_filename(package, ''), path)
	
	def resolve_output_to_path(self, ctx, target, bundle):
		package, _, path = target.rpartition(':')
		
		if package:
			target = resource_filename(package, path)
		
		return super(PackageResolver, self).resolve_output_to_path(ctx, target, bundle)


class Environment(Environment):
	resolver_class = PackageResolver



class BundleRegistry(PluginManager):
	"""A registry of named bundles manually registered and registered via `web.asset` entry_point namespace.
	"""
	
	def __init__(self, ctx, env, prefix=None):
		self._ctx = ctx
		self._env = env
		self._prefix = prefix
		super(BundleRegistry, self).__init__('web.asset')
	
	def register(self, name, plugin):
		"""Strip prefix from the plugin name, if we're using prefixes."""
		
		plugin.env = self._env
		
		if not self._prefix:
			return super(BundleRegistry, self).register(name, plugin)
		
		if not name.startswith(self._prefix + '.'):
			return
		
		return super(BundleRegistry, self).register(name[len(self._prefix) + 1:], plugin)
	
	def __getattr__(self, name):
		"""Allow prefix namespaces to be constructed dynamically, and unambiguous suffixes to resolve.
		
		For example, a plugin registered as `jquery.cookie` would be accessible as just `context.asset.cookie`, or
		through the full namespace: `context.asset.jquery.cookie`.
		"""
		
		# First, handle exact matches.
		
		names = set(self)
		
		if name in names:
			return self[name]
		
		# Second, handle suffixes.
		for candidate in names:
			if candidate.endswith('.' + name):
				return self[candidate]
		
		# Last, handle prefixes. These will be used least.
		for candidate in names:
			if candidate.startswith(name + '.'):
				self.__dict__[name] = BundleRegistry(self._ctx, self._env, ((self._prefix + '.') if self._prefix else '') + name)
				return self.__dict__[name]



class WebAssetsExtension(object):
	def __init__(self, target, url='/', bundles=None, path=None, debug=not __debug__, live=__debug__, bust=None,
			scheme='hash', manifest=None, cache=True, age=31536000, **kw):
		"""Configure WebAssets.
		
		The first positional argument is a string path to a WebAssets yaml configuration file, or an iterable of
		`entry_point` names in the `web.asset` namespace, referencing bundle instances.
		
		Pass a path as `target` to have the combined files output there. If a bundle does not specify a `load_path`
		the bundle's paths will be relative to this value.
		
		The path given in `url` must be the root path the `target` directory will be served as.
		
		The `path` argument translates to the `load_path` argument to `Environment`, defaults to `None`, and may be
		an iterable of path prefixes to attempt when resolving asset paths.
		
		The `debug` argument may be:
		
		* `True` - Bundles will be merged and filters applied. (The defualt in production.)
		* `False` - Bundles will output individual source files. (The default in development.)
		* `"merge"` - Merge soruce files, but do not apply filters.
		
		If `live` is truthy (the default in development) then bundles will be automatically rebuilt. If falsy, bundles
		will need to be manually built, i.e. using the `web asset` command.
		
		Cache busting is controlled via the `bust` option, which is `None` by default and represents:
		
		* `None` - Add an expiry querystring if the bundle does not use a version placeholder.
		* `True` - Append the bundle version as a querystring argument.
		* `False` - Do not append querystring arguments.
		
		It is recommended to include `%(version)s` in your bundle output file names. Define a maximum caching time as
		`age`, and you can control the format of the version using the `scheme` argument, which may be:
		
		* `"timestamp"` - The modification time of the bundle.
		* `"hash"` - A hash of the bundle contents.  (The default.)
		* `False` or `None` - Version functionality is disabled.
		
		You may also pass a version implementation callback; ref the WebAssets documentation.
		
		When generating bundles, they may be served from a different machine, making version determination by the
		production application difficult or impossible. You may define a `manifest` as:
		
		* `"file:..."` - The path to a file on-disk to store pickled manifest information within.
		* `"json:..."` - The path to a file on-disk to store the JSON version of the manifest information within.
		* `False` or `None` - Disable manifest use.
		
		As with versioning, a custom manifest implementation may be passed in.
		
		Builds of complex heirarchices can be sped up if not every file needs to be reprocessed. You control caching
		behaviour using the `cache` argument:
		
		* `True` - Cache using a `cache` directory within the `target` directory.
		* `False` - Disable cache generation and use.
		* `"..."` - The explicit path to a cache directory.
		
		Additional keyword arguments are passed to the Environment constructor.
		"""
		
		if ':' in target:
			package, _, path = target.rpartition(':')
			target = resource_filename(package, path)
		
		kw['debug'] = debug
		kw['cache'] = cache
		kw['auto_build'] = live
		kw['manifest'] = manifest
		kw['url_expire'] = scheme
		kw['cache_max_age'] = age
		kw['load_path'] = path
		
		if isinstance(bundles, (str, unicode)):
			self._base = YAMLLoader(bundles).load_bundles()
		else:
			self._base = bundles
		
		self._bust = bust
		self._scheme = scheme
		
		self._environment = Environment(target, url, **kw)
	
	def start(self, context):
		context.bundle = BundleRegistry(context, self._environment)
	
	def prepare(self, context):
		base = set()
		
		if self._base:
			for i in self._base:
				if isinstance(i, (str, unicode)):
					base.add(context.bundle[i])
				else:
					base.add(i)

		context.asset = base  # Intent: context.asset.add(context.bundle.jquery)

