#!/usr/bin/env python
'''
  filter rows
'''

import argparse
import collections
import csv
import logging
import sys

def process(fh, filters, delimiter):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')

    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames)
    out.writeheader()
    lines = written = 0

    rules = collections.defaultdict(set)
    for rule in filters:
      colname, value = rule.split('=')
      rules[colname].add(value)

    logging.info('affected columns: %s', ' '.join(rules.keys()))
    
    skipped = collections.defaultdict(int)
    for lines, row in enumerate(fh):
        # check each rule
        ok = True
        for rule in rules:
          if row[rule] not in rules[rule]:
            ok = False
            skipped[rule] += 1
            break
        if ok:
            out.writerow(row)
            written += 1

    logging.info('wrote %i of %i', written, lines + 1)
    logging.info('filtered: %s', ' '.join(['{}: {}'.format(key, skipped[key]) for key in skipped]))

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Update CSV column values')
    parser.add_argument('--filters', nargs='+', help='colname=valname')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    args = parser.parse_args()
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.filters, args.delimiter)

if __name__ == '__main__':
    main()
