#!/usr/bin/env python
'''
  Mean-center and optionally standardize each specified column by subtracting the mean and dividing by the standard deviation.
'''

import argparse
import collections
import csv
import logging
import sys

import numpy

def main(delimiter, fh, out, cols, sd, prefix):
  logging.info('reading...')
  reader = csv.DictReader(fh, delimiter=delimiter)
  rows = []
  vals = collections.defaultdict(list)
  exclude = set()
  if cols is None:
    cols = reader.fieldnames
  else:
    # all cols should be in reader
    for c in cols:
      if c not in reader.fieldnames:
        logging.warning('column %s not in input', c)
  for idx, r in enumerate(reader): # each row
    rows.append(r)
    for v in cols:
      try:
        vals[v].append(float(r[v]))
      except:
        exclude.add(v)

  logging.info('excluding %s', exclude)
  logging.info('calculating...')
  means = {k: numpy.mean(vals[k]) for k in vals if k not in exclude}
  sds = {k: numpy.std(vals[k], ddof=1) for k in vals if k not in exclude}

  logging.info('writing...')
  if prefix is None:
    writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=reader.fieldnames)
  else:
    writer = csv.DictWriter(out, delimiter=delimiter, fieldnames=reader.fieldnames + ['{}{}'.format(prefix, col) for col in cols])
  writer.writeheader()
  for r in rows:
    for v in cols:
      if prefix is not None:
        target = '{}{}'.format(prefix, v)
      else:
        target = v
      if v in exclude:
        if prefix is not None:
          r[target] = r[v]
        continue
      val = float(r[v])
      if prefix is not None:
        target = '{}{}'.format(prefix, v)
      else:
        target = v
      r[target] = val - means[v]
      if sd and sds[v] > 0:
        r[target] /= sds[v]
    writer.writerow(r)
  logging.info('done...')
    
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Basic stats of specified columns')
  parser.add_argument('--delimiter', required=False, default=',', help='input files')
  parser.add_argument('--encoding', required=False, help='input files')
  parser.add_argument('--sd', action='store_true', help='also normalise sd')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  parser.add_argument('--quiet', action='store_true', help='more logging')
  parser.add_argument('--cols', required=False, nargs='+', help='cols to normalise')
  parser.add_argument('--prefix', required=False, help='create new columns with this prefix')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  elif args.quiet:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if args.encoding and "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)

  main(args.delimiter, sys.stdin, sys.stdout, args.cols, args.sd, args.prefix)
