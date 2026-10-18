class OttoException(Exception):
    """A Generic Otto exception"""

    pass


class EdlException(OttoException):
    """An Edl the engine cannot render.

    When one clip is the cause, the message names it by its place in the Edl,
    counted from 1, and its name: `clip 2 ('title'): ...` is the second clip.
    """

    pass


class EmptyClipsException(EdlException):
    """There were no clips found in the Edl."""

    pass


class DownloadException(EdlException):
    """A clip's remote media was refused, or could not be fetched."""

    pass
