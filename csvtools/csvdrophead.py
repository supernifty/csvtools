#!/usr/bin/env python
'''
  column based diff
'''

import argparse
import collections
import csv
import logging
import sys

def drop_leading(r):
  header = True
  for line in r:
    if header and line.startswith('##'):
      continue
    header = False
    yield line

def main(ifh, ofh):
  logging.info('reading stdin...')
  for line in drop_leading(ifh):
    ofh.write(line)
  logging.info('done')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Assess MSI')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(sys.stdin, sys.stdout)
