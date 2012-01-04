#!/usr/bin/env python

import os.path
import sys


# TODO: Shouldn't we move it to cc.py?
reload_filename = "__reload__"
path = os.path.join(sys.path[0], "tmp", reload_filename)
open(path, "w").close()
