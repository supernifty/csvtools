#!/usr/bin/env python
'''
  filter rows
'''

import argparse
import collections
import csv
import logging
import sys

def process(fh, filters, delimiter):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')

    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames)
    out.writeheader()
    lines = written = 0

    eq = collections.defaultdict(set) # equal to rule
    lt = collections.defaultdict(float)
    gt = collections.defaultdict(float)
    ne = collections.defaultdict(set)
    for rule in filters:
      if '=' in rule:
        colname, value = rule.split('=')
        eq[colname].add(value)
      if '!' in rule:
        colname, value = rule.split('!')
        ne[colname].add(value)
      if '<' in rule:
        colname, value = rule.split('<')
        lt[colname] = float(value)
      if '>' in rule:
        colname, value = rule.split('>')
        gt[colname] = float(value)

    logging.info('affected columns: %s; %s; %s; %s', ' '.join(eq.keys()), ' '.join(lt.keys()), ' '.join(gt.keys()), ' '.join(ne.keys()))
    
    skipped = collections.defaultdict(int)
    for lines, row in enumerate(fh):
        # check each rule
        ok = True
        for rule in eq: # each colname in rules
          if row[rule] not in eq[rule]: # doesn't match =
            ok = False
            skipped[rule] += 1
            break
        if ok:
          for rule in ne:
            if row[rule] in ne[rule]: # matches !
              ok = False
              skipped[rule] += 1
              break
          if ok:
            # check lt
            for rule in lt:
              if float(row[rule]) >= lt[rule]: # lt fail
                ok = False
                skipped[rule] += 1
                break
            if ok:
              # check lt
              for rule in gt:
                if float(row[rule]) <= gt[rule]: # gt fail
                  ok = False
                  skipped[rule] += 1
                  break
              if ok:
                out.writerow(row)
                written += 1

    logging.info('wrote %i of %i', written, lines + 1)
    logging.info('filtered: %s', ' '.join(['{}: {}'.format(key, skipped[key]) for key in skipped]))

def main():
    '''
        parse command line arguments
    '''
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    parser = argparse.ArgumentParser(description='Filter rows')
    parser.add_argument('--filters', nargs='+', help='colname[<=>!]valname... same colname is or, different colname is and')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    args = parser.parse_args()
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.filters, args.delimiter)

if __name__ == '__main__':
    main()
