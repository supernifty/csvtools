#!/usr/bin/env python
'''
  apply operation to columns to generate a new column
'''

import argparse
import collections
import csv
import functools
import logging
import math
import operator
import sys

def process(fh, cols, op, dests, delimiter, default_newval=-1, join_string=' ', format_dest=None):
    '''
      apply operation and write to dest
    '''
    logging.info('reading from stdin...')
    out = csv.writer(sys.stdout, delimiter=delimiter)
    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames + dests)
    out.writeheader()
    for idx, row in enumerate(fh):
      try:
        if op == 'sum': # total of specified columns
          newval = sum(float(row[col]) for col in cols)
        elif op == 'diff':
          newval = float(row[cols[0]]) - sum(float(row[col]) for col in cols[1:])
        elif op == 'product':
          newval = functools.reduce(operator.mul, [float(row[col]) for col in cols])
        elif op == 'log':
          newval = math.log(functools.reduce(operator.mul, [float(row[col]) for col in cols]))
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
          newval = max(candidates, key=candidates.get)
        elif op == 'rank':
           subset = {col: float(row[col]) for col in cols}
           s = sorted(subset, key=subset.get)[::-1]
           if len(dests) > 1:
             for idx in range(0, len(dests)):
               row[dests[idx]] = '{} {}'.format(s[idx], row[s[idx]])
             newval = '{} {}'.format(s[0], row[s[0]])
           else: # push into one column
             newval = ' '.join(['{}({})'.format(x, row[x]) for x in s])

        elif op == 'concat':
          newval = join_string.join([row[col] for col in cols])
        elif op == 'inc':
          newval = idx
        elif op == 'truncate':
          newval = row[col][:int(format_dest)]
        elif op == 'format':
          newval = '{}'.format(format_dest).format(**row)
        else:
          logging.fatal('Unrecognised operation %s', op)
      except:
        logging.warning('Failed to process line %i with rows %s', idx, ' '.join(['{}={}'.format(colname, row[colname]) for colname in cols]))
        #raise
        newval = default_newval

      if op != 'format' and format_dest is not None:
        newval = format_dest.format(newval)

      logging.debug('writing %s to %s', newval, dests[0])
      row[dests[0]] = newval
      out.writerow(row)

    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--cols', nargs='*', required=False, help='column name')
    parser.add_argument('--op', required=True, help='operation sum, diff, product, divide, min, max, maxcol, concat, inc, log, rank, format, truncate')
    parser.add_argument('--join_string', required=False, default=' ', help='how to join concat')
    parser.add_argument('--format', required=False, help='how to format output (applies to rank, format, truncate)')
    parser.add_argument('--dests', required=True, nargs='+', help='column name(s) to add')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    parser.add_argument('--default_newval', default='-1', required=False, help='if dest cannot be populated')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    args = parser.parse_args()
    if args.verbose:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.cols, args.op, args.dests, args.delimiter, default_newval=args.default_newval, join_string=args.join_string, format_dest=args.format)

if __name__ == '__main__':
    main()
