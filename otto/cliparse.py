import argparse

parser = argparse.ArgumentParser()

# render
parser.add_argument(
    '--dry',
    '-n',
    action='store_false',
    dest='render',
    default=True,
    help='for dry run (no render)',
)

# renderFrame
parser.add_argument(
    '--frame',
    '-f',
    action='store',
    type=float,
    dest='frame',
    default=-1,
    help='followed by a time in seconds (-f 9.2) to render that frame',
)

# open
parser.add_argument(
    '--open',
    '-o',
    action='store_true',
    dest='open',
    default=False,
    help='open rendered video with vlc',
)

# verbose
parser.add_argument(
    '--verbose',
    '-v',
    action='store_true',
    dest='verbose',
    default=False,
    help='for verbose',
)

parser.add_argument(
    '--size',
    '-s',
    dest='size',
    nargs='+',
    type=int,
    default=[640, 480],
    help='size of rendered movie',
)


def parse_args(argv=None):
    """The parsed command line: `argv`, or sys.argv when it is None.

    Parsing used to happen when this module was imported, so importing it
    from any other program -- a test runner, a worker -- read that program's
    arguments, and exited it on any it did not recognise.
    """
    return parser.parse_args(argv)
