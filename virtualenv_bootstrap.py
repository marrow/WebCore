#!/usr/bin/env python

import os, virtualenv, textwrap
output = virtualenv.create_bootstrap_script(textwrap.dedent("""

import os, subprocess

if sys.version_info <= (2, 5):
    raise SystemExit("Python 2.5 or later is required.")

development_packages = ['WebCore-Start']
production_packages = ['WebCore']

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
    pip = join(os.getcwd(), home_dir, 'bin', 'pip')
    etc = join(os.getcwd(), home_dir, 'etc')
    src = join(os.getcwd(), home_dir, 'src')
    var = join(os.getcwd(), home_dir, 'var')
    tmp = join(os.getcwd(), home_dir, 'tmp')
    
    if not os.path.exists(etc): os.makedirs(etc)
    if not os.path.exists(src): os.makedirs(src)
    if not os.path.exists(var): os.makedirs(var)
    if not os.path.exists(tmp): os.makedirs(tmp)
    
    logger.notify('Installing WebCore into virtual environment...')
    
    subprocess.call(
            [pip, 'install'] + (production_packages if options.production else development_packages)
        )
    
    logger.notify('Run "cd %s ; . bin/activate" to enter the virtual environment.' % (os.path.relpath(home_dir, os.getcwd()), ))
    
    if not options.production:
        logger.notify('Run "paster quickstart" within the env to create a new web application.')
    

"""))
f = open('webcore-bootstrap.py', 'w').write(output)
os.chmod('webcore-bootstrap.py', 0755)