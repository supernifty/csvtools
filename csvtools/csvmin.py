#!/usr/bin/env python
'''
  filter rows
'''

import argparse
import collections
import csv
import logging
import sys

def process(fh, col, minval, maxval, delimiter, include):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')
    headers = next(fh)
    if col not in headers:
      logging.fatal('column %s not found in %s', col, headers)

    target = headers.index(col)

    out = csv.writer(sys.stdout, delimiter=delimiter)
    out.writerow(headers)
    lines = written = 0
    
    for lines, row in enumerate(fh):
      if (minval is None or float(row[target]) > minval) and (maxval is None or float(row[target]) < maxval): # it's in range
        out.writerow(row)
        written += 1
      elif include:
        if minval is not None and float(row[target]) < minval:
          row[target] = minval
        elif maxval is not None and float(row[target]) > maxval:
          row[target] = maxval
        out.writerow(row)
        written += 1
        
    logging.info('wrote %i of %i', written, lines + 1)

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--col', help='column name')
    parser.add_argument('--min', type=float, help='minimum value for column')
    parser.add_argument('--max', type=float, help='maximum value for column')
    parser.add_argument('--include', action='store_true', help='write at maximum or minimum value')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    args = parser.parse_args()
    process(csv.reader(sys.stdin, delimiter=args.delimiter), args.col, args.min, args.max, args.delimiter, args.include)

if __name__ == '__main__':
    main()
