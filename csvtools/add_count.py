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

def main(dest, cols, delimiter, as_map, cols_as_keys=False):
  fh = csv.DictReader(sys.stdin, delimiter=delimiter)
  if as_map is None:
    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames + [dest])
  else:
    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=[as_map, dest])
  out.writeheader()
  counts = collections.defaultdict(int)
  for idx, row in enumerate(fh):
    logging.debug('processing line %i...', idx)
    key = '-'.join([row[c] for c in cols])
    if cols_as_keys:
      if key not in counts:
        counts[key] = len(counts)
    else:
      counts[key] += 1
    if len(cols) > 0:
      if cols_as_keys:
        row[dest] = counts[key]
      else:
        row[dest] = '{}-{}'.format(key, counts[key])
    else:
      row[dest] = counts[key]
    if as_map is None:
      out.writerow(row)
    else:
      row = {as_map: row[as_map], dest: row[dest]}
      out.writerow(row)
    if (idx + 1) % 100000 == 0:
      logging.debug('%i lines processed', idx + 1)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Add column to tsv')
  parser.add_argument('--dest', required=True, help='new col name')
  parser.add_argument('--cols', required=False, nargs='*', default=[], help='cols to stratify')
  parser.add_argument('--cols_as_keys', action='store_true', help='cols to use as key')
  parser.add_argument('--delimiter', required=False, default=',', help='delimiter')
  parser.add_argument('--encoding', default='utf-8', help='file encoding')
  parser.add_argument('--as_map', help='write the mapping with this col as key')
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
 
  main(args.dest, args.cols, args.delimiter, args.as_map, args.cols_as_keys)
