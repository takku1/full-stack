"""Local inventory command line application."""
import argparse
import csv
import sqlite3
import sys
from storage import apply_batch, list_items
from validation import InvalidCSV, read_batch


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db', default='inventory.sqlite3')
    commands = parser.add_subparsers(dest='command', required=True)
    importer = commands.add_parser('import', help='Import a UTF-8 CSV atomically')
    importer.add_argument('csv_path')
    commands.add_parser('list', help='List inventory')
    args = parser.parse_args()
    try:
        if args.command == 'import':
            rows = read_batch(args.csv_path)
            apply_batch(args.db, rows)
            print(f'Imported {len(rows)} rows')
        else:
            writer = csv.writer(sys.stdout, lineterminator='\n')
            writer.writerow(['name', 'quantity'])
            writer.writerows(list_items(args.db))
    except (OSError, UnicodeError, csv.Error, sqlite3.Error, InvalidCSV) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
