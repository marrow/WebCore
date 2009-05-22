# encoding: utf-8

import                      logging
from elixir                 import using_options, Field, String, BLOB

from cmf.components.asset.model import Asset


log = logging.getLogger(__name__)
__all__ = ['File']
__model__ = ['File']


class File(Asset):
    """TODO:Docstring incomplete."""
    
    using_options(tablename='files', inheritance='multi', polymorphic=True)
    
    @property
    def Controller(self):
        from cmf.components.file.controller import FileController
        return FileController
    
    content         = Field(BLOB(2^32-1), deferred=True)
    mime            = Field(String(100), default="application/octet-stream")
