# encoding: utf-8

"""An abstracted interface for content management classes and related support structure."""


from cmf.util import CounterMeta


__all__ = ['IComponent', 'IAction', 'IView']


class IComponent(object):
    """A high-level component comprised of a controller and at least one descendant of the Asset model.
    
    A component ties these two primary elements together; when an instance of the Asset descendant is loaded, the controller identified here is used to process front-end requests.
    """
    
    title = None
    summary = None
    description = None
    icon = None
    group = None
    
    version = None
    author = None
    email = None
    url = None
    copyright = None
    license = None
    
    requires = []
    
    model = None
    controller = None
    
    def __repr__(self):
        return "<%s %r>" % (self.__class__.__name__, self.title)
    
    @property
    def enabled(self):
        return False
    
    def authorize(self, child):
        """Allow or deny creation of a child class within this component."""
        return True
    
    def authorized(self, parent):
        """Allow or deny creation of this component within a specific parent."""
        return True
    
    def start(self):
        pass
    
    def stop(self):
        pass
    
    def setup(self):
        pass


class IAction(object):
    """An action supported by a given controller.
    
    Subclass this to customize security, etc."""
    
    __metaclass__ = CounterMeta
    
    title = None
    description = None
    icon = None
    
    def __init__(self, title=None, description=None, icon=None):
        if title: self.title = title
        if description: self.description = description
        if icon: self.icon = icon
    
    def authorized(self, asset):
        return True


class IView(object):
    """An view supported by a given controller.
    
    Subclass this to customize security, etc."""
    
    __metaclass__ = CounterMeta
    
    title = None
    description = None
    icon = None
    
    def __init__(self, title=None, description=None, icon=None):
        if title: self.title = title
        if description: self.description = description
        if icon: self.icon = icon
    
    def authorized(self, asset):
        return True
