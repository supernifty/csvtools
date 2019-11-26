#!/usr/bin/env python
'''
  makes different columns into more rows
'''

import argparse
import csv
import logging
import re
import sys

def main(cols, targetname, targetvalue, delimiter):
  fh = csv.DictReader(sys.stdin, delimiter=delimiter)
  newcols = [x for x in fh.fieldnames if x not in cols] + [targetname, targetvalue]
  logging.debug(newcols)
  out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=newcols)
  out.writeheader()
  for row in fh:
    for oldcol in cols:
      newrow = {}
      for newcol in newcols:
        if newcol not in [targetname, targetvalue]:
          newrow[newcol] = row[newcol]
      # one row for each specified column
      logging.debug(cols)
      newrow[targetname] = oldcol
      newrow[targetvalue] = row[oldcol]
      out.writerow(newrow)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Add column to tsv')
  parser.add_argument('--cols', required=True, nargs='+', help='cols to remove')
  parser.add_argument('--targetname', required=True, help='new col name with value')
  parser.add_argument('--targetvalue', required=True, help='new col name with value')
  parser.add_argument('--delimiter', required=False, default=',', help='delimiter')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.cols, args.targetname, args.targetvalue, args.delimiter)
