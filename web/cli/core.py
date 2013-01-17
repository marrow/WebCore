#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function

import os
import sys
import select
import codecs
import pkg_resources

from marrow.script import describe
from marrow.script.core import ExitException
from marrow.config import Configuration

from web import release


__all__ = ['ScriptCore']


class ScriptCore(object):
    """Extensible command line script dispatcher for the WebCore web framework."""
    
    _cmd_script = dict(
            title = "web",
            version = release.version,
            copyright = "Copyright 2012 Alice Bevan-McGregor and contributors"
        )
    
    @describe(
            verbose="Increase logging level to DEBUG.",
            quiet="Reduce logging level to WARN.",
            config="The configuration file to use.",
            log="Where to send logging output; can use STDOUT and STDERR or the specifically named file.",
            log_level="The default logging level.\nSee marrow.logging documentation for valid values."
        )
    def __init__(self, verbose=False, quiet=False, config="local.yaml", log="STDERR", log_level="info"):
        self.verbose = verbose
        self.quiet = quiet
        self._config = config
        self._config_cache = None
        self.log = log
        self.log_level = log_level
        import logging
        logging.basicConfig(level=logging.DEBUG)
    
    @property
    def config(self):
        if not self._config_cache:
            if not sys.stdin.isatty() and select.select([sys.stdin],[],[],0.0)[0]:
                # We have configuration coming in over STDIN.
                self._config_cache = Configuration.load(sys.stdin)
            else:
                try:
                    self._config_cache = Configuration.load(codecs.open(self._config, 'r', 'utf8'))
                except FileNotFoundError:
                    raise ExitException(
                        "Configuration file not found: " + self._config +
                        "\n\nSpecify one using the --config (-c) global command-line argument."
                    )
        
        return self._config_cache
    
    # Load plugins.
    locals().update({
            i.name: i.load()
            for i in pkg_resources.iter_entry_points('web.command')
        })
    
    def __getattr__(self, name):
        if not name.endswith('.yaml'):
            raise AttributeError("'ScriptCore' object has no attribute '"+name+"'")
        
        self._config = name
        
        return getattr(self, self.config['exec'].command)


def main():
    from marrow.script import execute
    execute(ScriptCore)


if __name__ == '__main__':
    main()
