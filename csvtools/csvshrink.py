#!/usr/bin/env python
'''
  Reduce column values using Dirichlet shrinkage: combines observed values with a uniform prior using a shrinkage parameter.
'''

import argparse
import collections
import csv
import logging
import sys

def main(delimiter, fh, out, cols, n_col, k, prefix):
  logging.info('reading...')
  reader = csv.DictReader(fh, delimiter=delimiter)
  if cols is None:
    cols = reader.fieldnames
  else:
    # all cols should be in reader
    for c in cols:
      if c not in reader.fieldnames:
        logging.warning('column %s not in input', c)

  if prefix is None:
    writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=reader.fieldnames)
  else:
    writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=reader.fieldnames + ['{}{}'.format(prefix, col) for col in cols])
  writer.writeheader()

  prior = 1 / len(cols)
  for idx, r in enumerate(reader): # each row
    for c in cols: # cols to evaluate
      old_val = float(r[c])
      n = float(r[n_col])
      weight = n / (n + k)
      new_val = weight * old_val + (1 - weight) * prior
      if prefix is None:
        r[c] = new_val
      else:
        r['{}{}'.format(prefix, c)] = new_val
    writer.writerow(r)
  logging.info('done...')
    
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Basic shrinkage')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--encoding', required=False, help='input files')
  parser.add_argument('--cols', required=False, nargs='+', help='cols to shrink')
  parser.add_argument('--n_col', required=True, help='column with n')
  parser.add_argument('--k', required=True, type=int, help='k parameter for shrink')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--prefix', required=False, help='create new columns with this prefix')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if args.encoding and "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)

  main(args.delimiter, sys.stdin, sys.stdout, args.cols, args.n_col, args.k, args.prefix)
