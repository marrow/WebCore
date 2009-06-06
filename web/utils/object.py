# encoding: utf-8

"""

"""


__all__ = ['yield_property', 'isgenerator', 'CounterMeta', 'DottedFileNameFinder', 'get_dotted_object']



def yield_property(iterable, name):
    for i in iterable: yield getattr(i, name, None)


def isgenerator(func):
    try:
        return hasattr(func, '__iter__') or ( func.func_code.co_flags & CO_GENERATOR != 0 )
    
    except AttributeError:
        return False


class CounterMeta(type):
    """
    
    
    A simple meta class which adds a ``_counter`` attribute to the instances of
    the classes it is used on. This counter is simply incremented for each new
    instance.
    """
    
    counter = 0
    
    def __call__(self, *args, **kwargs):
        instance = type.__call__(self, *args, **kwargs)
        instance._counter = CounterMeta.counter
        CounterMeta.counter += 1
        return instance


class DottedFileNameFinder(object):
    """this class implements a cache system above the
    get_dotted_filename function and is designed to be stuffed
    inside the app_globals.

    It exposes a method named get_dotted_filename with the exact
    same signature as the function of the same name in this module.

    The reason is that is uses this function itself and just adds
    caching mechanism on top.
    """
    def __init__(self):
        self.__cache = dict()

    def get_dotted_filename(self, template_name, template_extension='.html'):
        """this helper function is designed to search a template or any other
        file by python module name.

        Given a string containing the file/template name passed to the @expose
        decorator we will return a resource useable as a filename even
        if the file is in fact inside a zipped egg.

        The actual implementation is a revamp of the Genshi buffet support
        plugin, but could be used with any kind a file inside a python package.

        @param template_name: the string representation of the template name
        as it has been given by the user on his @expose decorator.
        Basically this will be a string in the form of:
        "genshi:myapp.templates.somename"
        @type template_name: string

        @param template_extension: the extension we excpect the template to have,
        this MUST be the full extension as returned by the os.path.splitext
        function. This means it should contain the dot. ie: '.html'

        This argument is optional and the default value if nothing is provided will
        be '.html'
        @type template_extension: string
        """
        try:
            return self.__cache[template_name]

        except KeyError:
            # the template name was not found in our cache
            divider = template_name.rfind('.')
            if divider >= 0:
                package = template_name[:divider]
                basename = template_name[divider + 1:] + template_extension
                result = resource_filename(package, basename)

            else:
                result = template_name

            self.__cache[template_name] = result

            return result

def get_dotted_object(target):
    """This helper function loads an object identified by a dotted-notation string.
    
    For example:
    
        # Load class Foo from example.objects
        get_dotted_object('example.objects:Foo')
    """
    parts, target = target.split(':') if ':' in target else (target, None)
    module = __import__(parts)
    
    for part in parts.split('.')[1:] + [target]:
        module = getattr(module, part)
    
    return module
        