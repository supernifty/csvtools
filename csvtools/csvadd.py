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
  logging.debug('%i rules', len(rules))
  fh = csv.DictReader(sys.stdin, delimiter=delimiter)
  out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames + [name])
  logging.debug('output fields: %s', out.fieldnames)
  out.writeheader()
  for idx, row in enumerate(fh):
    logging.debug('processing line %i...', idx)
    for rule in rules:
      cond, newval = rule.split(':')
      condname, condval = re.split('[<=>!%]', cond, maxsplit=1)
      op = cond[len(condname)]
      if op == '<' and row[condname] != '' and float(row[condname]) < float(condval):
        row[name] = newval
        logging.debug('added %s to %s with <', newval, name)
        break
      elif op == '>' and row[condname] != '' and float(row[condname]) > float(condval):
        row[name] = newval
        logging.debug('added %s to %s with >', newval, name)
        break
      elif op == '=' and row[condname] == condval:
        row[name] = newval
        logging.debug('added %s to %s with =', newval, name)
        break
      elif op == '!' and row[condname] != condval:
        row[name] = newval
        logging.debug('added %s to %s with !', newval, name)
        break
      elif op == '%' and condval in row[condname]:
        row[name] = newval
        logging.debug('added %s to %s with %', newval, name)
        break
    else:
      row[name] = value
      logging.debug('added %s to %s', value, name)
    out.writerow(row)
    if (idx + 1) % 1000 == 0:
      logging.debug('%i lines processed', idx + 1)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Add column to tsv')
  parser.add_argument('--name', required=True, help='col name')
  parser.add_argument('--value', required=False, default='', help='default col value')
  parser.add_argument('--rule', required=False, nargs='*', default=[], help='rule for value of the form col[<=>%%]val:colval')
  parser.add_argument('--delimiter', required=False, default=',', help='delimiter')
  parser.add_argument('--encoding', default='utf-8', help='file encoding')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  if "reconfigure" in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)
    logging.debug('encoding %s applied', args.encoding)
  else:
    logging.debug('using default encoding')
 
  main(args.name, args.value, args.delimiter, args.rule)
