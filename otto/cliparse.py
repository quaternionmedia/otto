import argparse

parser = argparse.ArgumentParser()

#render
parser.add_argument('--dry', '-n', action='store_false', dest='render', default=True,
                    help='for dry run (no render)')

#renderFrame
parser.add_argument('--frame', '-f', action='store', type=int, dest='frame', default=-1,
                    help='followed by a number (-f 9) to render that frame')

#open
parser.add_argument('--open', '-o', action='store_true', dest='open', default=False,
                    help='open rendered video with vlc')

#verbose
parser.add_argument('--verbose', '-v', action='store_true', dest='verbose', default=False,
                    help='for verbose')

parser.add_argument('--size', '-s', dest='size', nargs='+', type=int, 
                    help='size of rendered movie')

args = parser.parse_args()
