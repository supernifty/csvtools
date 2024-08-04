#!/usr/bin/env python
'''
  measure proportions of categorical variables across groups
'''

import argparse
import collections
import csv
import logging
import sys

def main(ifh, ofh, delimiter, col, dest, names, separators, equal_policy):
  logging.info('starting...')

  idr = csv.DictReader(ifh, delimiter=delimiter)
  odr = csv.DictWriter(ofh, delimiter=delimiter, fieldnames=idr.fieldnames + [dest])
  odr.writeheader()
  summary = collections.defaultdict(int)
  for r in idr:
    v = float(r[col])
    result = names[-1] # if larger than everything
    for name, sep in zip(names[:-1], separators):
      if v < sep or equal_policy == 'down' and v <= sep:
        result = name
        break
    r[dest] = result
    summary[result] += 1
    odr.writerow(r)

  logging.info('done. summary: %s', ', '.join(['{}: {}'.format(x, summary[x]) for x in summary]))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='make a stratified variable')
  parser.add_argument('--delimiter', default=',', help='delimiter')
  parser.add_argument('--col', required=True, help='input col')
  parser.add_argument('--dest', required=True, help='output col')
  parser.add_argument('--names', required=True, nargs='+', help='categories')
  parser.add_argument('--separators', required=True, nargs='*', type=float, help='separator values')
  parser.add_argument('--equal_policy', default='down', help='what if value = separator? down|up')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(sys.stdin, sys.stdout, args.delimiter, args.col, args.dest, args.names, args.separators, args.equal_policy)


# python src/stratify.py --delimiter '    ' --col Reduced.SBS --dest Dosage --names Negative Low Medium High --separators 0.1 0.13075 0.25325 --equal_policy down

