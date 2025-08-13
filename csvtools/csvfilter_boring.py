#!/usr/bin/env python
'''
  filter rows
'''

import argparse
import collections
import csv
import logging
import sys

import numpy

def is_numeric(value):
  try:
    _ = float(value)
    return True
  except ValueError:
    return False

def process(ifh, ofh, delimiter, min_range=0.05, min_mean=0.0):
    '''
        read in csv file, drop any field with range < minrange and mean < minmean
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')

    data = []
    fh = csv.DictReader(ifh, delimiter=delimiter)
    for r in fh:
      data.append(r)

    include = set() # indexes of columns to include
    for c in range(len(data[0])):
      if all([is_numeric(data[i][fh.fieldnames[c]]) for i in range(len(data))]):
        coldata = [float(data[i][fh.fieldnames[c]]) for i in range(len(data))]
        minval = min(coldata)
        maxval = max(coldata)
        mean = numpy.mean(coldata)
        if mean > min_mean and abs(maxval - minval) > min_range:
          logging.debug('keeping %s with mean %.6f and range %f-%f', fh.fieldnames[c], mean, minval, maxval)
          include.add(c)
        else:
          logging.debug('dropping %s with mean %.6f and range %f-%f', fh.fieldnames[c], mean, minval, maxval)
      else:
        logging.debug('keeping non-numeric %s', fh.fieldnames[c])
        include.add(c) # non-numeric passes

    logging.info('considered %i cols, including %i', len(data[0]), len(include))

    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=[fh.fieldnames[i] for i in sorted(list(include))])
    out.writeheader()
    for d in data:
      row = {fh.fieldnames[i]: d[fh.fieldnames[i]] for i in include}
      out.writerow(row)
    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Filter rows')
    parser.add_argument('--min_range', default=0.05, type=float, help='min range of column')
    parser.add_argument('--min_mean', default=0.0, type=float, help='min mean of column')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    parser.add_argument('--encoding', default='utf-8', help='file encoding')
    parser.add_argument('--verbose', action='store_true', default=False, help='more logging')
    parser.add_argument('--quiet', action='store_true', default=False, help='less logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    if "reconfigure" in dir(sys.stdin):
      sys.stdin.reconfigure(encoding=args.encoding)
      logging.debug('encoding %s applied', args.encoding)
    else:
      logging.debug('using default encoding')
    process(sys.stdin, sys.stdout, delimiter=args.delimiter, min_range=args.min_range, min_mean=args.min_mean)

if __name__ == '__main__':
    main()
