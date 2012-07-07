# encoding: utf-8

import warnings
import web.core.locale

from web.core.locale import *
from web.core.middleware import defaultbool, middleware
from web.core.templating import registry


warnings.warn("The 'i18n' module has been renamed 'locale'.\nPlease update your import statements.", DeprecationWarning)


__all__ = web.core.locale.__all__


@middleware('locale', after="widgets")
def i18n(app, config):
    if not defaultbool(config.get('web.i18n', True), ['gettext']):
        return app

    from web.core.locale import LocaleMiddleware
    return LocaleMiddleware(app, config)

# Register the appropriate i18n functions in the global template scope.
registry.append(dict([('_', _), ('L_', L_), ('N_', N_)]))
