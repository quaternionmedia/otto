import logging
import sys, os
import sys
import os
from time import strftime

timestr = strftime('%Y%m%d-%H%M%S')
if not os.path.isdir('output'):
    os.mkdir('output')
fileout = os.path.join('output', f'{timestr}_otto.log')

logger = logging.getLogger('otto')
logger.setLevel(logging.INFO)


syshandler = logging.StreamHandler(sys.stdout)
syshandler.setLevel(logging.INFO)

filehandler = logging.FileHandler(fileout)
filehandler.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
syshandler.setFormatter(formatter)
filehandler.setFormatter(formatter)


logger.addHandler(syshandler)
logger.addHandler(filehandler)
