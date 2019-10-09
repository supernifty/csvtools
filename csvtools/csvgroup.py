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

def process(fh, op, delimiter, join_string=' + '):
    '''
      apply operation and write to dest
    '''
    logging.info('reading from stdin...')
    out = csv.writer(sys.stdout, delimiter=delimiter)
    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames)
    out.writeheader()
    out_rows = {}
    for idx, row in enumerate(fh):
      ops = {}
      for o in op:
        name, value = o.split('=')
        ops[name] = value

      key = []
      for field in fh.fieldnames:
        if field not in ops:
          key.append(row[field])

      key = tuple(key)
      if key not in out_rows:
        out_rows[key] = {}

      for field in fh.fieldnames:
        if field in ops:
          if ops[field] == 'sum':
            if field not in out_rows[key]:
              out_rows[key][field] = 0.0
            out_rows[key][field] += float(row[field])
          elif ops[field] == 'join':
            if field not in out_rows[key]:
              out_rows[key][field] = row[field]
            else:
              out_rows[key][field] = join_string.join([out_rows[key][field], row[field]])
          else:
            logging.warn('unrecognised operation %s', ops[field])
        else:
          out_rows[key][field] = row[field]
        
    for key in out_rows:
      out.writerow(out_rows[key])

    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--op', required=True, nargs='+', help='colname=[join|sum] ...')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    args = parser.parse_args()
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.op, args.delimiter)

if __name__ == '__main__':
    main()
