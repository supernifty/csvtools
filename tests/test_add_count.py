import io
import sys
import textwrap
import pathlib

# Ensure the project root directory is on sys.path so that
# `import csvtools` succeeds even when the package is not
# installed into the current environment.
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import csvtools.add_count as add_count


def _run_add_count(input_csv: str, *, dest, cols, delimiter=',', as_map=None):
    """Run add_count.main() with StringIO-based stdin/stdout and return output."""
    old_stdin, old_stdout = sys.stdin, sys.stdout
    try:
        sys.stdin = io.StringIO(input_csv)
        sys.stdout = io.StringIO()
        add_count.main(dest, cols, delimiter, as_map)
        return sys.stdout.getvalue()
    finally:
        sys.stdin, sys.stdout = old_stdin, old_stdout


SAMPLE = textwrap.dedent(
    """\
key,v1,v2
hello,bonjour,guten tag
hello,bonsoir,guten morgen
goodbye,au revoir,auf wiedersehn
"""
)


def test_grouped_counter():
    expected = textwrap.dedent(
        """\
key,v1,v2,count
hello,bonjour,guten tag,hello-1
hello,bonsoir,guten morgen,hello-2
goodbye,au revoir,auf wiedersehn,goodbye-1
"""
    )
    out = _run_add_count(SAMPLE, dest='count', cols=['key'])
    assert out.strip().splitlines() == expected.strip().splitlines()


def test_global_counter():
    expected = textwrap.dedent(
        """\
key,v1,v2,num
hello,bonjour,guten tag,1
hello,bonsoir,guten morgen,2
goodbye,au revoir,auf wiedersehn,3
"""
    )
    out = _run_add_count(SAMPLE, dest='num', cols=[])
    assert out.strip().splitlines() == expected.strip().splitlines()
