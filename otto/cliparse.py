import argparse

parser = argparse.ArgumentParser()

#render
parser.add_argument('-n', action='store_false', dest='render', default=True,
                    help='for dry run (no render)')

#renderFrame
parser.add_argument('-f', action='store', type=int, dest='frame', default=-1,
                    help='followed by a number (-f 9) to render that frame')

#open
parser.add_argument('-o', action='store_true', dest='open', default=False,
                    help='open rendered video with vlc')

#verbose
parser.add_argument('-v', action='store_true', dest='verbose', default=False,
                    help='for verbose')


args = parser.parse_args()
