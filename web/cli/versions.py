# encoding: utf-8

import pkg_resources


def versions(self):
    """Display versions of installed packages."""
    seen = dict()
    
    print("WebCore and dependencies:\n")
    for i in pkg_resources.require('WebCore'):
        if i in seen: continue
        seen[i] = None
        print(" * {0!r}".format(i))
    
    print("\nWebCore command line plugins:\n")
    for j in pkg_resources.iter_entry_points('web.command'):
        print(" * {0}: {1!r}".format(j.name, j.dist))
    
    print()
