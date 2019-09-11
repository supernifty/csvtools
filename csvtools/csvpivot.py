#!/usr/bin/env python
'''
  pivot around a column
'''

import argparse
import collections
import csv
import logging
import sys

def process(fh, pivot, delimiter):
    '''
        read in csv file, look at the header of each
    '''
    logging.info('reading from stdin...')
    newcols = ['Column']
    newrows = [{} for _ in range(len(fh.fieldnames))] # one row for each fieldname
    logging.debug(newrows)

    for idx, col in enumerate(fh.fieldnames): # each column name e.g. Sample Tags AF
      newrows[idx]['Column'] = col # set column name

    for row in fh: # for each row, we add a column to newrows
      newcols.append(row[pivot])
      for idx, col in enumerate(fh.fieldnames): # each column name e.g. Sample Tags AF
        if col != pivot:
          newrows[idx][row[pivot]] = row[col] # set column name

    logging.info('writing to stdout...')
    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=newcols)
    out.writeheader()
    for row in newrows:
      # skip pivot
      if row['Column'] == pivot:
        continue
      out.writerow(row)
    logging.info('done')

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Update CSV column values')
    parser.add_argument('--delimiter', default=',', help='file delimiter')
    parser.add_argument('--pivot', help='column to become header')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.pivot, args.delimiter)

if __name__ == '__main__':
    main()
