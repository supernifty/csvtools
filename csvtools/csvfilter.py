#!/usr/bin/env python
'''
  Filter CSV rows using a small rule engine.

  The module works in three stages:
  1. Parse raw filter strings such as ``category=foo`` or ``value>limit``.
  2. Compile them into rule objects grouped by operator semantics.
  3. Evaluate each input row once and decide whether it belongs in the
     main output or the filtered output.
'''

import argparse
import collections
import csv
import logging
import sys
from dataclasses import dataclass, field

OPERATORS = ['=', '%', '~', '^', '!', '<', '>', ':']
RULE_ORDER = ['=', '!', '<', '>', '^', '~', '%', ':']


class FilterError(ValueError):
  '''Raised when the filter specification is invalid before streaming rows.'''
  pass


@dataclass(frozen=True)
class RuleSpec:
  '''Single parsed filter string before it is normalised into runtime rules.'''
  column: str
  op: str
  value: str


@dataclass
class Rule:
  '''
    Runtime rule used during row evaluation.

    ``values`` is used for grouped string operators such as ``=`` or ``%``.
    ``target`` stores a numeric literal for ``<`` / ``>`` comparisons.
    ``ref_column`` stores a second column name for column-to-column checks.
  '''
  column: str
  op: str
  values: set = field(default_factory=set)
  target: float | None = None
  ref_column: str | None = None


def is_numeric(value, line, colname, complain=True):
  '''Return ``value`` as a float, or ``None`` if conversion fails.'''
  try:
    return float(value)
  except ValueError:
    if complain:
      logging.debug('line %i: %s is not numeric: %s', line, colname, value)

    return None


def parse_rule(rule):
  '''
    Split one raw filter string into ``column``, ``operator`` and ``value``.

    The first operator character wins, which allows values to contain other
    operator characters later in the string.
  '''
  matches = [(rule.find(op), op) for op in OPERATORS if op in rule]
  if not matches:
    raise FilterError('invalid filter "{}": no operator found'.format(rule))

  idx, op = min(matches)
  colname = rule[:idx]
  value = rule[idx + 1:]
  if not colname:
    raise FilterError('invalid filter "{}": missing column name'.format(rule))

  return RuleSpec(colname, op, value)


def add_grouped_rule(grouped, spec):
  '''Merge OR-style string rules for the same column/operator pair.'''
  if spec.column not in grouped[spec.op]:
    grouped[spec.op][spec.column] = Rule(spec.column, spec.op)
  grouped[spec.op][spec.column].values.add(spec.value)


def add_compare_rule(grouped, spec, fieldnames):
  '''Compile ``<`` and ``>`` rules against either a number or another column.'''
  if is_numeric(spec.value, -1, spec.column, complain=False) is not None:
    grouped[spec.op][spec.column] = Rule(spec.column, spec.op, target=float(spec.value))
    return

  if spec.value not in fieldnames:
    raise FilterError(
      'invalid filter "{}{}{}": unknown comparison column "{}"'.format(
        spec.column, spec.op, spec.value, spec.value
      )
    )
  grouped[spec.op][spec.column] = Rule(spec.column, spec.op, ref_column=spec.value)


def compile_rules(filters, fieldnames):
  '''
    Validate and normalise all filters before row processing begins.

    The output order defines evaluation order. Same-column grouped rules are
    collapsed into one runtime rule so they still behave like OR conditions.
  '''
  if filters is None:
    filters = []

  grouped = {op: collections.OrderedDict() for op in RULE_ORDER}
  for rule_text in filters:
    spec = parse_rule(rule_text)
    if spec.column not in fieldnames:
      raise FilterError(
        'invalid filter "{}{}{}": unknown column "{}"'.format(
          spec.column, spec.op, spec.value, spec.column
        )
      )

    if spec.op in ['=', '!', '%', '~', '^']:
      add_grouped_rule(grouped, spec)
    elif spec.op in ['<', '>']:
      add_compare_rule(grouped, spec, fieldnames)
    elif spec.op == ':':
      if spec.value not in fieldnames:
        raise FilterError(
          'invalid filter "{}:{}": unknown comparison column "{}"'.format(
            spec.column, spec.value, spec.value
          )
        )
      grouped[spec.op][spec.column] = Rule(spec.column, spec.op, ref_column=spec.value)

  rules = []
  for op in RULE_ORDER:
    rules.extend(grouped[op].values())
  return rules


def log_affected_columns(rules):
  '''Emit a compact summary of which columns participate in each rule type.'''
  affected = collections.defaultdict(list)
  for rule in rules:
    affected[rule.op].append(rule.column)

  logging.info(
    'affected columns: eq=%s lt=%s gt=%s ne=%s contains=%s starts=%s not_contains=%s other=%s',
    ' '.join(affected['=']),
    ' '.join(affected['<']),
    ' '.join(affected['>']),
    ' '.join(affected['!']),
    ' '.join(affected['%']),
    ' '.join(affected['^']),
    ' '.join(affected['~']),
    ' '.join(affected[':']),
  )


def rule_matches(rule, row, line):
  '''Evaluate one runtime rule against one input row.'''
  if rule.op == '=':
    return row[rule.column] in rule.values
  if rule.op == '!':
    return row[rule.column] not in rule.values
  if rule.op == '%':
    return any(value in row[rule.column] for value in rule.values)
  if rule.op == '~':
    return not all(value in row[rule.column] for value in rule.values)
  if rule.op == '^':
    return any(row[rule.column].startswith(value) for value in rule.values)
  if rule.op == ':':
    return row[rule.column] == row[rule.ref_column]

  lhs = is_numeric(row[rule.column], line, rule.column)
  if lhs is None:
    return False

  rhs = rule.target
  if rule.ref_column is not None:
    rhs = is_numeric(row[rule.ref_column], line, rule.ref_column)
    if rhs is None:
      return False

  if rule.op == '<':
    return lhs < rhs
  return lhs > rhs


def row_matches(rules, row, line, any_filter, skipped):
  '''
    Combine rule results for one row.

    ``any_filter=False`` means all compiled rules must pass.
    ``any_filter=True`` means the row matches as soon as one rule passes.
    ``skipped`` records the first failing column in AND mode, or every failed
    rule in OR mode until one succeeds.
  '''
  if not rules:
    return True

  if any_filter:
    for rule in rules:
      if rule_matches(rule, row, line):
        return True
      skipped[rule.column] += 1
    return False

  for rule in rules:
    if not rule_matches(rule, row, line):
      skipped[rule.column] += 1
      return False
  return True


def row_selected(line, rows):
  '''Apply the optional ``--rows`` pre-filter before evaluating rule logic.'''
  if rows is None:
    return True

  line_number = line + 1
  for row_rule in rows:
    if '-' in row_rule:
      start, end = [int(r) for r in row_rule.split('-')]
      if start <= line_number <= end:
        return True
    elif line_number == int(row_rule):
      return True

  logging.debug('skipped row %i outside of row ranges', line)
  return False


def write_row(out, out_f, row, write_main):
  '''Route a row to stdout or the optional filtered-output writer.'''
  if write_main:
    out.writerow(row)
  elif out_f is not None:
    out_f.writerow(row)


def process(fh, filters, delimiter, any_filter, exclude=False, rows=None, write_filtered=None):
  '''
      Stream rows from ``fh`` through the compiled filter engine.

      The main loop is:
      1. Compile and validate filters once from the header.
      2. Skip rows outside ``--rows`` selections.
      3. Evaluate whether the row matches the filter set.
      4. Invert the result when ``--exclude`` is set.
      5. Write the row to stdout or ``--write_filtered`` as appropriate.
  '''
  logging.info('reading from stdin...')

  rules = compile_rules(filters, fh.fieldnames)
  log_affected_columns(rules)

  out = csv.DictWriter(sys.stdout, delimiter=delimiter, fieldnames=fh.fieldnames)
  out.writeheader()

  out_fh = None
  if write_filtered is not None:
    out_fh = open(write_filtered, 'wt')
    out_f = csv.DictWriter(out_fh, delimiter=delimiter, fieldnames=fh.fieldnames)
    out_f.writeheader()
  else:
    out_f = None

  passed = 0
  total = 0
  skipped = collections.defaultdict(int)
  try:
    for line, row in enumerate(fh):
      total = line + 1
      logging.debug('processing %i: %s', line, row)

      if not row_selected(line, rows):
        continue

      matched = row_matches(rules, row, line, any_filter, skipped)
      write_main = matched != exclude
      write_row(out, out_f, row, write_main)
      if write_main:
        passed += 1

      if line % 100000 == 0:
        logging.info('%i lines processed, wrote %i. last row read: %s...', line, passed, row)
  finally:
    if out_fh is not None:
      out_fh.close()

  logging.info('wrote %i of %i', passed, total)
  logging.info('filtered: %s', ' '.join(['{}: {}'.format(key, skipped[key]) for key in skipped]))


def main():
  '''
      Parse CLI arguments, configure logging, and run the filter pipeline.
  '''
  parser = argparse.ArgumentParser(description='Filter rows')
  parser.add_argument('--filters', nargs='+', help='colname[<=>!%%^]valname... same colname is or, different colname is and')
  parser.add_argument('--rows', nargs='+', required=False, help='row numbers to include n n1-n2')
  parser.add_argument('--delimiter', default=',', help='csv delimiter')
  parser.add_argument('--any', action='store_true', help='allow if any filter is true (default is and)')
  parser.add_argument('--exclude', action='store_true', default=False, help='write rows that fail test')
  parser.add_argument('--write_filtered', help='write rows that fail test to this file')
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
  if 'reconfigure' in dir(sys.stdin):
    sys.stdin.reconfigure(encoding=args.encoding)
    logging.debug('encoding %s applied', args.encoding)
  else:
    logging.debug('using default encoding')

  try:
    process(csv.DictReader(sys.stdin, delimiter=args.delimiter), args.filters, args.delimiter, args.any, args.exclude, args.rows, args.write_filtered)
  except FilterError as exc:
    logging.error(str(exc))
    raise SystemExit(1)


if __name__ == '__main__':
  main()
