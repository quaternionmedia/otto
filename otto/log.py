import logging
import os
import sys
from time import strftime

from otto.config import LOG_DIR


def ts():
    return strftime('%Y%m%d-%H%M%S')


if not os.path.isdir(LOG_DIR):
    os.mkdir(LOG_DIR)


fileout = os.path.join(LOG_DIR, f'{ts()}_otto.log')

log = logging.getLogger(__name__)


log.setLevel(logging.INFO)


syshandler = logging.StreamHandler(sys.stdout)
syshandler.setLevel(logging.INFO)

filehandler = logging.FileHandler(fileout)
filehandler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
syshandler.setFormatter(formatter)
filehandler.setFormatter(formatter)


log.addHandler(syshandler)
log.addHandler(filehandler)
