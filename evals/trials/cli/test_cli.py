"""Real subprocess integration checks; each CLI call starts a new process."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent


def run_suite(phase):
    events = [{'python': sys.version, 'phase': phase}]
    with tempfile.TemporaryDirectory(dir=ROOT) as temporary:
        directory = Path(temporary)
        db = directory / 'inventory.sqlite3'

        def call(*args, expected=0):
            command = [sys.executable, str(ROOT / 'inventory.py'), '--db', str(db), *map(str, args)]
            result = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
            events.append({'argv': command, 'exit': result.returncode, 'stdout': result.stdout, 'stderr': result.stderr})
            assert result.returncode == expected, events[-1]
            return result

        def import_text(name, contents, expected=0):
            path = directory / name
            path.write_text(contents, encoding='utf-8')
            return call('import', path, expected=expected)

        def listed():
            return call('list').stdout

        try:
            import_text('valid.csv', 'name,quantity\napple,2\npear,0\n')
            baseline = 'name,quantity\napple,2\npear,0\n'
            assert listed() == baseline
            call('import', directory / 'missing.csv', expected=1)
            assert listed() == baseline
            errors = import_text('invalid.csv', 'name,quantity\napple,9\n,2\npear,-1\nmelon,1.5\n', expected=1)
            for line in (3, 4, 5):
                assert f'row {line}:' in errors.stderr
            assert listed() == baseline
            import_text('duplicate.csv', 'name,quantity\napple,9\napple,4\n', expected=1)
            assert listed() == baseline
            import_text('wrong_header.csv', 'name,count\napple,9\n', expected=1)
            assert listed() == baseline
            import_text('shape.csv', 'name,quantity\napple,9\nmissing\nextra,1,2\n', expected=1)
            assert listed() == baseline
            import_text('overflow.csv', 'name,quantity\napple,9223372036854775808\n', expected=1)
            assert listed() == baseline
            invalid_utf8 = directory / 'encoding.csv'
            invalid_utf8.write_bytes(b'name,quantity\n\xff,4\n')
            call('import', invalid_utf8, expected=1)
            assert listed() == baseline
            import_text('broken.csv', 'name,quantity\n"unterminated,2\n', expected=1)
            assert listed() == baseline
            # A real SQLite trigger rejects the second write after the first update.
            with closing(sqlite3.connect(db)) as connection:
                connection.execute("CREATE TRIGGER fail_blocked BEFORE INSERT ON inventory WHEN NEW.name = 'blocked' BEGIN SELECT RAISE(ABORT, 'blocked by test trigger'); END")
            import_text('rollback.csv', 'name,quantity\napple,55\nblocked,1\n', expected=1)
            assert listed() == baseline
            with closing(sqlite3.connect(db)) as connection:
                connection.execute('DROP TRIGGER fail_blocked')
            import_text('update.csv', 'name,quantity\napple,7\nmelon,4\n')
            baseline = 'name,quantity\napple,7\nmelon,4\npear,0\n'
            assert listed() == baseline
            import_text('empty.csv', 'name,quantity\n')
            assert listed() == baseline
            if phase == 'initial':
                import_text('spaces.csv', 'name,quantity\n apple ,8\n', expected=1)
                assert listed() == baseline
            else:
                import_text('spaces.csv', 'name,quantity\n apple ,8\n  new item  ,3\n')
                baseline = 'name,quantity\napple,8\nmelon,4\nnew item,3\npear,0\n'
                assert listed() == baseline
                import_text('trim_duplicate.csv', 'name,quantity\napple,9\n apple ,10\n', expected=1)
                assert listed() == baseline
                import_text('blank_name.csv', 'name,quantity\napple,9\n   ,2\n', expected=1)
                assert listed() == baseline
            events.append({'outcome': 'all assertions passed', 'cli_calls': len(events) - 1})
        except BaseException as error:
            events.append({'outcome': 'failed', 'error': repr(error)})
            raise
        finally:
            (ROOT / f'{phase}-execution.json').write_text(json.dumps(events, indent=2), encoding='utf-8')
    print(f'{phase}: all assertions passed; real CLI transcript saved')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('phase', choices=['initial', 'followup', 'final'])
    run_suite(parser.parse_args().phase)
