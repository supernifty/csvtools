#!/usr/bin/env python
'''
  Normalize specified columns by scaling each value by the column maximum (or a given threshold).
  Each value is replaced by (value / max) so that values lie between 0 and 1.
'''

import argparse
import collections
import csv
import logging
import sys

import numpy

def main(delimiter, fh, out, cols, threshold=None):
  logging.info('reading...')
  reader = csv.DictReader(fh, delimiter=delimiter)
  rows = []
  maxes = collections.defaultdict(float)
  for idx, r in enumerate(reader): # each row
    rows.append(r)
    for v in cols:
      val = float(r[v])
      if threshold is not None:
        val = min(val, threshold)
      maxes[v] = max(maxes[v], val)

  logging.info('writing...')
  writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=reader.fieldnames)
  writer.writeheader()
  for r in rows:
    for v in cols:
      val = float(r[v])
      if threshold is not None:
        val = min(val, threshold)
      r[v] = val / maxes[v]
    writer.writerow(r)
  logging.info('done...')
    
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Basic stats of specified columns')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--encoding', required=False, help='input files')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  parser.add_argument('--cols', required=False, nargs='+', help='cols to normalise')
  parser.add_argument('--threshold', required=False, type=float, help='cols to normalise')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if args.encoding and "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)

  main(args.delimiter, sys.stdin, sys.stdout, args.cols, args.threshold)
