#!/usr/bin/env python
'''
  summarise numerical columns
'''

import argparse
import collections
import csv
import logging
import sys

import numpy

def check(summary, col):
  if col not in summary:
    summary[col] = {'n': 0, 'sum': 0, 'max': sys.float_info.min, 'min': sys.float_info.max, 'd': []}
  return summary

def main(colnames, delimiter, categorical, fh, out):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  summary = {}
  if categorical:
    for row in reader:
      for col in colnames:
        if col not in summary:
          summary[col] = collections.defaultdict(int)
        summary[col][row[col]] += 1

    # summarise
    out.write('Value\tCount\n')
    for col in colnames:
      if len(colnames) > 1:
        out.write('* Column\t{}\n'.format(col))
      for key in sorted(summary[col].keys()):
        out.write('{}\t{}\n'.format(key, summary[col][key]))
      if len(colnames) > 1:
        out.write('=======\n')
  else:
    summary = {}
    for row in reader:
      for col in colnames:
        summary = check(summary, col)
        if row[col] in ('nan', 'inf'):
          continue
        try:
          v = float(row[col])
        except:
          continue
        summary[col]['n'] += 1
        summary[col]['sum'] += v
        summary[col]['max'] = max(summary[col]['max'], v)
        summary[col]['min'] = min(summary[col]['min'], v)
        summary[col]['d'].append(v)
  
    # write summary
    out.write('name\tn\ttotal\tmin\tmax\tmean\tsd\tmedian\n')
    for col in colnames:
      if summary[col]['n'] > 0:
        summary[col]['mean'] = summary[col]['sum'] / summary[col]['n']

        if summary[col]['n'] % 2 == 0:
          mid = int(summary[col]['n'] / 2)
          summary[col]['median'] = (summary[col]['d'][mid] + summary[col]['d'][mid - 1]) / 2
        else:
          mid = int((summary[col]['n'] - 1) / 2)

          summary[col]['median'] = summary[col]['d'][mid]
        if summary[col]['n'] > 1:
          summary[col]['sd'] = numpy.std(summary[col]['d'])
        else:
          summary[col]['sd'] = 0
        out.write('{}\t{}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\n'.format(col, summary[col]['n'], summary[col]['sum'], summary[col]['min'], summary[col]['max'], summary[col]['mean'], summary[col]['sd'], summary[col]['median']))
      else:
        out.write('{}\t0\t0\t-\t-\t-\t-\t-\n'.format(col))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--columns', required=True, nargs='+', help='columns to summarise')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--categorical', action='store_true', help='data is categorical')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.columns, args.delimiter, args.categorical, sys.stdin, sys.stdout)
