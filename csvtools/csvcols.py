#!/usr/bin/env python
'''
  filter on column names
'''

import argparse
import collections
import csv
import gzip
import logging
import sys

def get_fh(fh):
  c = fh.read(1)
  fh.seek(0)
  if ord(c) == 0x1f:
    return gzip.open(fh, 'rt')
  else:
    return fh

def process(fh, cols, exclude, exclude_ends_with, delimiter):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')
    out = csv.writer(sys.stdout, delimiter=delimiter)

    if not exclude:
      include = cols
      out.writerow(cols)

    lines = 0
    first = True
    for lines, row in enumerate(fh):
      if exclude and first:
        first = False
        include = []
        for colname in row.keys():
          if colname not in cols and (exclude_ends_with is None or not colname.endswith(exclude_ends_with)):
            include.append(colname)
            
        out.writerow(include)

      outrow = []
      for col in include:
        if col in row:
          outrow.append(row[col])
        else:
          outrow.append('')
      out.writerow(outrow)

    logging.info('read and wrote %i rows', lines + 1)

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Update CSV column values')
    parser.add_argument('--cols', required=True, nargs='+', help='columns to include')
    parser.add_argument('--exclude', action='store_true', help='exclude instead')
    parser.add_argument('--exclude_ends_with', required=False, help='additional exclude rule')
    parser.add_argument('--delimiter', default=',', help='file delimiter')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    parser.add_argument('--quiet', action='store_true', default=False, help='less logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    process(csv.DictReader(get_fh(sys.stdin.buffer), delimiter=args.delimiter), args.cols, args.exclude, args.exclude_ends_with, args.delimiter)

if __name__ == '__main__':
    main()
