"""Command-line conventions shared by the skill's scripts.

Exit codes (every script):
  0  success
  1  the script ran and found something to report (lint findings not accounted for, no matching rule,
     or a self-test failure)
  2  bad input, or output that can't be written: the message says what to fix
  3  internal error: a bug in the script; the traceback shows where, and the output is incomplete
  5  usage error (a wrong or missing argument)
  130  interrupted (Ctrl-C), the shell's convention
"""
import argparse
import json
import os
import signal
import sys
import tempfile
import traceback

OK, FOUND, BAD_INPUT, INTERNAL, USAGE = 0, 1, 2, 3, 5
INTERRUPTED = 130


class InputError(Exception):
    """Bad input, or output that can't be written: something the user can fix."""


class ArgParser(argparse.ArgumentParser):
    """argparse with the shared usage exit code (5) instead of argparse's 2, which means bad input here."""

    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(USAGE, f'{self.prog}: error: {message}\n')


def setup_output():
    """UTF-8 output on every platform (a cp1252 console can't print a check mark), and a quiet end when piped into head."""
    if hasattr(signal, 'SIGPIPE'):
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass


def read_json(path, what='file'):
    """Load a JSON file (a byte-order mark is allowed); raise InputError with a plain message if it can't be read."""
    try:
        with open(path, encoding='utf-8-sig') as fh:
            return json.load(fh)
    except OSError as e:
        raise InputError(f'cannot read {what} {path}: {e.strerror or e}') from e
    except ValueError as e:
        raise InputError(f'{what} {path} is not valid JSON ({e}); fix or regenerate it') from e


def write_json(path, data):
    """Write JSON atomically: a crash or a full disk never leaves a half-written file for the next script to read."""
    folder = os.path.dirname(os.path.abspath(path))
    try:
        fd, tmp = tempfile.mkstemp(prefix='.tmp-', suffix='.json', dir=folder)
    except OSError as e:
        raise InputError(f'cannot write {path}: {e.strerror or e}') from e
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as fh:
            json.dump(data, fh, indent=1, ensure_ascii=False)
        os.replace(tmp, path)
    except OSError as e:
        raise InputError(f'cannot write {path}: {e.strerror or e}') from e
    finally:
        if os.path.exists(tmp):
            os.remove(tmp)


def run_main(prog, main):
    """Run main() and return its exit code. InputError -> 2 with its message; any other exception -> 3 with a traceback."""
    try:
        rc = main()
    except InputError as e:
        print(f'{prog}: error: {e}', file=sys.stderr)
        return BAD_INPUT
    except KeyboardInterrupt:
        print(f'{prog}: interrupted', file=sys.stderr)
        return INTERRUPTED
    except Exception:  # a bug: show where, and say the output is incomplete
        traceback.print_exc()
        print(f'{prog}: internal error (a bug in the script); the traceback above shows where. Any output is incomplete.', file=sys.stderr)
        return INTERNAL
    return OK if rc is None else rc
