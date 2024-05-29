#!/usr/bin/env python
'''
  adds a new column with specified value
'''

import argparse
import collections
import csv
import logging
import re
import sys

def main(dest, cols, delimiter):
  fh = csv.DictReader(sys.stdin, delimiter=delimiter)
  out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames + [dest])
  counts = collections.defaultdict(int)
  out.writeheader()
  for idx, row in enumerate(fh):
    logging.debug('processing line %i...', idx)
    key = '-'.join([row[c] for c in cols])
    counts[key] += 1
    row[dest] = '{}-{}'.format(key, counts[key])
    out.writerow(row)
    if (idx + 1) % 100000 == 0:
      logging.debug('%i lines processed', idx + 1)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Add column to tsv')
  parser.add_argument('--dest', required=True, help='new col name')
  parser.add_argument('--cols', required=False, nargs='*', default=[], help='rule for value of the form col[<=>%%]val:colval')
  parser.add_argument('--delimiter', required=False, default=',', help='delimiter')
  parser.add_argument('--encoding', default='utf-8', help='file encoding')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)
    logging.debug('encoding %s applied', args.encoding)
  else:
    logging.debug('using default encoding')
 
  main(args.dest, args.cols, args.delimiter)
