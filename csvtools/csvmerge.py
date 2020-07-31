#!/usr/bin/env python
'''
  merge csvs by including common column names
'''

import argparse
import csv
import logging
import sys

def process(csvs, union, delimiter, default_value):
    '''
        read in each csv file, look at the header of each
        write out only columns that are in all csv files
    '''
    logging.info('merging %i files...', len(csvs))
    fhs = [csv.reader(open(filename, 'r'), delimiter=delimiter) for filename in csvs]
    headers_list = [next(fh) for fh in fhs] # column names for each csv
    headers = [set(header) for header in headers_list]
    intersection = []
    for name in headers_list[0]: # to keep same order as first file (each column from first file)
        if all([name in header for header in headers]):
            intersection.append(name)

    union_cols = list(set.union(*headers))

    if union:
      output_cols = union_cols
    else:
      output_cols = intersection

    logging.info('including %i fields', len(output_cols))
    # each file
    out = csv.writer(sys.stdout, delimiter=delimiter)
    out.writerow(output_cols)
    for idx, handle in enumerate(fhs): # each file
        drop = headers[idx].difference(output_cols)
        logging.info('processing %s: dropping %i columns: %s...',
                     csvs[idx],
                     len(drop),
                     ' '.join(list(drop)))
        lines = 0
        for lines, row in enumerate(handle):
            if len(row) == 0:
              logging.warn('processing %s: empty row. continuing...', csvs[idx])
              break
            outline = []
            for val in output_cols: # each colname to include
                if val in headers_list[idx]:
                  outline.append(row[headers_list[idx].index(val)])
                else:
                  outline.append(default_value) # no value
            out.writerow(outline)
        logging.info('processing %s: wrote %i lines', csvs[idx], lines + 1)

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Merge CSV files')
    parser.add_argument('csvs', nargs='+', help='csv files to merge')
    parser.add_argument('--union', default=False, action='store_true', help='keep all columns')
    parser.add_argument('--delimiter', required=False, default=',', help='input file delimiter')
    parser.add_argument('--default', required=False, default='', help='default value for missing values')
    parser.add_argument('--verbose', action='store_true', help='more logging')
    args = parser.parse_args()
    if args.verbose:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    else:
      logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    args = parser.parse_args()
    process(args.csvs, args.union, args.delimiter, args.default)

if __name__ == '__main__':
    main()
