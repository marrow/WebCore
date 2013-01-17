# encoding: utf-8

from __future__ import unicode_literals, print_function

from marrow.script import describe


@describe(reload="Monitor modules for changes and automatically restart.")
def serve(cli, reload=False):
    """Serve your web application."""
    
    config = cli.config
    
    application = config.application
    service = config.server(application)
    service.start()
