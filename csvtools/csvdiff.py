#!/usr/bin/env python
'''
  column based diff
'''

import argparse
import collections
import csv
import logging
import sys

def main(f1_fn, f2_fn, ofh, key, delimiter):
  logging.info('reading %s...', f1_fn)
  r1 = {}
  f1 = csv.DictReader(open(f1_fn, 'rt'), delimiter=delimiter)
  for i, r in enumerate(f1):
    if key == 'index':
      r1[i] = r
      continue
    if r[key] in r1:
      logging.warn('duplicate key %s', r[key])
    r1[r[key]] = r

  logging.info('reading %s...', f2_fn)
  f2 = csv.DictReader(open(f2_fn, 'rt'), delimiter=delimiter)
  odw = csv.DictWriter(ofh, delimiter='\t', fieldnames=f2.fieldnames)
  odw.writeheader()
  seen = set()
  missing = 0
  diffs = 0
  for i, r in enumerate(f2):
    if key == 'index' and i in r1:
      seen.add(i)
      for c in r:
        if c in r1[i]:
          if r[c] != r1[i][c]:
            r[c] = "[{} vs {}]".format(r1[i][c], r[c])
            diffs += 1
      odw.writerow(r)
      continue
    if r[key] in r1:
      seen.add(key)
      # compare intersecting columns
      for c in r:
        if c in r1[r[key]]:
          if r[c] != r1[r[key]][c]:
            r[c] = "[{} vs {}]".format(r1[r[key]][c], r[c])
            diffs += 1
    else:
      missing += 1
    odw.writerow(r)

  logging.info('done. %i of %i overlapping rows. %i cell differences. %i unmatched.', len(seen), len(r1), diffs, missing)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--key', required=True, help='join on this key. "index" to use line number')
  parser.add_argument('--f1', required=True, help='files to compare')
  parser.add_argument('--f2', required=True, help='files to compare')
  parser.add_argument('--delimiter', default=',', help='delimiter')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.f1, args.f2, sys.stdout, args.key, args.delimiter)
