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

def main(delimiter, fh, out, drop_empty):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  summary = collections.defaultdict(int)
  total = 0
  rows = []
  for idx, row in enumerate(reader): # each row
    total += 1
    this_row = 0
    for rn in row: # each column
      if rn is None:
        continue # how is this even possible?
      if row[rn] == '':
        summary[rn] += 1
        this_row += 1
      else:
        summary[rn] += 0
    if this_row > 0:
      logging.debug('row %i: %i missing values', idx, this_row)
    if drop_empty:
      rows.append(row)

  if drop_empty:
    # write without empties
    non_empty_cols = [r for r in reader.fieldnames if summary[r] < total]
    to_drop = [r for r in reader.fieldnames if summary[r] == total]
    logging.info('dropping: %s', ' '.join(to_drop))
    odw = csv.DictWriter(out, delimiter=delimiter, fieldnames=non_empty_cols)
    odw.writeheader()
    for r in rows:
      r = {k: r[k] for k in non_empty_cols}
      odw.writerow(r)
  else:
    # summarise
    logging.debug('sorting %s', summary)
    out.write('Column\tEmpty\tNon-Empty\tPct\n')
    for r in sorted(summary):
      out.write('{}\t{}\t{}\t{:.3f}\n'.format(r, summary[r], total - summary[r], summary[r] / total * 100))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Basic stats of specified columns')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--encoding', required=False, help='input files')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  parser.add_argument('--drop_empty', action='store_true', help='no summary but write dataset without empty cols')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if args.encoding and "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)

  main(args.delimiter, sys.stdin, sys.stdout, args.drop_empty)
