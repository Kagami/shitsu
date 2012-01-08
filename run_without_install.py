#!/usr/bin/env python

import sys
import os.path
dirname = os.path.dirname(__file__)
sys.path.insert(0, dirname)
import shitsu


config_path = os.path.join(dirname, "shitsu", "shitsu.cfg")
shitsu.run(config_path)
