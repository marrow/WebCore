# encoding: utf-8

from __future__ import print_function

import os
import sys
import py_compile


def compile(cli, pretend=False):
    """Compile all Python files into bytecode."""
    
    count = 0
    
    for base, directories, files in os.walk('.'):
        if os.path.basename(base).startswith('.'):
            continue
        
        for name in filter(lambda path: os.path.splitext(path)[1] == '.py', files):
            path = os.path.abspath(os.path.join(base, name))
            
            if cli.verbose:
                print(path)
            
            if not pretend:
                py_compile.compile(path)
            
            count += 1
    
    if cli.verbose:
        print()
    
    if not pretend:
        print("Compiled {0} source files.".format(count), file=sys.stderr)
    else:
        print("Would have compiled {0} source files.".format(count), file=sys.stderr)
