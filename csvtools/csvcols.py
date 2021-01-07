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
  try:
    c = fh.read(1)
    fh.seek(0)
    if ord(c) == 0x1f:
      return gzip.open(fh, 'rt')
    else:
      return fh
  except:
    return sys.stdin

def process(fh, cols, exclude, exclude_ends_with, delimiter, unique, rename_in):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('csvcols: reading from stdin...')
    out = csv.writer(sys.stdout, delimiter=delimiter)

    rename = {}
    if rename_in is not None:
      for xy in rename_in:
        newname, oldname = xy.split('=')
        rename[oldname] = newname

    if not exclude: # include specified
      if cols is None:
        include = fh.fieldnames
      else:
        include = cols
      logging.debug('csvcols: new header is %s', cols)
    else: # exclude
      include = []
      for colname in fh.fieldnames:
        if colname not in cols and (exclude_ends_with is None or not colname.endswith(exclude_ends_with)):
          include.append(colname)
            
      logging.debug('csvcols: new header is %s', include)

    if unique:
      include = [include[x] for x in range(len(include)) if include[x] not in include[0:x]]
      logging.debug('csvcols: new header is %s', include)

    out.writerow([rename.get(x, x) for x in include]) # write header

    lines = 0
    for lines, row in enumerate(fh):
      outrow = []
      for col in include:
        if col in row:
          outrow.append(row[col])
        else:
          outrow.append('')
      out.writerow(outrow)

    logging.info('csvcols: read and wrote %i rows', lines + 1)

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Filter column names')
    parser.add_argument('--cols', required=False, nargs='+', help='columns to include')
    parser.add_argument('--exclude', action='store_true', help='exclude instead')
    parser.add_argument('--exclude_ends_with', required=False, help='additional exclude rule')
    parser.add_argument('--unique', action='store_true', help='remove duplicate columns')
    parser.add_argument('--rename', required=False, nargs='+', help='rename columns newname=oldname...')
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

    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.cols, args.exclude, args.exclude_ends_with, args.delimiter, args.unique, args.rename)

if __name__ == '__main__':
    main()
