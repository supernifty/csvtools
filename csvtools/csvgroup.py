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
      for o in op: # each 
        name, value = o.split('=') # column, operation
        ops[name] = value # ops[column] = operation

      key = []
      for field in fh.fieldnames:
        if field not in ops:
          key.append(row[field])

      key = tuple(key) # all keys not with an operation
      if key not in out_rows:
        out_rows[key] = {}

      for field in fh.fieldnames:
        if field in ops:
          if ops[field] == 'sum':
            if field not in out_rows[key]:
              out_rows[key][field] = 0.0
            out_rows[key][field] += float(row[field])
          elif ops[field] == 'sumint':
            if field not in out_rows[key]:
              out_rows[key][field] = 0
            out_rows[key][field] += int(row[field])
          elif ops[field] == 'count':
            if field not in out_rows[key]:
              out_rows[key][field] = 0
            out_rows[key][field] += 1
          elif ops[field] == 'mean':
            if field not in out_rows[key]:
              out_rows[key][field] = (0.0, 0)
            try:
              out_rows[key][field] = (out_rows[key][field][0] + float(row[field]), out_rows[key][field][1] + 1) # tracking sum, count
            except:
              logging.warning('field %s not numeric: %s', field, row[field])
          elif ops[field] == 'join':
            if field not in out_rows[key]:
              out_rows[key][field] = row[field]
            else:
              out_rows[key][field] = join_string.join([out_rows[key][field], row[field]])
          elif ops[field] == 'joinset':
            if field not in out_rows[key]:
              out_rows[key][field] = row[field]
            else:
              vals = set(out_rows[key][field].split(join_string)) # not great
              vals.add(row[field])
              out_rows[key][field] = join_string.join(list(vals))
          elif ops[field] == 'min':
            if field not in out_rows[key]:
              out_rows[key][field] = row[field]
            else:
              out_rows[key][field] = min([out_rows[key][field], row[field]])
          elif ops[field] == 'max':
            if field not in out_rows[key]:
              out_rows[key][field] = row[field]
            else:
              out_rows[key][field] = max([out_rows[key][field], row[field]])
          else:
            logging.warn('unrecognised operation %s', ops[field])
        else:
          out_rows[key][field] = row[field]
        
    for key in out_rows:
      # post processing
      for field in ops:
        if ops[field] == 'mean':
          if out_rows[key][field][1] > 0:
            out_rows[key][field] = out_rows[key][field][0] / out_rows[key][field][1] 
          else:
            out_rows[key][field] = 'n/a'
      # write it
      out.writerow(out_rows[key])

    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--op', required=True, nargs='+', help='colname=[join|joinset|sum|sumint|count|min|max] ...')
    parser.add_argument('--join_string', required=False, default=' + ', help='join delimiter')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    args = parser.parse_args()
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.op, args.delimiter, args.join_string)

if __name__ == '__main__':
    main()
