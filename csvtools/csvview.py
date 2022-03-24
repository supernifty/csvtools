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

def process(fh, delimiter, out, mode, maxlen=1e6):
    '''
      apply operation and write to dest
    '''
    logging.info('csvview: reading from stdin...')
    if mode == 'vertical':
      for idx, row in enumerate(fh):
        out.write('Row\t{}\n'.format(idx + 1))
        for key in sorted([x for x in row.keys() if x is not None]):
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
          widths[key] = min(maxlen, max(widths[key], len(row[key])))
          if len(row[key]) > widths[key]:
            row[key] = row[key][:widths[key]]
        rows.append(row)
      # now print
      logging.info('writing %i rows...', idx + 1)
      out.write(' '.join([x.ljust(widths[x]) for x in fh.fieldnames])) # header
      out.write('\n')
      for row in rows:
        out.write(' '.join([row[x].ljust(widths[x]) for x in fh.fieldnames]))
        out.write('\n')
    else:
      logging.warn('unrecognized mode %s', mode)
    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    parser.add_argument('--mode', default='vertical', help='display mode (vertical, horizontal)')
    parser.add_argument('--maxlen', required=False, type=int, default=1e6, help='max len of any column')
    parser.add_argument('--quiet', action='store_true', default=False, help='less logging')
    parser.add_argument('--verbose', action='store_true', default=False, help='more logging')
    args = parser.parse_args()
    if args.verbose:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    elif args.quiet:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARNING)
    else:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.delimiter, sys.stdout, args.mode, args.maxlen)

if __name__ == '__main__':
    main()

