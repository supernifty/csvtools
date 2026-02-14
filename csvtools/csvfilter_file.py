#!/usr/bin/env python

import argparse
import collections
import csv
import logging
import sys

def main(ifh, ofh, delimiter, col, filename):
  logging.info('reading %s...', filename)
  f = set()
  for r in csv.DictReader(open(filename, 'rt'), delimiter=delimiter):
    f.add(r[col])
  logging.info('%i values', len(f))

  logging.info('starting...')
  idr = csv.DictReader(ifh, delimiter=delimiter)
  odw = csv.DictWriter(ofh, delimiter=delimiter, fieldnames=idr.fieldnames)
  odw.writeheader()
  for r in idr:
    if r[col] in f:
      odw.writerow(r)

  logging.info('done')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='filter rows based on another file')
  parser.add_argument('--col', required=True, help='more logging')
  parser.add_argument('--file', required=True, help='more logging')
  parser.add_argument('--delimiter', default=',', help='more logging')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(sys.stdin, sys.stdout, args.delimiter, args.col, args.file)
