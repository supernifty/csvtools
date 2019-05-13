#!/usr/bin/env python
'''
  filter out duplicate records by column name
'''

import argparse
import csv
import logging
import sys

def main(colnames, delimiter, fh, out):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=reader.fieldnames)
  writer.writeheader()
  output = {}
  count = 0
  for row in reader:
    key = '\t'.join([row[col] for col in colnames])
    output[key] = row # keep last matching
    count += 1

  logging.info('read %i. writing...', count)
  count = 0
  for key in sorted(output.keys()):
    writer.writerow(output[key])
    count += 1
  
  logging.info('done writing %i', count)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--columns', required=True, nargs='+', help='columns to use as index')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.columns, args.delimiter, sys.stdin, sys.stdout)
