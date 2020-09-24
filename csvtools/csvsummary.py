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

def main(colnames, delimiter, categorical, fh, out, groupcol):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  summary = collections.defaultdict(dict)
  groups = set()
  if categorical:
    for row in reader: # each row
      if groupcol is None:
        group_name = 'All'
      else:
        group_name = row[groupcol]
      groups.add(group_name)
      for col in colnames: # each column of interest
        if col not in summary:
          summary[group_name][col] = collections.defaultdict(int)
        summary[group_name][col][row[col]] += 1

    # summarise
    out.write('Group\tValue\tCount\n')
    for group in sorted(groups):
      for col in colnames:
        if len(colnames) > 1:
          out.write('* Column\t{}\n'.format(col))
        for key in sorted(summary[group][col].keys()):
          out.write('{}\t{}\t{}\n'.format(group, key, summary[group][col][key]))
        if len(colnames) > 1:
          out.write('=======\n')
  else:
    summary = collections.defaultdict(dict)
    for row in reader:
      if groupcol is None:
        group_name = 'All'
      else:
        group_name = row[groupcol]
      groups.add(group_name)
      for col in colnames:
        summary[group_name] = check(summary[group_name], col)
        if row[col] in ('nan', 'inf'):
          continue
        try:
          v = float(row[col])
        except:
          continue
        summary[group_name][col]['n'] += 1
        summary[group_name][col]['sum'] += v
        summary[group_name][col]['max'] = max(summary[group_name][col]['max'], v)
        summary[group_name][col]['min'] = min(summary[group_name][col]['min'], v)
        summary[group_name][col]['d'].append(v)
  
    # write summary
    out.write('group\tname\tn\ttotal\tmin\tmax\tmean\tsd\tmedian\n')
    for group in groups:
      for col in colnames:
        if summary[group][col]['n'] > 0:
          summary[group][col]['mean'] = summary[group][col]['sum'] / summary[group][col]['n']
  
          if summary[group][col]['n'] % 2 == 0:
            mid = int(summary[group][col]['n'] / 2)
            summary[group][col]['median'] = (summary[group][col]['d'][mid] + summary[group][col]['d'][mid - 1]) / 2
          else:
            mid = int((summary[group][col]['n'] - 1) / 2)
            summary[group][col]['median'] = summary[group][col]['d'][mid]
  
          if summary[group][col]['n'] > 1:
            summary[group][col]['sd'] = numpy.std(summary[group][col]['d'])
          else:
            summary[group][col]['sd'] = 0
          out.write('{}\t{}\t{}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\n'.format(group, col, summary[group][col]['n'], summary[group][col]['sum'], summary[group][col]['min'], summary[group][col]['max'], summary[group][col]['mean'], summary[group][col]['sd'], summary[group][col]['median']))
        else:
          out.write('{}\t{}\t0\t0\t-\t-\t-\t-\t-\n'.format(group_name, col))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--cols', '--columns', required=True, nargs='+', help='columns to summarise')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--group', required=False, help='column to group on')
  parser.add_argument('--categorical', action='store_true', help='data is categorical')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.cols, args.delimiter, args.categorical, sys.stdin, sys.stdout, args.group)
