#!/usr/bin/env python3
"""Extend odoo_cit_summer_2026.csv with the new coin_product_management columns
and a few dummy "003 Kundenprodukte" (customer-commissioned) demo rows.

Idempotent: safe to re-run any time. Column-adding and row-adding each check
their own precondition and skip if already done; nothing already present
gets overwritten.

- "Quantity On Hand": DUMMY/TEST stock quantities (seeded random, NOT real
  inventory numbers). Odoo's product import maps this header natively and
  creates the initial on-hand quantity for new products.
- "Customer" / "Customer Phone" / "Customer Email": blank for the 18 real
  "002 Eigenprodukte"/"005 Zubehör" rows (no real customer to attach yet).
  Independently-settable fields in the module (not derived from a linked
  contact), so they import directly.
- "attribute_line_ids/attribute_id" / "attribute_line_ids/value_ids":
  the Coin Cover variant ("Coin Cover" / "Capsule,Box") on EVERY row,
  accessories included. Headers are technical field paths, which the
  import wizard maps automatically. Odoo creates one variant per value;
  the imported Quantity On Hand lands on the first one (Capsule), Box
  starts at 0. (Older copies of this CSV used "Coin Cover Attribute" /
  "Coin Cover Values"; the script renames them.)

- DUMMY_CLIENT_PRODUCTS: a handful of obviously-fake "003 Münzen
  Kundenprodukte" rows (fake company names, +41 00 000 00 0x phone
  numbers, @example-test.ch emails) so the Client Products view has
  something to show for testing. Reuses the first real coin's image
  bytes as a placeholder image. NOT real customer data - replace/delete
  before any real launch import.
"""

import csv
import random
import sys
from pathlib import Path

INPUT_CSV = Path("odoo_cit_summer_2026.csv")
OUTPUT_CSV = Path("odoo_cit_summer_2026.csv")  # updated in place

QTY_MIN, QTY_MAX = 0, 75
RANDOM_SEED = 42

CLIENT_CATEGORY = "CIT Artikelgruppen / 003 Münzen Kundenprodukte"

# Guarantee at least a couple of visible "0 coins left" rows for testing the
# zero-stock red styling, rather than leaving it to random chance.
FORCE_ZERO_STOCK_REFS = {"31254", "31217"}  # Born for Speed - Sailfish, Knight Games - Jousting

DUMMY_CLIENT_PRODUCTS = [
    {
        "Internal Reference": "CUST-DEMO-001",
        "Name": "Custom Corporate Medallion – Alpine Bank AG",
        "Customer": "Alpine Bank AG (TEST)",
        "Customer Phone": "+41 44 000 00 01",
        "Customer Email": "orders@alpinebank-test.example",
        "Sales Price": "459.00",
    },
    {
        "Internal Reference": "CUST-DEMO-002",
        "Name": "Custom Anniversary Coin – Grand Hotel Zurich",
        "Customer": "Grand Hotel Zurich (TEST)",
        "Customer Phone": "+41 44 000 00 02",
        "Customer Email": "events@grandhotelzurich-test.example",
        "Sales Price": "329.00",
    },
    {
        "Internal Reference": "CUST-DEMO-003",
        "Name": "Custom Commemorative Set – Kanton Uri",
        "Customer": "Kanton Uri Staatskanzlei (TEST)",
        "Customer Phone": "+41 41 000 00 03",
        "Customer Email": "info@ur-test.example",
        "Sales Price": "599.00",
    },
]


def _is_numismatic_row(row):
    category = row.get("Product Category", "")
    return "Münzen" in category or "Medaillen" in category


def _dummy_qty(_row):
    return random.randint(QTY_MIN, QTY_MAX)


# Technical field paths: Odoo's import wizard splits headers on "/" and maps
# each segment itself, so these columns need no manual mapping.
COVER_ATTR_COL = "attribute_line_ids/attribute_id"
COVER_VALUES_COL = "attribute_line_ids/value_ids"
LEGACY_COVER_COLS = {"Coin Cover Attribute": COVER_ATTR_COL, "Coin Cover Values": COVER_VALUES_COL}
COVER_ATTRIBUTE = "Coin Cover"
# Capsule first: Odoo puts an imported "Quantity On Hand" on the first variant.
COVER_VALUES = "Capsule,Box"

# (column name, insert-after existing column, value or value(row) -> value)
NEW_COLUMNS = [
    ("Customer", "Internal Reference", ""),
    ("Customer Phone", "Customer", ""),
    ("Customer Email", "Customer Phone", ""),
    ("Quantity On Hand", "Sales Price", _dummy_qty),
    (COVER_ATTR_COL, "Quantity On Hand", COVER_ATTRIBUTE),
    (COVER_VALUES_COL, COVER_ATTR_COL, COVER_VALUES),
]


def normalize_coin_cover(fieldnames, rows):
    """Rename the old human-readable Coin Cover headers and give every row
    (accessories included) both Capsule and Box."""
    changed = False
    for old, new in LEGACY_COVER_COLS.items():
        if old in fieldnames and new not in fieldnames:
            fieldnames[fieldnames.index(old)] = new
            for row in rows:
                row[new] = row.pop(old)
            changed = True
    if COVER_ATTR_COL in fieldnames:
        for row in rows:
            if row.get(COVER_ATTR_COL) != COVER_ATTRIBUTE or row.get(COVER_VALUES_COL) != COVER_VALUES:
                row[COVER_ATTR_COL] = COVER_ATTRIBUTE
                row[COVER_VALUES_COL] = COVER_VALUES
                changed = True
    print("Coin Cover: " + ("set Capsule,Box on every row." if changed else "already on every row, nothing to do."))
    return fieldnames, changed


def add_missing_columns(fieldnames, rows):
    missing = [(name, after, default) for name, after, default in NEW_COLUMNS if name not in fieldnames]
    if not missing:
        print("Columns: all target columns already present, nothing to do.")
        return fieldnames, False

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

    added = ", ".join(name for name, _a, _d in missing)
    print(f"Columns: added {added}.")
    return new_fieldnames, True


def add_dummy_client_rows(fieldnames, rows):
    if any(row.get("Product Category", "") == CLIENT_CATEGORY for row in rows):
        print("Client rows: '003 Kundenprodukte' rows already present, nothing to do.")
        return rows, False

    # Reuse the first real coin's images as placeholders for the dummy rows.
    template_row = next((r for r in rows if _is_numismatic_row(r)), rows[0])
    placeholder_rev = template_row.get("Reverse Image", "")
    placeholder_obv = template_row.get("Obverse Image", "")
    placeholder_img128 = template_row.get("Image 128", "")

    random.seed(RANDOM_SEED)
    new_rows = []
    for demo in DUMMY_CLIENT_PRODUCTS:
        row = {col: "" for col in fieldnames}
        row.update({
            "Currency": "CHF",
            "Activity State": "",
            "Product Category": CLIENT_CATEGORY,
            "WP Picture Reverse (small)": "",
            "WP Picture Obverse (small)": "",
            "Favorite": "FALSE",
            "Name": demo["Name"],
            "Internal Reference": demo["Internal Reference"],
            "Customer": demo["Customer"],
            "Customer Phone": demo["Customer Phone"],
            "Customer Email": demo["Customer Email"],
            "Sales Price": demo["Sales Price"],
            "Quantity On Hand": random.randint(QTY_MIN, QTY_MAX),
            COVER_ATTR_COL: COVER_ATTRIBUTE,
            COVER_VALUES_COL: COVER_VALUES,
            "Unit": "Units",
            "Reverse Image": placeholder_rev,
            "Obverse Image": placeholder_obv,
            "Image 128": placeholder_img128,
            "Last Updated on": "2026-09-23 12:00:00",
            "Show On Hand Qty Status Button": "TRUE",
        })
        new_rows.append(row)

    print(f"Client rows: added {len(new_rows)} dummy '003 Kundenprodukte' rows (clearly-fake test data).")
    return rows + new_rows, True


def force_zero_stock_samples(rows):
    changed = False
    for row in rows:
        if row.get("Internal Reference") in FORCE_ZERO_STOCK_REFS and row.get("Quantity On Hand") != "0":
            row["Quantity On Hand"] = "0"
            changed = True
    if changed:
        print(f"Stock: forced {sorted(FORCE_ZERO_STOCK_REFS)} to 0 coins left "
              f"(guaranteed test case for the zero-stock red styling).")
    else:
        print("Stock: zero-stock sample rows already set.")
    return rows, changed


def run():
    if not INPUT_CSV.exists():
        sys.exit(f"Input file not found: {INPUT_CSV}")

    csv.field_size_limit(sys.maxsize)
    with INPUT_CSV.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    # Rename legacy Coin Cover headers first, so the missing-column step
    # doesn't add the technical ones next to them.
    fieldnames, cover_changed = normalize_coin_cover(fieldnames, rows)
    fieldnames, cols_changed = add_missing_columns(fieldnames, rows)
    rows, rows_changed = add_dummy_client_rows(fieldnames, rows)
    rows, zero_changed = force_zero_stock_samples(rows) if "Quantity On Hand" in fieldnames else (rows, False)

    if not (cover_changed or cols_changed or rows_changed or zero_changed):
        print("Nothing to do.")
        return

    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved '{OUTPUT_CSV}' with {len(rows)} total rows.")


if __name__ == "__main__":
    run()
