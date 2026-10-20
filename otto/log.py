import logging
import os
import sys
from time import strftime

from otto.config import LOG_DIR


def ts():
    return strftime('%Y%m%d-%H%M%S')


log = logging.getLogger(__name__)
"""otto's logger. Importing this module configures nothing: see `configure`."""


def configure(log_dir=LOG_DIR):
    """Log INFO and above to stdout and to a timestamped file in `log_dir`.

    The directory is created here, when logging to it is asked for. Importing
    this module used to create it, and open a log file in it, in whatever
    directory the importing process happened to be running in.
    """
    os.makedirs(log_dir, exist_ok=True)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    for handler in (
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(log_dir, f'{ts()}_otto.log')),
    ):
        handler.setLevel(logging.INFO)
        handler.setFormatter(formatter)
        log.addHandler(handler)
    log.setLevel(logging.INFO)
    return log
