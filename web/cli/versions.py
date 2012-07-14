# encoding: utf-8

from __future__ import print_function

import pkg_resources

from marrow.script import Parser
from marrow.script.util import wrap


def versions(self, namespace=None):
    """Display versions of installed packages.
    
    Use the namespace argument to enumerate all plugins for the given namespace.  Examples include: console_scripts, web.command, web.db.engines, web.dispatch, marrow.templating, ...
    """
    
    def explore(namespace):
        for i in pkg_resources.iter_entry_points(namespace):
            print(" * \"{0}\" provided by {1} {2} from:".format(i.name, i.dist.project_name, i.dist.version))
            print("  ", i.dist.location, end="\n\n")
    
    if namespace:
        print("Plugins within the \"{0}\" namespace:\n".format(namespace))
        return explore(namespace)
    
    print("WebCore and dependencies:\n")
    
    seen = dict()
    for i in pkg_resources.require('WebCore'):
        if i in seen: continue
        seen[i] = None
        
        print(" * {0} {1} from:".format(i.project_name, i.version))
        print("   ", "   ".join(wrap(i.location, Parser.width() - 3).split("\n")), sep='', end="\n\n")
