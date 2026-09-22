#!/usr/bin/env python3
"""Extend odoo_cit_summer_2026.csv with the new coin_product_management columns.

Idempotent per-column: safe to re-run after new columns are added to the
module, it will only insert whatever is still missing and leaves any
already-present column's data untouched.

- "Quantity On Hand": DUMMY/TEST stock quantities (seeded random, NOT real
  inventory numbers). Odoo's product import maps this header natively and
  creates the initial on-hand quantity for new products.
- "Customer" / "Customer Phone" / "Customer Email": left blank for every
  row. None of the current 18 rows are customer-commissioned
  "003 Münzen Kundenprodukte" items, so there is no real customer to
  attach yet. All three are independently-settable fields in the module
  (not derived from a linked contact), so they import directly.
- "Coin Cover Attribute" / "Coin Cover Values": populated only for actual
  coin/medal rows (category contains "Münzen" or "Medaillen"), not for
  packaging/accessory rows. Maps to product.template's one2many
  attribute_line_ids (attribute_id / value_ids) via nested "/" column
  paths in Odoo's import wizard, matched by name like Product Category
  was. Each coin gets both "Capsule" and "Box" as selectable values,
  so Odoo generates one variant per packaging option.

  IMPORTANT: when mapping these two columns in the import wizard, map
  them to the nested path Attributes (attribute_line_ids) > Attribute
  (attribute_id) and Attributes > Values (value_ids) respectively - the
  wizard lets you drill into the relation via the field picker. This is
  a more fragile import path than a flat field; if it errors, check that
  the module has been upgraded first so the "Coin Cover" attribute and
  its Capsule/Box values already exist (data/product_attribute_data.xml).
"""

import csv
import random
import sys
from pathlib import Path

INPUT_CSV = Path("odoo_cit_summer_2026.csv")
OUTPUT_CSV = Path("odoo_cit_summer_2026_.csv")  # updated in place

QTY_MIN, QTY_MAX = 5, 75
RANDOM_SEED = 42


def _is_numismatic_row(row):
    category = row.get("Product Category", "")
    return "Münzen" in category or "Medaillen" in category


def _dummy_qty(_row):
    return random.randint(QTY_MIN, QTY_MAX)


def _coin_cover_attribute(row):
    return "Coin Cover" if _is_numismatic_row(row) else ""


def _coin_cover_values(row):
    return "Capsule,Box" if _is_numismatic_row(row) else ""


# (column name, insert-after existing column, value or value(row) -> value)
NEW_COLUMNS = [
    ("Customer", "Internal Reference", ""),
    ("Customer Phone", "Customer", ""),
    ("Customer Email", "Customer Phone", ""),
    ("Quantity On Hand", "Sales Price", _dummy_qty),
    ("Coin Cover Attribute", "Quantity On Hand", _coin_cover_attribute),
    ("Coin Cover Values", "Coin Cover Attribute", _coin_cover_values),
]


def run():
    if not INPUT_CSV.exists():
        sys.exit(f"Input file not found: {INPUT_CSV}")

    csv.field_size_limit(sys.maxsize)
    with INPUT_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    missing = [(name, after, default) for name, after, default in NEW_COLUMNS if name not in fieldnames]
    if not missing:
        print("All target columns already present. Nothing to do.")
        return

    new_fieldnames = list(fieldnames)
    for name, after, _default in missing:
        if after in new_fieldnames:
            new_fieldnames.insert(new_fieldnames.index(after) + 1, name)
        else:
            new_fieldnames.append(name)

    random.seed(RANDOM_SEED)
    for row in rows:
        for name, _after, default in missing:
            row[name] = default(row) if callable(default) else default

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=new_fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    added = ", ".join(name for name, _a, _d in missing)
    print(f"Updated {len(rows)} rows in '{OUTPUT_CSV}': added column(s): {added}.")


if __name__ == "__main__":
    run()
