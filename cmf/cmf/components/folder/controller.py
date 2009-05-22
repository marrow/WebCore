# encoding: utf-8

"""

Base asset controller.

"""

from tg                     import request, session, expose, flash, redirect, url
from pylons.i18n            import ugettext as _
from datetime               import datetime

from cmf.core               import View

from cmf.components.asset.controller import AssetController


log = __import__('logging').getLogger(__name__)
__all__ = ['FolderController']



class FolderController(AssetController):
    """TODO: Docstring incomplete."""
    
    pass