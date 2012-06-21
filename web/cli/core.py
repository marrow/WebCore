#!/usr/bin/env python
# encoding: utf-8

from __future__ import print_function, absolute_import

import os
import pkg_resources

from marrow.script import script, describe
from marrow.script.util import wrap, partitionhelp

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
        pass
    
    # Load plugins.
    locals().update({
            i.name: i.load()
            for i in pkg_resources.iter_entry_points('web.command')
        })


def main():
    from marrow.script import execute
    execute(ScriptCore)


if __name__ == '__main__':
    main()
