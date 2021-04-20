#!/usr/bin/env python
'''
  map values in fields to new values
  python csvmap.py --mapfile fn --source_col --map_col_from --map_col_to < old.csv > new.csv
'''

import argparse
import collections
import csv
import logging
import sys

def process(fh, mapfile, delimiter, source_col, map_col_from, map_col_to):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''

    m = {}
    for row in csv.DictReader(open(mapfile, 'r'), delimiter=delimiter):
      m[row[map_col_from]] = row[map_col_to]

    logging.info('reading from stdin...')
    rfh = csv.DictReader(fh, delimiter=delimiter)
    wfh = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=rfh.fieldnames)
    wfh.writeheader()
    for row in rfh:
      row[source_col] = m.get(row[source_col], row[source_col])
      wfh.writerow(row)

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Update CSV column values')
    parser.add_argument('--mapfile', required=True, help='map csv')
    parser.add_argument('--source_col', required=True, help='map csv')
    parser.add_argument('--map_col_from', required=True, help='map csv')
    parser.add_argument('--map_col_to', required=True, help='map csv')
    parser.add_argument('--delimiter', default=',', help='file delimiter')
    args = parser.parse_args()
    process(sys.stdin, args.mapfile, args.delimiter, args.source_col, args.map_col_from, args.map_col_to)

if __name__ == '__main__':
    main()
