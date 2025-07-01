#!/usr/bin/env python
'''
  filter rows
'''

import argparse
import collections
import csv
import logging
import re
import sys

def rule_succeeded(out, row, exclude):
  logging.debug('entering rule_succeeded with exclude=%s for row=%s', exclude, row)
  if not exclude:
    out.writerow(row)

def process(fh, delimiter, grep=None):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')

    if grep is None:
      grep = []
    else:
      grep = [re.compile(g) for g in grep]

    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames)
    out.writeheader()
    lines = passed = 0

    skipped = collections.defaultdict(int)
    for lines, row in enumerate(fh):
        # check each rule for a fail
        ok = True
        done = False # for any_filter

        # check grep
        if grep:
          grep_ok = False
          for g in grep:
            if any(g.search(v) for v in row.values()):
              grep_ok = True
              break
          if not grep_ok:
            logging.debug('skipped row %i for not matching grep', lines)
            continue

        # check lines
        logging.debug('processing %i: %s', lines, row)

        if grep_ok:
           rule_succeeded(out, row, False)
           passed += 1

        if lines % 100000 == 0:
          logging.info('%i lines processed, wrote %i. last row read: %s...', lines, passed, row)

    logging.info('wrote %i of %i', passed, lines + 1)

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Filter rows')
    parser.add_argument('grep', nargs='+', help='regular expression to match anywhere in row')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    parser.add_argument('--encoding', default='utf-8', help='file encoding')
    parser.add_argument('--verbose', action='store_true', default=False, help='more logging')
    parser.add_argument('--quiet', action='store_true', default=False, help='less logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    if "reconfigure" in dir(sys.stdin):
      sys.stdin.reconfigure(encoding=args.encoding)
      logging.debug('encoding %s applied', args.encoding)
    else:
      logging.debug('using default encoding')
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.delimiter, args.grep)

if __name__ == '__main__':
    main()
