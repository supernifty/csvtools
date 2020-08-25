#!/usr/bin/env python
'''
  filter rows
'''

import argparse
import collections
import csv
import gzip
import logging
import sys

def get_fh(fh):
  try:
    c = fh.read(1)
    fh.seek(0)
    if ord(c) == 0x1f:
      return gzip.open(fh, 'rt')
    else:
      return fh
  except:
    return sys.stdin

def is_numeric(value, line, colname):
  try:
    _ = float(value)
    return True
  except ValueError:
    logging.debug('line %i: %s is not numeric: %s', line, colname, value)
    return False

def process(fh, filters, delimiter, any_filter):
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
    contains = collections.defaultdict(set)
    starts = collections.defaultdict(set)
    for rule in filters:
      if '=' in rule:
        colname, value = rule.split('=')
        eq[colname].add(value)
      elif '%' in rule:
        colname, value = rule.split('%')
        contains[colname].add(value)
      elif '^' in rule:
        colname, value = rule.split('^')
        starts[colname].add(value)
      elif '!' in rule:
        colname, value = rule.split('!')
        ne[colname].add(value)
      elif '<' in rule:
        colname, value = rule.split('<')
        lt[colname] = float(value)
      elif '>' in rule:
        colname, value = rule.split('>')
        gt[colname] = float(value)

    logging.info('affected columns: %s %s %s %s %s %s', ' '.join(eq.keys()), ' '.join(lt.keys()), ' '.join(gt.keys()), ' '.join(ne.keys()), ' '.join(contains.keys()), ' '.join(starts.keys()))
    
    skipped = collections.defaultdict(int)
    for lines, row in enumerate(fh):
        # check each rule
        ok = True
        done = False # for any_filter
        for rule in eq: # each colname in rules
          if row[rule] not in eq[rule]: # doesn't match =
            ok = False
            skipped[rule] += 1
            if not any_filter:
              break
          elif any_filter: # success
            done = True
            break
        if done:
          out.writerow(row)
          written += 1
          continue

        if any_filter or ok:
          for rule in ne:
            if row[rule] in ne[rule]: # matches !
              ok = False
              skipped[rule] += 1
              if not any_filter:
                break
            elif any_filter: # success
              done = True
              break
          if done:
            out.writerow(row)
            written += 1
            continue
          if any_filter or ok:
            # check lt
            for rule in lt:
              if not is_numeric(row[rule], lines, rule) or float(row[rule]) >= lt[rule]: # lt fail
                ok = False
                skipped[rule] += 1
                if not any_filter:
                  break
              elif any_filter:
                done = True
                break
            if done:
              out.writerow(row)
              written += 1
              continue
            if any_filter or ok:
              # check lt
              for rule in gt:
                if not is_numeric(row[rule], lines, rule) or float(row[rule]) <= gt[rule]: # gt fail
                  ok = False
                  skipped[rule] += 1
                  if not any_filter:
                    break
                elif any_filter:
                  done = True
                  break
              if done:
                out.writerow(row)
                written += 1
                continue
              if any_filter or ok:
                for rule in starts: # each row
                  if all(not row[rule].startswith(x) for x in starts[rule]):
                    ok = False
                    skipped[rule] += 1
                    if not any_filter:
                      break
                  elif any_filter:
                    done = True
                    break
                if done:
                  out.writerow(row)
                  written += 1
                  continue
  
                if any_filter or ok:
                  for rule in contains: # each row
                    if all(x not in row[rule] for x in contains[rule]):
                      ok = False
                      skipped[rule] += 1
                      if not any_filter:
                        break
                    elif any_filter:
                      done = True
                      break
  
                  if done or ok:
                    out.writerow(row)
                    written += 1

        if lines % 100000 == 0:
          logging.info('%i lines processed, wrote %i. last row read: %s...', lines, written, row)

    logging.info('wrote %i of %i', written, lines + 1)
    logging.info('filtered: %s', ' '.join(['{}: {}'.format(key, skipped[key]) for key in skipped]))

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Filter rows')
    parser.add_argument('--filters', nargs='+', help='colname[<=>!%%^]valname... same colname is or, different colname is and')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    parser.add_argument('--any', action='store_true', help='allow if any filter is true (default is and)')
    parser.add_argument('--verbose', action='store_true', default=False, help='more logging')
    parser.add_argument('--quiet', action='store_true', default=False, help='less logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    process(csv.DictReader(get_fh(sys.stdin.buffer), delimiter=args.delimiter), args.filters, args.delimiter, args.any)

if __name__ == '__main__':
    main()
