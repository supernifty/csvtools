#!/usr/bin/env python
'''
  adds a new column with specified value
'''

import argparse
import csv
import logging
import re
import sys

def main(name, value, delimiter, rules):
  fh = csv.DictReader(sys.stdin, delimiter=delimiter)
  out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames + [name])
  out.writeheader()
  for row in fh:
    for rule in rules:
      cond, newval = rule.split(':')
      condname, condval = re.split('[<=>]', cond)
      op = cond[len(condname)]
      if op == '<' and float(row[condname]) < float(condval):
        row[name] = newval
        break
      elif op == '>' and float(row[condname]) > float(condval):
        row[name] = newval
        break
      elif op == '=' and row[condname] == condval:
        row[name] = newval
        break
    else:
      row[name] = value
    out.writerow(row)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Add column to tsv')
  parser.add_argument('--name', required=True, help='col name')
  parser.add_argument('--value', required=False, default='', help='default col value')
  parser.add_argument('--rule', required=False, nargs='*', default=[], help='rule for value of the form col[<=>]val:colval')
  parser.add_argument('--delimiter', required=False, default=',', help='delimiter')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.name, args.value, args.delimiter, args.rule)
