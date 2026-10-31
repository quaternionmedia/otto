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


class NoSoundException(EdlException):
    """Nothing in the Edl makes a sound, so `renderSound` has nothing to write:
    it has no video or audio clip, or no audio clip and no video clip with
    sound where it plays."""

    pass


class FFmpegException(OttoException):
    """ffmpeg ran, and did not write what otto asked it for.

    `stderr` is everything ffmpeg said; the message ends with the last of it.
    """

    def __init__(self, message, stderr=''):
        super().__init__(message)
        self.stderr = stderr
