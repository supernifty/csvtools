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

def process(fhs, keys, delimiter, inner, key_length, horizontal):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading files...')
    headers_map = []
    headers = []
    out_headers = []

    for file_num, (key, fh) in enumerate(zip(keys, fhs)):
      header = next(fh)
      if file_num == 0:
        out_headers = out_headers + header 
      else:
        out_headers = out_headers + [h for h in header if h not in out_headers] # don't include identical keys
      colmap = {name: pos for pos, name in enumerate(header)}
      headers_map.append(colmap)
      headers.append(header)
      for keyname in key.split(','):
        if keyname not in colmap:
          logging.warn('key %s not found', keyname)

    logging.debug(sorted(out_headers))

    # first file
    rows = collections.defaultdict(list)
    lines = 0
    for lines, row in enumerate(fhs[0]):
      key_pos = [headers_map[0][key] for key in keys[0].split(',')]
      if key_length is None:
        val = tuple([row[key] for key in key_pos])
      else:
        val = (row[key_pos[0]][:key_length],) # with key_pos we only support one key
      # each line from the first file indexed on key value
      logging.debug('adding key %s', val)
      rows[val].append({headers[0][row_num]: row[row_num] for row_num in range(len(row))})

    logging.info('read %i lines', lines + 1)

    for key, fh, fh_pos in zip(keys[1:], fhs[1:], range(1, len(keys))): # each subsequent file and the index key
      lines = 0
      keys_seen = collections.defaultdict(int)
      for lines, row in enumerate(fh): # each row in file of interest
        key_pos = [headers_map[fh_pos][keyname] for keyname in key.split(',')] # which column is the key in this file?
        if key_length is None:
          val_of_interest = tuple([row[keyname] for keyname in key_pos]) # what is the value of the index for this file?
        else:
          val_of_interest = (row[key_pos[0]][:key_length],)
        if val_of_interest in rows:
          keys_seen[val_of_interest] += 1
          if keys_seen[val_of_interest] > 1:
            logging.debug('%s seen %i times', val_of_interest, keys_seen[val_of_interest])
          if horizontal:
            for item in rows[val_of_interest]:
              item.update({'{}_{}'.format(headers[fh_pos][row_num], keys_seen[val_of_interest]): row[row_num] for row_num in range(len(row))})
            # TODO this is inefficient
            for row_num in range(len(row)):
              if '{}_{}'.format(headers[fh_pos][row_num], keys_seen[val_of_interest]) not in out_headers:
                out_headers.append('{}_{}'.format(headers[fh_pos][row_num], keys_seen[val_of_interest]))
          else: # normal
            for item in rows[val_of_interest]:
              item.update({headers[fh_pos][row_num]: row[row_num] for row_num in range(len(row))})
        else:
          logging.debug('key %s not found on line %i with column number %s', val_of_interest, lines + 1, key_pos)
      logging.info('read %i lines', lines + 1)

    out = csv.writer(sys.stdout, delimiter=delimiter)
    out.writerow(out_headers)
    written = 0
    for lines, row_key in enumerate(rows.keys()):
      for row in rows[row_key]:
        if inner and len(row) != len(out_headers):
          logging.debug('skipped line %i since not all files have matching records (%i columns vs %i expected)', lines + 1, len(row), len(out_headers))
          continue
        out_row = [row.get(column, '') for column in out_headers]
        out.writerow(out_row)
        written += 1
        
    logging.info('wrote %i lines', written)

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Merge CSVs based on key')
    parser.add_argument('--keys', nargs='+', help='column names (comma separated for multiple keys)')
    parser.add_argument('--key_length', type=int, required=False, help='only match first part of keys')
    parser.add_argument('--files', nargs='+', help='input files')
    parser.add_argument('--delimiter', required=False, default=',', help='input files')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    parser.add_argument('--inner', action='store_true', help='intersect')
    parser.add_argument('--horizontal', action='store_true', help='add additionally found records as new columns')
    args = parser.parse_args()
    if args.verbose:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    process([csv.reader(open(fn, 'r'), delimiter=args.delimiter) for fn in args.files], args.keys, args.delimiter, args.inner, args.key_length, args.horizontal)

if __name__ == '__main__':
    main()
