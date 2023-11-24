#!/usr/bin/env python
'''
  split into multiple files on column
'''

import argparse
import collections
import csv
import logging
import sys

def main(ifh, target, delimiter, col):
  logging.info('starting...')
  idr = csv.DictReader(ifh, delimiter=delimiter)
  ofs = {}
  
  for i, r in enumerate(idr):
    if r[col] not in ofs:
      ofs[r[col]] = csv.DictWriter(open(target.replace('value', r[col]), 'wt'), delimiter=delimiter, fieldnames=idr.fieldnames)
      ofs[r[col]].writeheader()
      logging.info('opened %s', target.replace('value', r[col])) 
    ofs[r[col]].writerow(r)
    if i % 1000000 == 0:
      logging.info('%i rows written to %i files', i, len(ofs))

  logging.info('done. %i files.', len(ofs))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='make a stratified variable')
  parser.add_argument('--delimiter', default=',', help='delimiter')
  parser.add_argument('--col', required=True, help='column to split on')
  parser.add_argument('--target', required=True, help='output file pattern: replace value with colvalue')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(sys.stdin, args.target, args.delimiter, args.col)

