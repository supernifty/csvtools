#!/usr/bin/env python
'''
  converts a table into a 2-column output
'''

import argparse
import collections
import csv
import logging
import sys

import numpy

def main(delimiter, fh, out, key):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  out.write('Key\tValue\n')
  for row in reader:
    for col in reader.fieldnames:
      if col != key:
        out.write('{}_{}{}{}\n'.format(row[key], col, delimiter, row[col]))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--key', required=True, help='key to include in new key')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.delimiter, sys.stdin, sys.stdout, args.key)
