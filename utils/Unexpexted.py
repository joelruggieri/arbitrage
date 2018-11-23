from pymonad.Maybe import _Nothing
from pymonad.Maybe import Maybe


class _Unexpexted(_Nothing):
    def __init__(self, value=None):
        super(Maybe, self).__init__(value)


Unexpexted = _Unexpexted()