#!/usr/bin/env python
'''
  count occurrences of values
'''

import argparse
import collections
import csv
import logging
import re
import sys

def main(ifh, ofh, cols, delimiter, numeric):
  fh = csv.DictReader(ifh, delimiter=delimiter)
  out = csv.DictWriter(ofh, delimiter=delimiter, fieldnames=['value', 'count', 'pct'])
  counts = collections.defaultdict(int)
  out.writeheader()
  total = skipped = 0
  for idx, row in enumerate(fh):
    if numeric:
      try:
        key = float(row[cols[0]])
      except:
        skipped += 1
        continue
    else:
      key = '-'.join([row[c] for c in cols])
    counts[key] += 1
    total += 1

  logging.info('skipped %i and included %i', skipped, total)

  for k in sorted(counts):
    # todo arrange into bins for numeric
    out.writerow({'value': k, 'count': counts[k], 'pct': '{:.2f}'.format(100 * counts[k] / total)})

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Add column to tsv')
  parser.add_argument('--cols', required=True, nargs='+', default=[], help='cols to consider')
  parser.add_argument('--delimiter', required=False, default=',', help='delimiter')
  parser.add_argument('--encoding', default='utf-8', help='file encoding')
  parser.add_argument('--numeric', action='store_true', help='treat as numeric')
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
 
  main(sys.stdin, sys.stdout, args.cols, args.delimiter, args.numeric)