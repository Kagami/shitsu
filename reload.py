#!/usr/bin/env python

import os.path
import sys


# TODO: Shouldn't we use optparse and `./C.C..py -r' ?
reload_filename = "__reload__"
path = os.path.join(sys.path[0], "tmp", reload_filename)
open(path, "w").close()
