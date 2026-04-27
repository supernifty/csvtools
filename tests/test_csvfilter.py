import csv
import io
import sys
import textwrap

import pytest

from csvtools.csvfilter import process


SAMPLE_CSV = textwrap.dedent(
    """\
name,category,value,limit,text,copy
alice,foo,10,15,alpha,alpha
bob,bar,20,10,foo=bar,beta
charlie,baz,30,35,bar,bar
diana,qux,40,40,prefix=bar,beta
eve,foo,50,45,zzz,zzz
"""
)


def _process(input_csv: str, *, filters, any_filter=False, exclude=False):
    old_stdout = sys.stdout
    captured = io.StringIO()
    try:
        sys.stdout = captured
        reader = csv.DictReader(io.StringIO(input_csv))
        process(reader, filters, delimiter=",", any_filter=any_filter, exclude=exclude)
    finally:
        sys.stdout = old_stdout
    return captured.getvalue()


def _output_lines(output: str):
    return output.strip().splitlines()


def test_same_column_equals_rules_are_or_by_default():
    output = _process(SAMPLE_CSV, filters=["category=foo", "category=bar"])

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "alice,foo,10,15,alpha,alpha",
        "bob,bar,20,10,foo=bar,beta",
        "eve,foo,50,45,zzz,zzz",
    ]


def test_different_columns_are_and_by_default():
    output = _process(SAMPLE_CSV, filters=["category=foo", "value>40"])

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "eve,foo,50,45,zzz,zzz",
    ]


def test_exclude_keeps_rows_that_fail_all_filters():
    output = _process(SAMPLE_CSV, filters=["category=foo"], exclude=True)

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "bob,bar,20,10,foo=bar,beta",
        "charlie,baz,30,35,bar,bar",
        "diana,qux,40,40,prefix=bar,beta",
    ]


def test_any_filter_matches_when_any_rule_succeeds():
    output = _process(
        SAMPLE_CSV,
        filters=["category=foo", "value>40"],
        any_filter=True,
    )

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "alice,foo,10,15,alpha,alpha",
        "eve,foo,50,45,zzz,zzz",
    ]


def test_any_filter_exclude_keeps_only_rows_that_fail_every_rule():
    output = _process(
        SAMPLE_CSV,
        filters=["category=foo", "value>40"],
        any_filter=True,
        exclude=True,
    )

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "bob,bar,20,10,foo=bar,beta",
        "charlie,baz,30,35,bar,bar",
        "diana,qux,40,40,prefix=bar,beta",
    ]


def test_contains_rule_accepts_equals_in_match_value():
    output = _process(SAMPLE_CSV, filters=["text%foo=bar"])

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "bob,bar,20,10,foo=bar,beta",
    ]


def test_contains_rule_with_equals_supports_exclude():
    output = _process(SAMPLE_CSV, filters=["text%foo=bar"], exclude=True)

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "alice,foo,10,15,alpha,alpha",
        "charlie,baz,30,35,bar,bar",
        "diana,qux,40,40,prefix=bar,beta",
        "eve,foo,50,45,zzz,zzz",
    ]


def test_any_filter_with_contains_rule_value_including_equals():
    output = _process(
        SAMPLE_CSV,
        filters=["category=foo", "text%foo=bar"],
        any_filter=True,
    )

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "alice,foo,10,15,alpha,alpha",
        "bob,bar,20,10,foo=bar,beta",
        "eve,foo,50,45,zzz,zzz",
    ]


def test_any_filter_exclude_with_contains_rule_value_including_equals():
    output = _process(
        SAMPLE_CSV,
        filters=["category=foo", "text%foo=bar"],
        any_filter=True,
        exclude=True,
    )

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "charlie,baz,30,35,bar,bar",
        "diana,qux,40,40,prefix=bar,beta",
    ]


def test_column_to_column_greater_than_filter():
    output = _process(SAMPLE_CSV, filters=["value>limit"])

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "bob,bar,20,10,foo=bar,beta",
        "eve,foo,50,45,zzz,zzz",
    ]


def test_column_to_column_equality_filter():
    output = _process(SAMPLE_CSV, filters=["text:copy"])

    assert _output_lines(output) == [
        "name,category,value,limit,text,copy",
        "alice,foo,10,15,alpha,alpha",
        "charlie,baz,30,35,bar,bar",
        "eve,foo,50,45,zzz,zzz",
    ]


def test_invalid_filter_without_operator_raises_value_error():
    with pytest.raises(ValueError, match='no operator found'):
        _process(SAMPLE_CSV, filters=["category"])


def test_unknown_source_column_raises_value_error():
    with pytest.raises(ValueError, match='unknown column "missing"'):
        _process(SAMPLE_CSV, filters=["missing=foo"])


def test_unknown_comparison_column_raises_value_error():
    with pytest.raises(ValueError, match='unknown comparison column "missing"'):
        _process(SAMPLE_CSV, filters=["value>missing"])
