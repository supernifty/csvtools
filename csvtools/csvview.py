#!/usr/bin/env python
'''
  view each cell as a line
'''

import argparse
import collections
import csv
import functools
import logging
import operator
import sys

def process(fh, delimiter, out, mode):
    '''
      apply operation and write to dest
    '''
    logging.info('reading from stdin...')
    if mode == 'vertical':
      for idx, row in enumerate(fh):
        out.write('Row\t{}\n'.format(idx + 1))
        for key in sorted(row.keys()):
          out.write('{}\t{}\n'.format(key, row[key]))
        out.write('\n')
    elif mode == 'horizontal':
      widths = collections.defaultdict(int)
      for x in fh.fieldnames:
        widths[x] = len(x)
      rows = []
      idx = 0
      for idx, row in enumerate(fh):
        for key in row.keys():
          widths[key] = max(widths[key], len(row[key]))
        rows.append(row)
      # now print
      logging.info('writing %i rows...', idx + 1)
      out.write(delimiter.join([x.ljust(widths[x]) for x in fh.fieldnames])) # header
      out.write('\n')
      for row in rows:
        out.write(delimiter.join([row[x].ljust(widths[x]) for x in fh.fieldnames]))
        out.write('\n')
    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    parser.add_argument('--mode', default='', help='display mode (vertical, horizontal)')
    args = parser.parse_args()
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.delimiter, sys.stdout, args.mode)

if __name__ == '__main__':
    main()

