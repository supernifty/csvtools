#!/usr/bin/env python
'''
  Calculate a new column based on mapping existing column values.
  This tool reads a CSV from stdin, uses provided source and destination value lists, and appends a new column with the computed result.
'''

import argparse
import collections
import csv
import logging
import sys

def process(fh, src_col, src_vals, dest_col, dest_vals, default, delimiter):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')
    headers = next(fh)
    colmap = {name: pos for pos, name in enumerate(headers)}

    if src_col not in colmap:
      logging.fatal('Column %s not found in header', src_col)

    valmap = {src: dest for src, dest in zip(src_vals, dest_vals)}

    out = csv.writer(sys.stdout, delimiter=delimiter)
    headers.append(dest_col)
    out.writerow(headers)

    lines = 0
    counts = collections.defaultdict(int)

    for lines, row in enumerate(fh):
        if row[colmap[src_col]] in valmap:
          dest_val = valmap[row[colmap[src_col]]]
          logging.debug('%s -> %s', row[colmap[src_col]], dest_val)
          counts[dest_val] += 1
        else:
          dest_val = default
          logging.debug('Value "%s" is unmatched', row[colmap[src_col]])
          counts['unmatched'] += 1
        row.append(dest_val)
        out.writerow(row)

    logging.info('wrote %i lines. new values: %s.', lines + 1, ', '.join(['{}: {}'.format(key, counts[key]) for key in counts]))

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Update CSV column values')
    parser.add_argument('--src_col', required=True, help='column to take values from')
    parser.add_argument('--src_vals', nargs='+', help='existing value')
    parser.add_argument('--dest_col', required=True, help='column to take values from')
    parser.add_argument('--dest_vals', nargs='+', help='existing value')
    parser.add_argument('--default', default='', help='default value if no match')
    parser.add_argument('--delimiter', default=',', help='file delimiter')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

    process(csv.reader(sys.stdin, delimiter=args.delimiter), args.src_col, args.src_vals, args.dest_col, args.dest_vals, args.default, args.delimiter)

if __name__ == '__main__':
    main()
