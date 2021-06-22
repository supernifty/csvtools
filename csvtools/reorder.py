#!/usr/bin/env python

import sys

lines = sys.stdin.readlines()
for v in sys.argv[1:]:
  sys.stdout.write(lines[int(v)])
