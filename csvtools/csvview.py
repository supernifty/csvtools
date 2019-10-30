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

def process(fh, delimiter, out):
    '''
      apply operation and write to dest
    '''
    logging.info('reading from stdin...')
    for idx, row in enumerate(fh):
      out.write('Row\t{}\n'.format(idx + 1))
      for key in sorted(row.keys()):
        out.write('{}\t{}\n'.format(key, row[key]))
      out.write('\n')

    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    args = parser.parse_args()
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.delimiter, sys.stdout)

if __name__ == '__main__':
    main()

