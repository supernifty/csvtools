#!/usr/bin/env python
'''
  Filter out duplicate rows considering all columns.
  Reads a CSV from stdin and writes only the first occurrence of each row, preserving the original order.
'''

import argparse
import collections
import csv
import logging
import sys

def main(delimiter, fh, out):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=reader.fieldnames)
  writer.writeheader()
  seen = set()
  for row in reader:
    items = tuple([row[x] for x in sorted(row.keys())])
    if items in seen:
      continue
    seen.add(items)
    writer.writerow(row)
    out.flush()
    
  logging.info('done writing %i', len(seen))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='write unique rows')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.delimiter, sys.stdin, sys.stdout)
