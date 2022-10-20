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
import scipy.stats

def check(summary, col):
  if col not in summary:
    summary[col] = {'n': 0, 'sum': 0, 'max': sys.float_info.min, 'min': sys.float_info.max, 'd': []}
  return summary

def main(colnames, delimiter, categorical, fh, out, groupcols, population_sd, percentiles, just_write, output_format, pvalue):
  logging.info('starting...')

  reader = csv.DictReader(fh, delimiter=delimiter)
  summary = collections.defaultdict(dict)
  groups = set()
  if categorical:
    for row in reader: # each row
      if groupcols is None:
        group_name = 'All'
      else:
        group_name = tuple([row[groupcol] for groupcol in groupcols])
      groups.add(group_name)
      for col in colnames: # each column of interest
        if col not in summary[group_name]:
          summary[group_name][col] = collections.defaultdict(int)
        summary[group_name][col][row[col]] += 1
        #logging.debug('added to group %s col %s with value %s', group_name, col, row[col])

    # finished reading

    # summarise
    if output_format == 'tabular':
      # want to have....
      # group col1_val1 col1_val2...
      # x %...
      # builld list of colnames
      fieldnames = []
      colkeys = collections.defaultdict(set)
      for group in sorted(groups): # each unique group
        for col in colnames: 
          for key in summary[group][col].keys():
            colkeys[col].add(key)
            if '{}_{}'.format(col, key) not in fieldnames:
              fieldnames.append('{}_{}'.format(col, key))
      ofh = csv.DictWriter(out, delimiter=delimiter, fieldnames=['Group'] + sorted(fieldnames))
      ofh.writeheader()

      pvalues = {}
      if pvalue: # pvalue across groups (chi-square)
        # figure out observed and expected
        for col in colnames:
          observed = []
          expected = []
          for group in sorted(groups):
            observed.extend([summary[group][col][x] for x in sorted(colkeys[col])])
            total_for_group = sum([summary[group][col][x] for x in sorted(colkeys[col])])
            total_for_each_key = [sum([summary[x][col][key] for x in groups]) for key in sorted(colkeys[col])]
            total = sum(total_for_each_key)
            expected.extend([total_for_group * x / total for x in total_for_each_key])
          dof = (len(groups) - 1) * (len(colkeys[col]) - 1) # correct dof
          ddof = len(observed) - 1 - dof
          pvalues[col] = scipy.stats.chisquare(observed, expected, ddof)[1]
          logging.debug('pvalue for %s is %f from observed %s expected %s dof %i ddof %i', col, pvalues[col], observed, expected, dof, ddof)

      for group in sorted(groups): # each unique group
        row = {'Group': group}
        for col in colnames: # each column
          total = sum([summary[group][col][x] for x in summary[group][col]])
          for key in summary[group][col].keys():
            row['{}_{}'.format(col, key)] = '{} ({:.2f}%)'.format(summary[group][col][key], 100 * summary[group][col][key] / total)
        ofh.writerow(row)
      
      if pvalue:
        row = {'Group': 'pvalue'}
        for col in colnames:
          for key in colkeys[col]:
            row['{}_{}'.format(col, key)] = pvalues[col]
        ofh.writerow(row)

    else:
      out.write('Group\tValue\tCount\tPct\n')
      logging.debug('%i groups', len(groups))
      for group in sorted(groups):
        logging.debug('%i columns', len(colnames))
        for col in colnames:
          if len(colnames) > 1:
            out.write('* Column\t{}\n'.format(col))
          logging.debug('%i distinct values', len(summary[group][col].keys()))
          total = sum([summary[group][col][x] for x in summary[group][col]])
          for key in sorted(summary[group][col].keys()):
            out.write('{}\t{}\t{}\t{:.6f}\n'.format(','.join(group), key, summary[group][col][key], summary[group][col][key] / total))
          if len(colnames) > 1:
            out.write('=======\n')
  else: # numeric
    summary = collections.defaultdict(dict)
    for row in reader:
      if groupcols is None:
        group_name = 'All'
      else:
        group_name = tuple([row[groupcol] for groupcol in groupcols])
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

    if output_format == 'tabular':
      # want to have....
      # group col1_val1 col1_val2...
      # x %...
      # builld list of colnames
      ofh = csv.DictWriter(out, delimiter=delimiter, fieldnames=['Group'] + sorted(colnames))
      ofh.writeheader()
      for group in groups:
        row = {'Group': group}
        for col in colnames:
          if summary[group][col]['n'] > 0:
            row[col] = '{:.3f} ({:.3f})'.format(summary[group][col]['sum'] / summary[group][col]['n'], numpy.std(summary[group][col]['d'], ddof=1))
          else:
            row[col] = '-'
        ofh.writerow(row)

      if pvalue:
        pvalues = {}
        tests = {}
        for col in colnames:
          if len(groups) == 2: # t-test
            ds = []
            for g in summary:
              ds.append(summary[g][col]['d'])
            logging.debug('ttest on %s vs %s', ds[0], ds[1])
            pvalues[col] = scipy.stats.ttest_ind(ds[0], ds[1]).pvalue
            tests[col] = 'ttest'
          elif len(groups) > 2: # anova
            ds = []
            for g in summary:
              ds.append(summary[g][col]['d'])
            logging.debug('anova on %s', ds)
            pvalues[col] = scipy.stats.f_oneway(*ds).pvalue
            tests[col] = 'anova'
          else:
            pvalues[col] = -1
            tests[col] = 'none'

        logging.debug('pvalues are %s', pvalues)
        pvalues['Group'] = 'pvalue'
        ofh.writerow(pvalues)
        tests['Group'] = 'test'
        ofh.writerow(tests)

    else: # old style
      # write summary
      if percentiles is None:
        percentiles = []
      if just_write is None:
        out.write('group\tname\tn\ttotal\tmin\tmax\tmean\tsd\tmedian{}\n'.format(''.join(['\tpercentile_{}'.format(x) for x in percentiles])))
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
              if population_sd:
                summary[group][col]['sd'] = numpy.std(summary[group][col]['d'], ddof=0)
              else:
                summary[group][col]['sd'] = numpy.std(summary[group][col]['d'], ddof=1)
            else:
              summary[group][col]['sd'] = 0
            percentile_results = numpy.percentile(summary[group][col]['d'], percentiles)
            if just_write is None:
              out.write('{}\t{}\t{}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}\t{:.3f}{}\n'.format(group, col, summary[group][col]['n'], summary[group][col]['sum'], summary[group][col]['min'], summary[group][col]['max'], summary[group][col]['mean'], summary[group][col]['sd'], summary[group][col]['median'], ''.join(['\t{:.3f}'.format(x) for x in percentile_results])))
            else:
              out.write('{}\n'.format(summary[group][col][just_write]))
          else:
            out.write('{}\t{}\t0\t0\t-\t-\t-\t-\t-\n'.format(group_name, col))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Basic stats of specified columns')
  parser.add_argument('--cols', '--columns', required=True, nargs='+', help='columns to summarise')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--group', required=False, nargs='+', help='column to group on')
  parser.add_argument('--categorical', action='store_true', help='data is categorical')
  parser.add_argument('--population_sd', action='store_true', help='use population sd')
  parser.add_argument('--percentiles', required=False, nargs='+', type=float, help='percentiles to calculate')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--encoding', default='utf-8', help='file encoding')
  parser.add_argument('--just_write', required=False, help='only write this field value')
  parser.add_argument('--output_format', required=False, help='options: tabular')
  parser.add_argument('--pvalue', action='store_true', help='calculate pvalue')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)
  main(args.cols, args.delimiter, args.categorical, sys.stdin, sys.stdout, args.group, args.population_sd, args.percentiles, args.just_write, args.output_format, args.pvalue)
