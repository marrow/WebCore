# encoding: utf-8

"""

"Guest Pass" authentication method.

Grant permission to view a protected asset using a simple single password.

"""

import logging

from cmf.hooks import authorize

log = logging.getLogger(__name__)
__all__ = ['BaseController']


class GuestPass(object):
    """"""
    
    @authorize()
    def validate(self, asset):
        value = asset.properties.get('cmf.authentication.guestpass', None)
        
        # If there is no Guest Pass defined (or if it has been nulled) we don't proceed.
        if value is None: return None
        
        if value not in session.get('cmf.authentication.guestpass', []):
            session['cmf.authentication.method'] = 'guestpass'
            # flash("warning::Requires Authentication::A guest pass is required to view this asset.")
            return False
        
        return True
