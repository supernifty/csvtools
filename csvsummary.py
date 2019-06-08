#!/usr/bin/env python
'''
  summarise numerical columns
'''

import argparse
import csv
import logging
import sys

def check(summary, col):
  if col not in summary:
    summary[col] = {'n': 0, 'sum': 0, 'max': sys.float_info.min, 'min': sys.float_info.max}
  return summary

def main(colnames, delimiter, fh, out):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  summary = {}
  count = 0
  for row in reader:
    for col in colnames:
      summary = check(summary, col)
      try:
        v = float(row[col])
      except:
        continue
      summary[col]['n'] += 1
      summary[col]['sum'] += v
      summary[col]['max'] = max(summary[col]['max'], v)
      summary[col]['min'] = min(summary[col]['min'], v)

  # write summary
  out.write('name\tn\ttotal\tmin\tmax\tmean\n')
  for col in colnames:
    if summary[col]['n'] > 0:
      summary[col]['mean'] = summary[col]['sum'] / summary[col]['n']
      out.write('{}\t{}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\n'.format(col, summary[col]['n'], summary[col]['sum'], summary[col]['min'], summary[col]['max'], summary[col]['mean']))
    else:
      out.write('{}\t0\t0\t-\t-\t-\n'.format(col))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--columns', required=True, nargs='+', help='columns to summarise')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.columns, args.delimiter, sys.stdin, sys.stdout)
