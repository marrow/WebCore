import os
import sys

import paste.fixture
import paste.registry
import paste.deploy.config
from paste.deploy import loadapp, appconfig
from paste.script.command import Command, BadCommand


__all__ = ['ShellCommand']


def can_import(name):
    """Attempt to __import__ the specified package/module, returning
    True when succeeding, otherwise False"""
    try:
        __import__(name)
        return True
    except ImportError:
        return False




class ShellCommand(Command):
    """Open an interactive shell with the web app loaded.

    The optional CONFIG_FILE argument specifies the config file to use for the interactive shell. CONFIG_FILE defaults to 'development.ini'.

    This allows you to test your models and simulate web requests using ``paste.fixture``.

    Example::

        $ paster shell my-development.ini

    """
    summary = __doc__.splitlines()[0]
    usage = '\n' + __doc__

    min_args = 0
    max_args = 2
    group_name = 'webcore'

    parser = Command.standard_parser(simulate=True)
    parser.add_option('-d', '--disable-ipython', action='store_true', dest='disable_ipython', help="Don't use IPython if it is available")
    parser.add_option('-q', action='count', dest='quiet', default=0, help="Do not load logging configuration from the config file")

    def command(self):
        """Main command to create a new shell"""
        self.verbose = 3
        if len(self.args) == 0:
            # Assume the .ini file is ./development.ini
            config_file = 'development.ini'
            if not os.path.isfile(config_file):
                raise BadCommand('%sError: CONFIG_FILE not found at: .%s%s\n'
                                 'Please specify a CONFIG_FILE' % \
                                 (self.parser.get_usage(), os.path.sep,
                                  config_file))
        else:
            config_file = self.args[0]

        config_name = 'config:%s' % config_file
        here_dir = os.getcwd()

        if not self.options.quiet:
            # Configure logging from the config file
            self.logging_file_config(config_file)
        
        conf = appconfig(config_name, relative_to=here_dir)
        conf.update(dict(app_conf=conf.local_conf, global_conf=conf.global_conf))
        paste.deploy.config.CONFIG.push_thread_config(conf)
        
        # Load locals and populate with objects for use in shell
        sys.path.insert(0, here_dir)
        
        # Load the wsgi app first so that everything is initialized right
        wsgiapp = loadapp(config_name, relative_to=here_dir)
        test_app = paste.fixture.TestApp(wsgiapp)
        
        # Query the test app to setup the environment
        tresponse = test_app.get('/_test_vars')
        request_id = int(tresponse.body)
        
        # Disable restoration during test_app requests
        test_app.pre_request_hook = lambda self: paste.registry.restorer.restoration_end()
        test_app.post_request_hook = lambda self: paste.registry.restorer.restoration_begin(request_id)
        
        paste.registry.restorer.restoration_begin(request_id)
        
        locs = dict(__name__="webcore-admin", application=wsgiapp, test=test_app)
        
        exec 'import web' in locs
        exec 'from web.core import http, Controller, request, response, cache, session' in locs
        
        if len(self.args) == 2:
            execfile(self.args[1], {}, locs)
            return
        
        banner = "Welcome to the WebCore shell."
        
        try:
            if self.options.disable_ipython:
                raise ImportError()

            # try to use IPython if possible
            from IPython.Shell import IPShellEmbed

            shell = IPShellEmbed(argv=self.args)
            shell.set_banner(shell.IP.BANNER + '\n\n' + banner)
            try:
                shell(local_ns=locs, global_ns={})
            finally:
                paste.registry.restorer.restoration_end()
        
        except ImportError:
            import code
            py_prefix = sys.platform.startswith('java') and 'J' or 'P'
            newbanner = "WebCore Interactive Shell\n%sython %s\n\n" % (py_prefix, sys.version)
            banner = newbanner + banner
            shell = code.InteractiveConsole(locals=locs)
            try:
                import readline
            except ImportError:
                pass
            try:
                shell.interact(banner)
            finally:
                paste.registry.restorer.restoration_end()
