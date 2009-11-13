#!/usr/bin/env python

import virtualenv, textwrap
output = virtualenv.create_bootstrap_script(textwrap.dedent("""

import os, subprocess

if sys.version_info <= (2, 5):
    raise SystemExit("Python 2.5 or later is required.")

development_packages = ['WebCore-Start']
production_packages = ['WebCore']

def filter_python_develop(line):
    if not line.strip():
        return Logger.DEBUG
    for prefix in ['Searching for', 'Reading ', 'Best match: ', 'Processing ',
                   'Moving ', 'Adding ', 'running ', 'writing ', 'Creating ',
                   'creating ', 'Copying ']:
        if line.startswith(prefix):
            return Logger.DEBUG
    return Logger.NOTIFY

def extend_parser(parser):
    parser.add_option(
            '--production',
            action = 'store_true',
            dest = 'production',
            default = False,
            help = "Omit development packages."
        )

def adjust_options(options, args):
    options.no_site_packages = True
    options.use_distribute = True

def after_install(options, home_dir):
    pip = join(home_dir, 'bin', 'pip')
    etc = join(home_dir, 'etc')
    src = join(home_dir, 'src')
    var = join(home_dir, 'var')
    tmp = join(home_dir, 'tmp')
    
    if not os.path.exists(etc): os.makedirs(etc)
    if not os.path.exists(src): os.makedirs(src)
    if not os.path.exists(var): os.makedirs(var)
    if not os.path.exists(tmp): os.makedirs(tmp)
    
    logger.indent += 2
    
    try:
        logger.notify('Installing WebCore into virtual environment...')
        subprocess.call(
                [pip, 'install'] + production_packages if options.production else development_packages,
                cwd = os.path.abspath(home_dir),
                filter_stdout = filter_python_develop,
                show_stdout = False
            )
    
    finally:
        logger.indent -= 2
    
    logger.notify('Run "cd %s ; . bin/activate" to enter the virtual environment.' % (os.path.relpath(home_dir, os.getcwd()), ))
    
    if not options.production:
        logger.notify('Run "paster quickstart" within the env to create a new web application.')
    

"""))
f = open('webcore-bootstrap.py', 'w').write(output)