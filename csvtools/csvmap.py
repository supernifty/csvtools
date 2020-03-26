#!/usr/bin/env python
'''
  map values in fields to new values
  python csvmap.py --map fieldname,oldvalue,newvalue < old.csv > new.csv
  e.g.
  python csvmap.py --map type,0,notfound type,1,found < old.csv > new.csv
'''

import argparse
import collections
import csv
import logging
import sys

def process(fh, rules, delimiter):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')
    headers = next(fh)
    colmap = {name: pos for pos, name in enumerate(headers)}

    out = csv.writer(sys.stdout, delimiter=delimiter)
    out.writerow(headers)
    matched = collections.defaultdict(int)
    lines = 0
    for lines, row in enumerate(fh):
        for rule in rules:
            colname, oldvalue, newvalue = rule.split(',')
            if row[colmap[colname]] == oldvalue:
                matched[colname] += 1
                row[colmap[colname]] = newvalue
        out.writerow(row)
        
    logging.info('wrote %i lines', lines + 1)
    logging.info('columns updated: {}'.format(', '.join(['{}: {}'.format(k, matched[k]) for k in sorted(matched.keys())])))

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Update CSV column values')
    parser.add_argument('--map', nargs='+', help='rules to apply to data of the form fieldname,oldvalue,newvalue')
    parser.add_argument('--delimiter', default=',', help='file delimiter')
    args = parser.parse_args()
    process(csv.reader(sys.stdin, delimiter=args.delimiter), args.map, args.delimiter)

if __name__ == '__main__':
    main()
