#!/usr/bin/env python
'''
  Normalize specified columns in each row as a proportion of the row total.
  Appends a new column 'total' representing the sum of the specified columns.
'''

import argparse
import collections
import csv
import logging
import sys

import numpy

def main(delimiter, fh, out, cols):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=reader.fieldnames + ['total'])
  writer.writeheader()
  if cols is None:
    cols = reader.fieldnames
  for idx, r in enumerate(reader): # each row
    r['total'] = sum([float(r[v]) for v in cols])
    for v in cols:
      r[v] = '{:.6f}'.format(float(r[v]) / r['total'])
    writer.writerow(r)
    
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Basic stats of specified columns')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--encoding', required=False, help='input files')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  parser.add_argument('--cols', required=False, nargs='+', help='cols to include in calculation')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if args.encoding and "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)

  main(args.delimiter, sys.stdin, sys.stdout, args.cols)
