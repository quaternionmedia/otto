class OttoException(Exception):
    """A Generic Otto exception"""

    pass


class EdlException(OttoException):
    """An Edl the engine cannot render.

    When one clip is the cause, the message names it by its index in the Edl
    and its name, e.g. `clip 2 ('title'): ...`.
    """

    pass


class EmptyClipsException(EdlException):
    """There were no clips found in the Edl."""

    pass


class DownloadException(EdlException):
    """A clip's remote media was refused, or could not be fetched."""

    pass
