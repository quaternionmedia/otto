from os import environ

LOG_DIR = environ.get('LOG_DIR', 'logs')
DATA_DIR = environ.get('DATA_DIR', 'data')

defaults = {
    'fontcolor': '#FFFFFF',
    'themecolor': '#FFFF00',
    'address': '123 Main St',
    'hours': '24/7',
    'website': 'alfred.quaternion.media',
}
