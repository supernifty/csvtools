#!/usr/bin/env python
'''
  filter on column names
'''

import argparse
import collections
import csv
import gzip
import logging
import signal
import sys

signal.signal(signal.SIGPIPE, signal.SIG_DFL)

def get_fh(fh):
  try:
    c = fh.read(1)
    fh.seek(0)
    if ord(c) == 0x1f:
      return gzip.open(fh, 'rt')
    else:
      return fh
  except:
    return sys.stdin

def safe_float(v, default):
  if v in ('nan', 'inf'):
    return default

  try:
    return float(v)
  except:
    return default

def process(reader, cols, numeric, descending, order, delimiter):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')

    lines = []
    for row in reader:
      lines.append(row)

    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=reader.fieldnames)
    out.writeheader()

    if numeric:
      sorted_lines = sorted(lines, key=lambda k: [safe_float(k[col], -1e100) for col in cols])
    else:
      if order is None:
        sorted_lines = sorted(lines, key=lambda k: [k[col] for col in cols]) # each col of interest
      else:
        sorted_lines = sorted(lines, key=lambda k: [order.index(k[col]) if k[col] in order else len(order) for col in cols])

    if descending:
      sorted_lines = sorted_lines[::-1]

    for row in sorted_lines:
      out.writerow(row)

    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Update CSV column values')
    parser.add_argument('--cols', required=True, nargs='+', help='column to sort on')
    parser.add_argument('--delimiter', default=',', help='file delimiter')
    parser.add_argument('--numeric', action='store_true', help='numeric sort')
    parser.add_argument('--order', nargs='+', required=False, help='sort categories in this order')
    parser.add_argument('--desc', action='store_true', help='descending')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.cols, args.numeric, args.desc, args.order, args.delimiter)

if __name__ == '__main__':
    main()
