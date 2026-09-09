# Inventory CLI

Requires Python 3 with standard-library SQLite. Run commands from this directory.

Import a UTF-8 file with exact header `name,quantity`:

```powershell
python inventory.py --db inventory.sqlite3 import items.csv
```

List inventory:

```powershell
python inventory.py --db inventory.sqlite3 list
```

Names are case-sensitive and initially must have no surrounding whitespace or control characters. Quantities are nonnegative ASCII decimal integers (optional leading plus), at most 9223372036854775807. Duplicate batch names and any invalid rows reject the whole batch. Existing names are updated only after every row passes validation. Errors go to stderr and exit nonzero. Output listing is CSV sorted by name.
