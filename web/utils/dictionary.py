# encoding: utf-8
# pragma: no cover

"""
A collection of specialized dictionary subclasses.
"""

import warnings

from marrow.util.bunch import Bunch as adict


__all__ = ['adict']


warnings.warn("Use of web.utils.dictionary.adict is deprecated, use marrow.util.bunch.Bunch instead.", DeprecationWarning)
