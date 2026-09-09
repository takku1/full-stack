"""CSV input policy; no persistence side effects."""
import csv
import re


class InvalidCSV(ValueError):
    pass


def normalize_name(raw):
    if not raw or raw != raw.strip() or any(ord(c) < 32 for c in raw):
        raise ValueError('name must be nonempty, without surrounding whitespace or controls')
    return raw


def read_batch(path):
    rows, errors, seen = [], [], set()
    with open(path, encoding='utf-8', newline='') as stream:
        reader = csv.reader(stream, strict=True)
        if next(reader, None) != ['name', 'quantity']:
            raise InvalidCSV('row 1: expected header name,quantity')
        for fields in reader:
            line = reader.line_num
            if len(fields) != 2:
                errors.append(f'row {line}: expected two fields')
                continue
            raw_name, raw_quantity = fields
            try:
                name = normalize_name(raw_name)
            except ValueError as error:
                errors.append(f'row {line}: {error}')
                name = None
            if name is not None:
                if name in seen:
                    errors.append(f'row {line}: duplicate name {name!r}')
                seen.add(name)
            if not re.fullmatch(r'\+?[0-9]+', raw_quantity):
                errors.append(f'row {line}: quantity must be a nonnegative integer')
                continue
            digits = raw_quantity.lstrip('+').lstrip('0') or '0'
            if len(digits) > 19 or (len(digits) == 19 and digits > '9223372036854775807'):
                errors.append(f'row {line}: quantity exceeds SQLite integer range')
                continue
            rows.append((name, int(digits)))
    if errors:
        raise InvalidCSV('\n'.join(errors))
    return rows
