#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, absolute_import

import os
import pkg_resources

from marrow.script import script, describe
from marrow.script.util import wrap, partitionhelp

from web import release

__all__ = ['ScriptCore']

def discover():
    """List available templates."""
        
    msg = "Available commands:\n"
        
    # Load Python plugins.
    commands = dict((i.name, i.load()) for i in pkg_resources.iter_entry_points('web.command'))
        
    # Get the length of the longest plugin name.
    mlen = max(len(i) for i in commands)
        
    # Output one line per command: name, then the first line of documentation (if available).
    for name in sorted(commands):
        doc = partitionhelp(getattr(commands[name], '__doc__', 'No description available.'))[0][0]
        msg += " %-*s  %s" % (mlen, name, wrap(doc).replace("\n", "\n" + " " * (mlen + 3)))
        
    msg += "\nIf the last segment of the name is unambiguous you can omit the namespace."
    return msg   


class ScriptCore(object):
    """ ScriptCore: command line script for webcore
    web [--config|-c <config=local.yaml>] [--log|-l <file=STDERR>] [--log-level|-L <level=info>] [cmd] [<cmdopts>]
    """ + discover()
    
    _cmd_script = dict(
            title = "web",
            version = release.version,
            copyright = "Copyright 2011 Alice Bevan-McGregor"
        )
    
    @describe(verbose="Increase logging level to DEBUG.", quiet="Reduce logging level to WARN.")
    def __init__(self, verbose=False, quiet=False, config="local.yaml", log="STDERR", log_level="info"):
        pass
    
    def __getattr__(self, command):
        # Load Python plugins.
        available = dict()
        commands = dict([(i.name, i.load()) for i in pkg_resources.iter_entry_points('web.command')])
        for name in commands.keys():
            short = name.partition('.')[2]
            
            if short in commands:
                available[short] = False
                continue
            
            available[short] = commands[name]
        
        command = available.get(command, None)
        
        if command is None:
            print("Unknown command.  ", end='')
            return 1
        
        if command is False:
            print("Ambiguous command.  ", end='')
            return 2
        
        return command


def main():
    from marrow.script import execute
    execute(ScriptCore)


if __name__ == '__main__':
    main()
