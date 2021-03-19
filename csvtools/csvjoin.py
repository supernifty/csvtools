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
import re
import sys

def process(fhs, keys, delimiter, inner, key_length, horizontal, left, key_match_up_to):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading %i files...', len(fhs))
    headers_map = []
    headers = []
    out_headers = []

    while len(keys) < len(fhs):
      keys.append(keys[-1])

    for file_num, (key, fh) in enumerate(zip(keys, fhs)):
      logging.debug('reading header of file %i with key %s...', file_num, key)
      header = next(fh)
      logging.debug('reading header of file %i: %s', file_num, header)
      if not horizontal or file_num == 0:
        out_headers = out_headers + header 
      else:
        out_headers = out_headers + [h for h in header if h not in out_headers] # don't include identical keys
      colmap = {name: pos for pos, name in enumerate(header)}
      headers_map.append(colmap)
      headers.append(header)
      for keyname in key.split(','):
        if keyname not in colmap:
          logging.warn('key %s not found in file %i', keyname, file_num)

    logging.debug(sorted(out_headers))

    # first file
    logging.info('reading first file...')
    rows = collections.defaultdict(list)
    extra = [] # items that don't match first file's keys
    lines = 0
    key_order = []
    for lines, row in enumerate(fhs[0]):
      if lines % 1000 == 0:
        logging.info('processed %i lines...', lines)
      key_pos = [headers_map[0][key] for key in keys[0].split(',')] # where are our key(s)
      logging.debug('key_pos is %s and there are %i columns', key_pos, len(row))
      if key_length is None:
        val = tuple([row[key] for key in key_pos])
      else:
        val = (row[key_pos[0]][:key_length],) # with key_pos we only support one key

      if key_match_up_to is not None:
        if '|' in key_match_up_to:
          logging.warn('| in key_match_up_to likely to cause trouble')
        val = tuple([re.split('|'.join(key_match_up_to), v)[0] for v in val])
        #val = tuple([v.split(key_match_up_to)[0] for v in val])

      if val not in key_order:
        key_order.append(val)

      # each line from the first file indexed on key value
      #logging.debug('adding key %s to headers %s', val, headers)
      rows[val].append({headers[0][row_num]: row[row_num] for row_num in range(len(row))})

    logging.info('read %i lines from first file', lines + 1)

    for key, fh, fh_pos in zip(keys[1:], fhs[1:], range(1, len(keys))): # each subsequent file and the index key
      lines = 0
      keys_seen = collections.defaultdict(int)
      logging.info('reading next file...')
      for lines, row in enumerate(fh): # each row in file of interest
        if lines % 1000 == 0:
          logging.info('processed %i lines...', lines)
          logging.debug('finding keys %s in header %s', key, headers_map[fh_pos])
        key_pos = [headers_map[fh_pos][keyname] for keyname in key.split(',')] # which column is the key in this file?
        if key_length is None:
          val_of_interest = tuple([row[keyname] for keyname in key_pos]) # what is the value of the index for this file?
        else:
          val_of_interest = (row[key_pos[0]][:key_length],)

        if key_match_up_to is not None:
          if '|' in key_match_up_to:
            logging.warn('| in key_match_up_to likely to cause trouble')
          val_of_interest = tuple([re.split('|'.join(key_match_up_to), v)[0] for v in val_of_interest])
          #val_of_interest = tuple([v.split(key_match_up_to)[0] for v in val_of_interest])

        logging.debug('val of interest is "%s"', val_of_interest)

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
              logging.debug('updating %s with %s: %s', item, val_of_interest, [row[row_num] for row_num in range(len(row))])
              item.update({headers[fh_pos][row_num]: row[row_num] for row_num in range(len(row))})
        else:
          logging.debug('key %s not found on line %i with column number %s', val_of_interest, lines + 1, key_pos)
          extra.append({headers[fh_pos][row_num]: row[row_num] for row_num in range(len(row))})
      logging.info('read %i lines', lines + 1)

    out = csv.writer(sys.stdout, delimiter=delimiter)
    out.writerow(out_headers)
    written = 0
    for lines, row_key in enumerate(key_order): # keep same order from first file #rows.keys()):
      for row in rows[row_key]:
        if inner and len(set(row)) != len(set(out_headers)):
          logging.debug('skipped line %i since not all files have matching records (%i columns vs %i expected)', lines + 1, len(row), len(out_headers))
          continue
        out_row = [row.get(column, '') for column in out_headers]
        out.writerow(out_row)
        written += 1
    # rows with keys not seen in first file
    if not left:
      for item in extra:
        if inner:
          continue
        out_row = [item.get(column, '') for column in out_headers]
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
    parser.add_argument('--key_match_up_to', nargs='+', required=False, help='match up to string')
    parser.add_argument('--files', nargs='+', help='input files')
    parser.add_argument('--delimiter', required=False, default=',', help='input files')
    parser.add_argument('--encoding', default='utf-8', help='file encoding')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    parser.add_argument('--inner', action='store_true', help='intersect')
    parser.add_argument('--left', action='store_true', help='keys seen in first file')
    parser.add_argument('--horizontal', action='store_true', help='add additionally found records as new columns')
    args = parser.parse_args()
    if args.verbose:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    process([csv.reader(open(fn, 'r', encoding=args.encoding), delimiter=args.delimiter) for fn in args.files], args.keys, args.delimiter, args.inner, args.key_length, args.horizontal, args.left, args.key_match_up_to)

if __name__ == '__main__':
    main()
