#!/usr/bin/env python
'''
  what proportion of each column are populated?
'''

import argparse
import collections
import csv
import logging
import sys

import numpy

def main(delimiter, fh, out):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  summary = collections.defaultdict(int)
  total = 0
  for idx, row in enumerate(reader): # each row
    total += 1
    this_row = 0
    for rn in row: # each column
      if row[rn] == '':
        summary[rn] += 1
        this_row += 1
      else:
        summary[rn] += 0
    if this_row > 0:
      logging.debug('row %i: %i missing values', idx, this_row)

  # summarise
  out.write('Column\tEmpty\tNon-Empty\tPct\n')
  for r in sorted(summary):
    out.write('{}\t{}\t{}\t{:.3f}\n'.format(r, summary[r], total - summary[r], summary[r] / total * 100))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Basic stats of specified columns')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--encoding', required=False, help='input files')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if args.encoding and "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)

  main(args.delimiter, sys.stdin, sys.stdout)
