#!/usr/bin/env python3

import argparse
import csv
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(
        description="Create a CSV containing the header and a specified number of data lines."
    )
    parser.add_argument("csv_file", type=Path, help="Input CSV file")
    parser.add_argument(
        "lines",
        type=int,
        help="Number of data lines to include (0 = header only)",
    )

    args = parser.parse_args()

    if not args.csv_file.is_file():
        parser.error(f"File does not exist: {args.csv_file}")

    if args.lines < 0:
        parser.error("Number of lines cannot be negative")

    output_file = args.csv_file.with_name(
        f"{args.csv_file.stem}_{args.lines}{args.csv_file.suffix}"
    )

    with args.csv_file.open("r", newline="", encoding="utf-8") as infile:
        reader = csv.reader(infile)

        try:
            header = next(reader)
        except StopIteration:
            parser.error("CSV file is empty")

        with output_file.open("w", newline="", encoding="utf-8") as outfile:
            writer = csv.writer(outfile)

            # Always write header
            writer.writerow(header)

            # Write requested number of data rows
            for i, row in enumerate(reader):
                if i >= args.lines:
                    break
                writer.writerow(row)

    print(f"Created: {output_file}")


if __name__ == "__main__":
    main()
    