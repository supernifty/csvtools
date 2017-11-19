#!/usr/bin/env python
'''
  merge csvs by including common column names
'''

import argparse
import csv
import logging
import sys

def process(csvs):
    '''
        read in each csv file, look at the header of each
        write out only columns that are in all csv files
    '''
    logging.info('merging %i files...', len(csvs))
    fhs = [csv.reader(open(filename, 'r')) for filename in csvs]
    headers_list = [next(fh) for fh in fhs]
    headers = [set(header) for header in headers_list]
    intersection = []
    for name in headers_list[0]: # to keep same order as first file
        if all([name in header for header in headers]):
            intersection.append(name)
    logging.info('including %i fields', len(intersection))
    # each file
    out = csv.writer(sys.stdout)
    out.writerow(intersection)
    for idx, handle in enumerate(fhs): # each file
        drop = headers[idx].difference(intersection)
        logging.info('processing %s: dropping %i columns: %s...',
                     csvs[idx],
                     len(drop),
                     ' '.join(list(drop)))
        lines = 0
        for lines, row in enumerate(handle):
            outline = []
            for val in intersection: # each colname to include
                outline.append(row[headers_list[idx].index(val)])
            out.writerow(outline)
        logging.info('processing %s: wrote %i lines', csvs[idx], lines + 1)

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Merge CSV files')
    parser.add_argument('csvs', nargs='+', help='csv files to merge')
    args = parser.parse_args()
    process(args.csvs)

if __name__ == '__main__':
    main()
