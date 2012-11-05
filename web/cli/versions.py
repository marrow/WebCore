# encoding: utf-8

from __future__ import print_function

import pkg_resources

from marrow.script import Parser
from marrow.script.util import wrap


def explore(namespace, short):
    for i in pkg_resources.iter_entry_points(namespace):
        if not short:
            print(" * \"{0}\" provided by {1} {2} from:".format(i.name, i.dist.project_name, i.dist.version))
            print("   ", "   ".join(wrap(i.dist.location, Parser.width() - 3).split("\n")), sep='', end="\n\n")
        else:
            print("{0} ({1} {2})".format(i.name, i.dist.project_name, i.dist.version))


def dependencies(package, short):
    seen = dict()
    for i in pkg_resources.require(package):
        if i in seen: continue
        seen[i] = None
        
        if not short:
            print(" * {0} {1} from:".format(i.project_name, i.version))
            print("   ", "   ".join(wrap(i.location, Parser.width() - 3).split("\n")), sep='', end="\n\n")
        else:
            print("{0} {1}".format(i.project_name, i.version))


def all_packages(short):
    seen = dict()
    for i in pkg_resources.working_set:
        if i in seen: continue
        seen[i] = None
        
        if not short:
            print(" * {0} {1} from:".format(i.project_name, i.version))
            print("   ", "   ".join(wrap(i.location, Parser.width() - 3).split("\n")), sep='', end="\n\n")
        else:
            print("{0} {1}".format(i.project_name, i.version))


def all_namespaces():
    counts = dict()
    
    for i in pkg_resources.working_set:
        plugins = pkg_resources.get_entry_map(i)
        for k in plugins:
            counts.setdefault(k, 0)
            counts[k] += len(plugins[k])
    
    for k in sorted(counts):
        print(" * {0} ({1} plugins)".format(k, counts[k]))


def versions(self, all=False, package='WebCore', namespace=None, namespaces=False, short=False):
    """Display versions of installed packages.
    
    Use the namespace argument to enumerate all plugins for the given namespace.  Examples include: console_scripts, web.command, web.db.engines, web.dispatch, marrow.templating, ...
    
    Example calls:
    
    web versions --all
    # dump all installed packages
    
    web versions --package mako
    # dump requirements for specific package
    
    web versions --namespaces
    # show available plugin namespaces
    
    web versions --namespace marrow.templating
    # show all plugins for this namespace
    
    web versions --short
    # one line per requirement, no paths or formatting
    """
    
    # TODO: Determine if versions are latest, and if safe upgrading is possible.
    
    if namespace:
        print("Plugins within the \"{0}\" namespace:\n".format(namespace))
        return explore(namespace, short)
    
    if all:
        print("All installed Python packages:\n")
        return all_packages(short)
    
    if namespaces:
        print("Plugin namespaces:\n")
        return all_namespaces()
    
    print(package, "and dependencies:\n")
    return dependencies(package, short)
