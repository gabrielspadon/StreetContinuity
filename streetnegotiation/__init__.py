#
#   Copyright 2019, Gabriel Spadon, all rights reserved.
#   This code is under GNU General Public License v3.0.
#       www.spadon.com.br & gabriel@spadon.com.br
#


import sys

if sys.version_info[:2] < (3, 6):
    m = "Python 3.6 or later is required for StreetPyradox (%d.%d was detected)."
    raise ImportError(m % sys.version_info[:2])
