# encoding: utf-8
#
# WebCore documentation build configuration file.
#
# This file is execfile()d with the current directory set to its containing dir.

import sys, os
from web import release

# sys.path.append(os.path.abspath('../'))

# -- General configuration -----------------------------------------------------

extensions = [
        'sphinx.ext.autodoc',
        #'sphinx.ext.autosummary',
        #'sphinx.ext.coverage',
        #'sphinx.ext.doctest',
        'sphinx.ext.intersphinx',
        'sphinx.ext.todo'
    ]

templates_path = ['tools/templates']

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = release.name
copyright = release.copyright
version = release.version
release = release.release

# List of documents that shouldn't be included in the build.
unused_docs = [
    ]

# List of directories, relative to source directory, that shouldn't be searched for source files.
exclude_trees = [
        'tools/sphinx'
    ]

# If true, '()' will be appended to :func: etc. cross-reference text.
add_function_parentheses = True

# If true, the current module name will be prepended to all description unit titles (such as .. function::).
add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the output. They are ignored by default.
show_authors = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# -- Options for HTML output ---------------------------------------------------

html_theme = 'default'
html_theme_options = {}
html_theme_path = ['tools/themes']

# The name for this set of Sphinx documents.  If None, it defaults to
# "<project> v<release> documentation".
html_title = "WebCore %s Documentation" % (version, )

# The name of an image file (relative to this directory) to place at the top
# of the sidebar.
#html_logo = None

# The name of an image file (within the static path) to use as favicon of the
# docs.  This file should be a Windows icon file (.ico) being 16x16 or 32x32
# pixels large.
#html_favicon = ['tools/static/Radio-32.png']

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['tools/static']

# If not '', a 'Last updated on:' timestamp is inserted at every page bottom,
# using the given strftime format.
#html_last_updated_fmt = '%b %d, %Y'

# If true, SmartyPants will be used to convert quotes and dashes to
# typographically correct entities.
html_use_smartypants = True

# Custom sidebar templates, maps document names to template names.
html_sidebars = {}

# Additional templates that should be rendered to pages, maps page names to template names.
html_additional_pages = {}

# If false, no module index is generated.
html_use_modindex = True

# If false, no index is generated.
html_use_index = True

# If true, the index is split into individual pages for each letter.
html_split_index = False

# If true, links to the reST sources are added to the pages.
#html_show_sourcelink = True

# If true, an OpenSearch description file will be output, and all pages will
# contain a <link> tag referring to it.  The value of this option must be the
# base URL from which the finished HTML is served.
#html_use_opensearch = ''

# If nonempty, this is the file name suffix for HTML files (e.g. ".xhtml").
#html_file_suffix = ''

# Output file base name for HTML help builder.
htmlhelp_basename = 'WebCore-Doc'


# -- Options for LaTeX output --------------------------------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
latex_font_size = '10pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, documentclass [howto/manual]).
latex_documents = [
  ('index', 'WebCore.tex', u'WebCore Documentation', u'Alice Bevan-McGregor', 'manual'),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
#latex_logo = None

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
latex_use_parts = True

# Additional stuff for the LaTeX preamble.
#latex_preamble = ''

# Documents to append as an appendix to all manuals.
#latex_appendices = []

# If false, no module index is generated.
#latex_use_modindex = True


intersphinx_mapping = {'http://docs.python.org/dev': None,
                       'http://www.sqlalchemy.org/docs/05/':None,
                       'http://sprox.org/': None,
                       'http://toscawidgets.org/documentation/tw.forms/':None,
                       'http://toscawidgets.org/documentation/ToscaWidgets/':None,
                       }
