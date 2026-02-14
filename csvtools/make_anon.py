#!/usr/bin/env python
'''
  make a map of random ids
'''

import argparse
import collections
import csv
import logging
import random
import sys

def main(ifh, ofh, col, prefix, delimiter, write_map):
  logging.info('starting...')
  idr = csv.DictReader(ifh, delimiter=delimiter)
  seen = set()
  rows = []
  for r in idr:
    seen.add(r[col])
    rows.append(r)
  logging.info('%i distinct values', len(seen))
  items = list(seen)
  random.shuffle(items) 
  digits = len(str(len(seen)))
  to_anon = {}
  for i, item in enumerate(items):
    to_anon[item] = '{}{}'.format(prefix, '{}'.format(i).zfill(digits))

  if write_map is not None:
    odw = csv.DictWriter(open(write_map, 'wt'), delimiter=delimiter, fieldnames=[col, 'anon'])
    odw.writeheader()
    for i, item in enumerate(items):
      odw.writerow({col: item, 'anon': to_anon[item]})

  odw = csv.DictWriter(ofh, delimiter=delimiter, fieldnames=idr.fieldnames + ['anon'])
  odw.writeheader()
  for _, item in enumerate(rows):
    item['anon'] = to_anon[item[col]]
    odw.writerow(item)

  logging.info('done')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='make a map of random ids')
  parser.add_argument('--col', required=True, help='more logging')
  parser.add_argument('--prefix', required=False, default='', help='more logging')
  parser.add_argument('--write_map', required=False, help='write map to this file')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(sys.stdin, sys.stdout, args.col, args.prefix, args.delimiter, args.write_map)
