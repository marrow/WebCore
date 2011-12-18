# encoding: utf-8

import warnings

import web.core.locale
from web.core.locale import *


warnings.warn("The 'i18n' module has been renamed 'locale'.\nPlease udpate your import statements.", DeprecationWarning)


__all__ = web.core.locale.__all__
