# encoding: utf-8

from __future__ import print_function

import pkg_resources

from marrow.script import Parser
from marrow.script.util import wrap


def collect(self):
    """Collect static resources.
    
    Most applications serve static files from the development server, in production, however, you'll want a high-performance web server doing this.
    
    This command gathers static resources from your applciation and any other applications you have embedded and emits them with optional minification.
    """
    
    print("TBD")