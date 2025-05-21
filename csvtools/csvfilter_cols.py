#!/usr/bin/env python
'''
  keep cols matching a rule
'''

import argparse
import collections
import csv
import logging
import sys

def main(delimiter, ifh, ofh, minval, keep):
  logging.info('starting...')
  if keep is None:
    keep = set()
  else:
    keep = set(keep)
  idr = csv.DictReader(ifh, delimiter=delimiter)
  logging.info('considering %i columns, keeping %i', len(idr.fieldnames), len(keep))
  d = []
  for r in idr:
    d.append(r)
    for c in r:
      if c in keep:
        continue
      if minval is not None:
        try:
          if float(r[c]) >= minval:
            keep.add(c)
        except:
          pass

  logging.info('writing %i columns', len(keep))
  odw = csv.DictWriter(ofh, delimiter='\t', fieldnames=list(keep))
  odw.writeheader()
  for r in d:
    odw.writerow({k: r[k] for k in keep})
  logging.info('done')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--min', type=float, required=True, help='at least one value of at least this value')
  parser.add_argument('--keep', nargs='+', required=False, help='always keep these columns')
  parser.add_argument('--delimiter', default=',', help='csv delimiter')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.delimiter, sys.stdin, sys.stdout, args.min, args.keep)
