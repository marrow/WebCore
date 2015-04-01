# Method naming conventions

* Classes must:
	* Have valid, and useful, `__repr__` and `__str__` methods.
	* Optionally, for web-accessible resources, providing a `__url__` method is nice.
* Conversion routines.
	* `to_` and `from_` methods are encouraged for XML, as that is the backup/archive format.
	* `as_` methods must be `@property` decorated, `json` is generally recommended, `text` where content extraction is possible, and `html` where rendering to the web is a possiblity.
