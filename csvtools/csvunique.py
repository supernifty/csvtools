#!/usr/bin/env python
'''
  filter out duplicate records by column name
'''

import argparse
import collections
import csv
import logging
import sys

def main(colnames, delimiter, fh, out, duplicates, count_col):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  # remove duplicate columns
  if count_col is None:
    fieldnames = list(collections.OrderedDict.fromkeys(reader.fieldnames))
  else:
    fieldnames = list(collections.OrderedDict.fromkeys(reader.fieldnames)) + [count_col]
  writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=fieldnames)
  writer.writeheader()
  output = {}
  count = 0
  counts = collections.defaultdict(int)
  if duplicates is not None:
    duplicates_fh = open(duplicates, 'w')
  for row in reader:
    key = '\t'.join([row[col] for col in colnames])
    if key in output and duplicates is not None:
      result = [row[col] for col in reader.fieldnames]
      if None in result:
        logging.warn(result)
      duplicates_fh.write('{}\n'.format(delimiter.join([row[col] for col in reader.fieldnames])))
    output[key] = row # keep last matching
    counts[key] += 1
    if count < 10 or count % 100000 == 0:
      logging.debug('%i: %s', count, row)
    count += 1

  logging.info('read %i. writing...', count)
  count = 0
  for key in sorted(output.keys()):
    if count_col is not None:
      output[key][count_col] = counts[key]
    writer.writerow(output[key])
    count += 1
    if count < 10:
      logging.debug('key: %s value: %s', key, output[key])
  
  logging.info('done writing %i', count)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Filter to unique rows')
  parser.add_argument('--cols', required=True, nargs='+', help='columns to use as index')
  parser.add_argument('--count_col', required=False, help='column to write count')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--duplicates', required=False, help='write duplicates to file')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.cols, args.delimiter, sys.stdin, sys.stdout, args.duplicates, args.count_col)
