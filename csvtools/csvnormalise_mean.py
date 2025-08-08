#!/usr/bin/env python
'''
  normalise columns by mean
'''

import argparse
import collections
import csv
import logging
import sys

import numpy

def main(delimiter, fh, out, cols, sd):
  logging.info('reading...')
  reader = csv.DictReader(fh, delimiter=delimiter)
  rows = []
  vals = collections.defaultdict(list)
  for idx, r in enumerate(reader): # each row
    rows.append(r)
    for v in cols:
      vals[v].append(float(r[v]))

  logging.info('calculating...')
  means = {k: numpy.mean(vals[k]) for k in vals}
  sds = {k: numpy.std(vals[k], ddof=1) for k in vals}

  logging.info('writing...')
  writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=reader.fieldnames)
  writer.writeheader()
  for r in rows:
    for v in cols:
      val = float(r[v])
      r[v] = val - means[v]
      if sd:
        r[v] /= sds[v]
    writer.writerow(r)
  logging.info('done...')
    
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Basic stats of specified columns')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--encoding', required=False, help='input files')
  parser.add_argument('--sd', action='store_true', help='also normalise sd')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  parser.add_argument('--cols', required=False, nargs='+', help='cols to normalise')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if args.encoding and "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)

  main(args.delimiter, sys.stdin, sys.stdout, args.cols, args.sd)
