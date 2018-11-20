#!/usr/bin/env python

import argparse
import logging
import sys

def main(name, value, delimiter):
  first = True
  for line in sys.stdin:
    if first:
      first = False
      sys.stdout.write('{}{}{}\n'.format(line.strip('\n'), delimiter, name))
      continue
    sys.stdout.write('{}{}{}\n'.format(line.strip('\n'), delimiter, value))

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Add column to tsv')
  parser.add_argument('--name', required=True, help='col name')
  parser.add_argument('--value', required=True, help='col value')
  parser.add_argument('--delimiter', required=False, default=',', help='delimiter')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.name, args.value, args.delimiter)
