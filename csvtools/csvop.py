#!/usr/bin/env python
'''
  apply operation to columns to generate a new column
'''

import argparse
import collections
import csv
import functools
import logging
import operator
import sys

def process(fh, cols, op, dest, delimiter, default_newval=-1, join_string=' ', format_dest=None, rank_count=None):
    '''
      apply operation and write to dest
    '''
    logging.info('reading from stdin...')
    out = csv.writer(sys.stdout, delimiter=delimiter)
    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames + [dest])
    out.writeheader()
    for idx, row in enumerate(fh):
      try:
        if op == 'sum': # total of specified columns
          newval = sum(float(row[col]) for col in cols)
        elif op == 'diff':
          newval = float(row[cols[0]]) - sum(float(row[col]) for col in cols[1:])
        elif op == 'product':
          newval = functools.reduce(operator.mul, [float(row[col]) for col in cols])
        elif op == 'divide':
          if float(row[cols[1]]) == 0:
            newval = 0
          else:
            newval = float(row[cols[0]]) / float(row[cols[1]])
        elif op == 'min': # min value of columns
          newval = min(float(row[col]) for col in cols)
        elif op == 'max': # max value of columns
          newval = max(float(row[col]) for col in cols)
        elif op == 'maxcol': # column name of max
          candidates = {col: float(row[col]) for col in cols}
          newval = max(row, key=candidates.get)
        elif op == 'rank':
           subset = {col: float(row[col]) for col in cols}
           s = sorted(subset, key=subset.get)[::-1]
           if rank_count is not None:
             s = s[:rank_count]
           newval = ' '.join(['{}({})'.format(x, row[x]) for x in s])
        elif op == 'concat':
          newval = join_string.join([row[col] for col in cols])
        elif op == 'inc':
          newval = idx
        else:
          logging.fatal('Unrecognised operation %s', op)
      except:
        logging.warn('Failed to process line %i with rows %s', idx, ' '.join(['{}={}'.format(colname, row[colname]) for colname in cols]))
        newval = default_newval

      if format_dest is not None:
        newval = ('{:%s}' % format_dest).format(newval)

      logging.debug('writing %s to %s', newval, dest)
      row[dest] = newval
      out.writerow(row)

    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--cols', nargs='*', required=False, help='column name')
    parser.add_argument('--op', required=True, help='operation sum, diff, product, divide, min, max, maxcol, concat, inc, rank')
    parser.add_argument('--join_string', required=False, default=' ', help='how to join concat')
    parser.add_argument('--rank_count', required=False, type=int, help='how many to include in rank')
    parser.add_argument('--format', required=False, help='how to format output')
    parser.add_argument('--dest', required=True, help='column name to add')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    args = parser.parse_args()
    if args.verbose:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.cols, args.op, args.dest, args.delimiter, join_string=args.join_string, format_dest=args.format, rank_count=args.rank_count)

if __name__ == '__main__':
    main()
