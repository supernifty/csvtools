#!/usr/bin/env python
'''
  split into multiple files on column
'''

import argparse
import collections
import csv
import logging
import sys

def main(ifh, target, delimiter, lines):
  logging.info('starting...')
  idr = csv.DictReader(ifh, delimiter=delimiter)
  index = 0
  written = 0
  odw = csv.DictWriter(open(target.replace('value', str(index)), 'wt'), delimiter=delimiter, fieldnames=idr.fieldnames)
  odw.writeheader()
  logging.info('writing to %s', target.replace('value', str(index)))
  
  for i, r in enumerate(idr):
    odw.writerow(r)
    written += 1
    if written >= lines:
      index += 1
      written = 0
      odw = csv.DictWriter(open(target.replace('value', str(index)), 'wt'), delimiter=delimiter, fieldnames=idr.fieldnames)
      odw.writeheader()
      logging.info('writing to %s', target.replace('value', str(index)))

  logging.info('done. %i files.', index + 1)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='make a stratified variable')
  parser.add_argument('--delimiter', default=',', help='delimiter')
  parser.add_argument('--lines', required=True, type=int, help='lines per file')
  parser.add_argument('--target', required=True, help='output file pattern: replace value with number')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(sys.stdin, args.target, args.delimiter, args.lines)

