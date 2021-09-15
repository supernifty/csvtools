#!/usr/bin/env python
'''
  summarise numerical columns
'''

import argparse
import collections
import csv
import logging
import sys

import numpy

def check(summary, col):
  if col not in summary:
    summary[col] = {'n': 0, 'sum': 0, 'max': sys.float_info.min, 'min': sys.float_info.max, 'd': []}
  return summary

def main(delimiter, x, y, z, fh, out):
  logging.info('reading...')
  cell = {}
  xs = set()
  ys = set()
  for row in csv.DictReader(fh, delimiter=delimiter):
    xs.add(row[x])
    ys.add(row[y])
    cell[(row[x], row[y])] = row[z]

  fo = csv.DictWriter(out, delimiter=delimiter, fieldnames=[x] + sorted(list(xs)))
  fo.writeheader()
  for y in sorted(list(ys)):
    row = {x: y}
    for xv in xs:
      row[xv] = cell.get((xv, y),'')
    fo.writerow(row)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Basic stats of specified columns')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--x', required=True, help='x column')
  parser.add_argument('--y', required=True, help='y column')
  parser.add_argument('--z', required=True, help='z column')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--encoding', default='utf-8', help='file encoding')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)
  main(args.delimiter, args.x, args.y, args.z, sys.stdin, sys.stdout)
