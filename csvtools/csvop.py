#!/usr/bin/env python
'''
  apply operation to columns to generate a new column
'''

import argparse
import collections
import csv
import logging
import sys

def process(fh, cols, op, dest, delimiter, default_newval=-1):
    '''
      apply operation and write to dest
    '''
    logging.info('reading from stdin...')
    out = csv.writer(sys.stdout, delimiter=delimiter)
    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames + [dest])
    out.writeheader()
    for idx, row in enumerate(fh):
      try:
        if op == 'sum':
          newval = sum(float(row[col]) for col in cols)
        elif op == 'diff':
          newval = float(row[cols[0]]) - sum(float(row[col]) for col in cols[1:])
        else:
          logging.fatal('Unrecognised operation %s', op)
      except:
        logging.warn('Failed to process line %i with rows %s', idx, ' '.join(['{}={}'.format(colname, row[colname]) for colname in cols]))
        newval = default_newval

      row[dest] = newval
      out.writerow(row)

    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--cols', nargs='+', required=True, help='column name')
    parser.add_argument('--op', required=True, help='operation sum, diff')
    parser.add_argument('--dest', required=True, help='column name to add')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    args = parser.parse_args()
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.cols, args.op, args.dest, args.delimiter)

if __name__ == '__main__':
    main()
