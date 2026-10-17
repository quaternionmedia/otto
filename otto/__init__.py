import warnings

from ._version import __version__

__all__ = ['__version__']


def _restore_pillow_antialias():
    """Give Pillow back the `Image.ANTIALIAS` that moviepy 1.0.3 resizes with.

    Pillow 10 removed the name -- it was always LANCZOS -- so on Pillow 10 and
    later every resize moviepy 1.0.3 does raises AttributeError: `Clip.resize`,
    and the templates that scale their text. Pillow 9 still has the name,
    behind a DeprecationWarning, and is left exactly as it is.
    """
    try:
        from PIL import Image
    except ImportError:
        return
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', DeprecationWarning)
        if hasattr(Image, 'ANTIALIAS'):
            return
    Image.ANTIALIAS = Image.LANCZOS


_restore_pillow_antialias()
