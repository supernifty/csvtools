#!/usr/bin/env python
'''
  filter rows
'''

import argparse
import collections
import csv
import logging
import sys

def is_numeric(value, line, colname, complain=True):
  try:
    _ = float(value)
    return True
  except ValueError:
    if complain:
      logging.debug('line %i: %s is not numeric: %s', line, colname, value)

    return False

def rule_succeeded(out, row, exclude):
  logging.debug('entering rule_succeeded with exclude=%s for row=%s', exclude, row)
  if not exclude:
    out.writerow(row)

def process(fh, filters, delimiter, any_filter, exclude=False, rows=None):
    '''
        read in csv file, look at the header of each
        apply rule to each field (in order)
    '''
    logging.info('reading from stdin...')

    if filters is None:
      filters = []

    out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames)
    out.writeheader()
    lines = passed = 0

    eq = collections.defaultdict(set) # equal to rule
    lt = collections.defaultdict(float)
    gt = collections.defaultdict(float)
    ne = collections.defaultdict(set)
    contains = collections.defaultdict(set)
    not_contains = collections.defaultdict(set)
    starts = collections.defaultdict(set)
    for rule in filters:
      if '=' in rule:
        colname, value = rule.split('=', maxsplit=1)
        eq[colname].add(value)
      elif '%' in rule:
        colname, value = rule.split('%', maxsplit=1)
        contains[colname].add(value)
      elif '~' in rule:
        colname, value = rule.split('~', maxsplit=1)
        not_contains[colname].add(value)
      elif '^' in rule:
        colname, value = rule.split('^', maxsplit=1)
        starts[colname].add(value)
      elif '!' in rule:
        colname, value = rule.split('!', maxsplit=1)
        ne[colname].add(value)
      elif '<' in rule:
        colname, value = rule.split('<', maxsplit=1)
        try:
          lt[colname] = float(value) # lt contains colname of interest and required value
        except ValueError:
          lt[colname] = value # now it's another column name
      elif '>' in rule:
        colname, value = rule.split('>', maxsplit=1)
        try:
          gt[colname] = float(value)
        except ValueError:
          gt[colname] = value # now it's another column name

    logging.info('affected columns: %s %s %s %s %s %s', ' '.join(eq.keys()), ' '.join(lt.keys()), ' '.join(gt.keys()), ' '.join(ne.keys()), ' '.join(contains.keys()), ' '.join(starts.keys()))
    
    skipped = collections.defaultdict(int)
    for lines, row in enumerate(fh):
        # check each rule for a fail
        ok = True
        done = False # for any_filter
        # check lines
        logging.debug('processing %i: %s', lines, row)
        
        if rows is not None:
          row_ok = False
          for row_rule in rows:
            if '-' in row_rule:
              row_range = [int(r) for r in row_rule.split('-')]
              if row_range[0] <= lines + 1 <= row_range[1]:
                row_ok = True
                break
            else:
              if lines + 1 == int(row_rule):
                row_ok = True
                break
          if not row_ok:
            logging.debug('skipped row %i outside of row ranges', lines)
            continue

        # now rules
        for rule in eq: # each colname in rules
          if row[rule] not in eq[rule]: # doesn't match =
            ok = False
            skipped[rule] += 1
            if not any_filter: # fail
              break
          elif any_filter: # success
            done = True
            break

        if done:
          rule_succeeded(out, row, exclude)
          passed += 1
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
            rule_succeeded(out, row, exclude)
            passed += 1
            continue

          if any_filter or ok:
            # check lt
            for rule in lt: # rule is colname
              if not is_numeric(row[rule], lines, rule) or (is_numeric(lt[rule], lines, rule) and float(row[rule]) >= lt[rule]) or (not is_numeric(lt[rule], lines, rule) and float(row[rule]) >= float(row[lt[rule]])): # lt fail
                ok = False
                skipped[rule] += 1
                if not any_filter:
                  break
              elif any_filter: # success
                done = True
                break

            if done:
              rule_succeeded(out, row, exclude)
              passed += 1
              continue

            if any_filter or ok:
              # check gt
              for rule in gt:
                if not is_numeric(row[rule], lines, rule) or (is_numeric(gt[rule], lines, rule) and float(row[rule]) <= gt[rule]) or (not is_numeric(gt[rule], lines, rule) and float(row[rule]) <= float(row[gt[rule]])): # gt fail
                  ok = False
                  skipped[rule] += 1
                  if not any_filter:
                    break
                elif any_filter:
                  done = True
                  break

              if done:
                rule_succeeded(out, row, exclude)
                passed += 1
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
                  rule_succeeded(out, row, exclude)
                  passed += 1
                  continue

                if any_filter or ok:
                  for rule in not_contains: # each row
                    if all(x in row[rule] for x in not_contains[rule]):
                      ok = False
                      skipped[rule] += 1
                      if not any_filter:
                        break
                    elif any_filter:
                      done = True
                      break

                  if done:
                    rule_succeeded(out, row, exclude)
                    passed += 1
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
                      rule_succeeded(out, row, exclude)
                      passed += 1

        # it got through all rules and something failed
        if exclude and not ok:
          rule_succeeded(out, row, False)

        if lines % 100000 == 0:
          logging.info('%i lines processed, wrote %i. last row read: %s...', lines, passed, row)

    logging.info('wrote %i of %i', passed, lines + 1)
    logging.info('filtered: %s', ' '.join(['{}: {}'.format(key, skipped[key]) for key in skipped]))

def main():
    '''
        parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Filter rows')
    parser.add_argument('--filters', nargs='+', help='colname[<=>!%%^]valname... same colname is or, different colname is and')
    parser.add_argument('--rows', nargs='+', required=False, help='row numbers to include n n1-n2')
    parser.add_argument('--delimiter', default=',', help='csv delimiter')
    parser.add_argument('--any', action='store_true', help='allow if any filter is true (default is and)')
    parser.add_argument('--exclude', action='store_true', default=False, help='write rows that fail test')
    parser.add_argument('--encoding', default='utf-8', help='file encoding')
    parser.add_argument('--verbose', action='store_true', default=False, help='more logging')
    parser.add_argument('--quiet', action='store_true', default=False, help='less logging')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    elif args.quiet:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.WARN)
    else:
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.INFO)
    if "reconfigure" in dir(sys.stdin):
      sys.stdin.reconfigure(encoding=args.encoding)
      logging.debug('encoding %s applied', args.encoding)
    else:
      logging.debug('using default encoding')
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.filters, args.delimiter, args.any, args.exclude, args.rows)

if __name__ == '__main__':
    main()
