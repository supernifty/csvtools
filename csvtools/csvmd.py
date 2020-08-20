#!/usr/bin/env python
'''
  write as markdown compatible table
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
    first = True
    for idx, row in enumerate(fh):
      out.write('|{}|\n'.format('|'.join(row)))
      if first:
        out.write('|{}|\n'.format('|'.join('-' * len(row))))
        first = False
    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Filter CSV based on values')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    parser.add_argument('--verbose', action='store_true', default=False, help='more logging')
    parser.add_argument('--quiet', action='store_true', default=False, help='more logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    process(csv.reader(sys.stdin, delimiter=args.delimiter), args.delimiter, sys.stdout)

if __name__ == '__main__':
    main()


