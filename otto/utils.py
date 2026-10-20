import os
import tempfile
import urllib.request

from PIL.ImageColor import getcolor
from tqdm import tqdm


class DownloadProgressBar(tqdm):
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_url(url, output_path):
    """Fetch `url` to `output_path`, which appears whole or not at all.

    The file is written beside `output_path` under a temporary name, readable
    by this user alone, and moved into place once it is complete. Written in
    place, a fetch that failed part way left a truncated file at the path a
    cache looks for, which every later render then used as if it were whole.
    """
    directory, name = os.path.split(output_path)
    handle, partial = tempfile.mkstemp(
        prefix=f'.{name}.', suffix='.part', dir=directory or os.curdir
    )
    os.close(handle)
    try:
        with DownloadProgressBar(
            unit='B', unit_scale=True, miniters=1, desc=url.split('/')[-1]
        ) as t:
            urllib.request.urlretrieve(url, filename=partial, reporthook=t.update_to)
        os.replace(partial, output_path)
    except BaseException:
        try:
            os.remove(partial)
        except OSError:
            pass
        raise


def rgbToDec(rgb: str):
    color = getcolor(rgb, 'RGB')
    color = [c / 255 for c in color]
    return color
