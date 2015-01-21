# encoding: utf-8

from __future__ import print_function


def prepare(app):
    """Prepare the shell environment"""
    extensions = [ext.interactive() for ext in app.extensions if hasattr(ext, 'interactive')]
    return dict().update(*extensions)


def run_python(env):
    import code
    code.interact(local=env)


def run_ipython(env):
    """Runs the shell environment through ipython using `env` as local variables"""
    try:
        from IPython import embed
        embed()
    except ImportError:
        try:
            from IPython.Shell import IPShellEmbed
            shell = IPShellEmbed()
            shell(local_ns=env)
        except ImportError:
            raise ValueError('Unable to find ipython. To install, run: pip install ipython')


def run_bpython(env):
    """Runs the shell environment through bpython using `env` as local variables"""
    try:
        import bpython
        bpython.embed(locals_=env)
    except ImportError:
        raise ValueError('Unable to find bpython. To install, run: pip install bpython')


def shell(self, interactive=True, run='auto'):
    """Run the shell within the WebCore environment."""
    #env = prepare(self.config.application)
    env = dict()
    interpreters = ['bpython', 'ipython', 'python']
    interpreter = None

    if run != 'auto':
        if run not in interpreters or ('run_' + run) not in globals():
            raise ValueError('Unknown interpreter {0}, use one of: {1}'.format(run, ', '.join(interpreters)))
        interpreters = [run]

    for shell in interpreters:
        try:
            interpreter = globals()['run_' + shell]
        except KeyError:
            pass
        else:
            # An interpreter not being found isn't an error when scanning.
            # But is an error if explicitly asking for that shell.
            try:
                interpreter(env)
            except ValueError:
                pass
            else:
                break
