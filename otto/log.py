import logging
import sys
from time import strftime


timestr = strftime('%Y%m%d-%H%M%S')
fileout = f'output/{timestr}_otto.log'

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
