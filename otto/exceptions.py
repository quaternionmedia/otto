class OttoException(Exception):
    """A Generic Otto exception"""

    pass


class EdlException(OttoException):
    """A generic Edl exception"""

    pass


class EmptyClipsException(EdlException):
    """There were no clips found in the Edl."""

    pass
