#!/usr/bin/env python
'''
  combine csvs with matching column value
  python csvjoin.py --keys col1 col2 --files file1.csv file2.csv > new.csv
  e.g.
  python csvjoin.py --keys key key2 --files test/3.csv test/4.csv > new.csv
'''

import argparse
import collections
import csv
import logging
import sys

def process(fhs, keys, delimiter, inner, key_length):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading files...')
    headers_map = []
    headers = []
    out_headers = []
    for key, fh in zip(keys, fhs):
      header = next(fh)
      out_headers = out_headers + header
      colmap = {name: pos for pos, name in enumerate(header)}
      headers_map.append(colmap)
      headers.append(header)
      if key not in colmap:
        logging.warn('key %s not found', key)

    rows = collections.defaultdict(dict)
    lines = 0
    for lines, row in enumerate(fhs[0]):
      key_pos = headers_map[0][keys[0]]
      if key_length is None:
        key = row[key_pos]
      else:
        key = row[key_pos][:key_length]
      rows[key].update({headers[0][row_num]: row[row_num] for row_num in range(len(row))})

    logging.info('read %i lines', lines + 1)

    for key, fh, fh_pos in zip(keys[1:], fhs[1:], range(1, len(keys))): # each subsequent file
      lines = 0
      for lines, row in enumerate(fh):
        key_pos = headers_map[fh_pos][key] # which column is the key?
        if key_length is None:
          key_of_interest = row[key_pos]
        else:
          key_of_interest = row[key_pos][:key_length]
        if key_of_interest in rows:
          rows[key_of_interest].update({headers[fh_pos][row_num]: row[row_num] for row_num in range(len(row))})
        else:
          logging.debug('key %s not found on line %i', row[key_pos], lines + 1)
      logging.info('read %i lines', lines + 1)

    out = csv.writer(sys.stdout, delimiter=delimiter)
    out.writerow(out_headers)
    written = 0
    for lines, row in enumerate(rows.keys()):
      if inner and len(rows[row]) != len(out_headers):
        logging.debug('skipped line %i since not all files have matching records', lines + 1)
        continue
      out_row = [rows[row].get(column, '') for column in out_headers]
      out.writerow(out_row)
      written += 1
        
    logging.info('wrote %i lines', written)

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Merge CSVs based on key')
    parser.add_argument('--keys', nargs='+', help='column names')
    parser.add_argument('--key_length', type=int, required=False, help='only match first part of keys')
    parser.add_argument('--files', nargs='+', help='input files')
    parser.add_argument('--delimiter', required=False, default=',', help='input files')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    parser.add_argument('--inner', action='store_true', help='intersect')
    args = parser.parse_args()
    if args.verbose:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    process([csv.reader(open(fn, 'r'), delimiter=args.delimiter) for fn in args.files], args.keys, args.delimiter, args.inner, args.key_length)

if __name__ == '__main__':
    main()
