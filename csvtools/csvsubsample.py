#!/usr/bin/env python
'''
  subsample a tsv
'''

import argparse
import logging
import random
import sys

def main(probability):
  logging.info('reading from stdin...')

  first = True
  total = written = 0
  for line in sys.stdin:
    if first:
      sys.stdout.write(line)
      first = False
    else:
      total += 1
      if random.random() < probability:
        sys.stdout.write(line)
        written += 1

  logging.info('done. wrote %i of %i records', written, total)

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Subsample tsv')
  parser.add_argument('--probability', required=False, type=float, default=1.0, help='tumour vcf')
  parser.add_argument('--verbose', action='store_true', help='more logging')
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
  else:
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)

  main(args.probability)
