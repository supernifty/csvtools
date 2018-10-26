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

def process(fhs, keys, delimiter):
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
      key = row[key_pos]
      rows[key].update({headers[0][row_num]: row[row_num] for row_num in range(len(row))})

    logging.info('read %i lines', lines + 1)

    for key, fh, fh_pos in zip(keys[1:], fhs[1:], range(1, len(keys))):
      lines = 0
      for lines, row in enumerate(fh):
        key_pos = headers_map[fh_pos][key]
        if row[key_pos] in rows:
          rows[row[key_pos]].update({headers[fh_pos][row_num]: row[row_num] for row_num in range(len(row))})
        else:
          logging.debug('key %s not found on line %i', row[key_pos], lines + 1)
      logging.info('read %i lines', lines + 1)

    out = csv.writer(sys.stdout, delimiter=delimiter)
    out.writerow(out_headers)
    for lines, row in enumerate(rows.keys()):
      out_row = [rows[row].get(column, '') for column in out_headers]
      out.writerow(out_row)
        
    logging.info('wrote %i lines', lines + 2)

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Merge CSVs based on key')
    parser.add_argument('--keys', nargs='+', help='column names')
    parser.add_argument('--files', nargs='+', help='input files')
    parser.add_argument('--delimiter', required=False, default=',', help='input files')
    args = parser.parse_args()
    process([csv.reader(open(fn, 'r'), delimiter=args.delimiter) for fn in args.files], args.keys, args.delimiter)

if __name__ == '__main__':
    main()
