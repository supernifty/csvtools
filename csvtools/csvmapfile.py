#!/usr/bin/env python
'''
  Map values in a specified column using a provided mapping file.
  The mapping file should contain columns indicating the source and target values; the tool applies the mapping to each row read from stdin.
'''

import argparse
import collections
import csv
import logging
import sys

def process(fh, mapfile, delimiter, source_col, map_col_from, map_col_to, target_col, not_found):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''

    m = {}
    for row in csv.DictReader(open(mapfile, 'r'), delimiter=delimiter):
      m[row[map_col_from]] = row[map_col_to]

    rfh = csv.DictReader(fh, delimiter=delimiter)
    if target_col is None:
      wfh = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=rfh.fieldnames)
      target_col = source_col
    else:
      wfh = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=rfh.fieldnames + [target_col])
    wfh.writeheader()
    logging.info('reading from stdin and adding %s...', target_col)
    for row in rfh:
      if not_found is None:
        row[target_col] = m.get(row[source_col], row[source_col])
      else:
        row[target_col] = m.get(row[source_col], not_found)
      wfh.writerow(row)

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Update CSV column values')
    parser.add_argument('--mapfile', required=True, help='map csv')
    parser.add_argument('--source_col', required=True, help='column to map')
    parser.add_argument('--target_col', required=False, help='column to add')
    parser.add_argument('--map_col_from', required=True, help='mapfile column')
    parser.add_argument('--map_col_to', required=True, help='mapfile column')
    parser.add_argument('--not_found', help='marker if no mapping')
    parser.add_argument('--delimiter', default=',', help='file delimiter')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    args = parser.parse_args()
    if args.verbose:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    args = parser.parse_args()
    process(sys.stdin, args.mapfile, args.delimiter, args.source_col, args.map_col_from, args.map_col_to, args.target_col, args.not_found)

if __name__ == '__main__':
    main()
