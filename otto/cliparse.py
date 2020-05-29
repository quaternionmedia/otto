from optparse import OptionParser

parser = OptionParser()

#render
parser.add_option("-n", action="store_false", dest="render", default=True)

#renderFrame
parser.add_option("-f", action="store", type="int", dest="frame", default=-1)

#open
parser.add_option("-o", action="store_true", dest="open", default=False)

#verbose
parser.add_option("-v", action="store_true", dest="verbose", default=False)

(options, args) = parser.parse_args()
