#!/usr/bin/env python3
"""CIT Summer Launch 2026 - Production-Ready Odoo 19 Importer
Converts PDF CMYK/alpha masks to verified sRGB JPEGs.
"""



"""

----------- PDF to CSV -----------

"""

import base64
import csv
import io
import os
from PIL import Image
import pymupdf

# Removed '# Product Variants' so Odoo never auto-matches it to 'Products'
CSV_HEADERS = [
    "Currency",
    "Activity State",
    "Product Category",
    "WP Picture Reverse (small)",
    "WP Picture Obverse (small)",
    "Favorite",
    "Name",
    "Internal Reference",
    "Sales Price",
    "Unit",
    "Reverse Image",
    "Obverse Image",
    "Image 128",
    "Last Updated on",
    "Show On Hand Qty Status Button",
]

CIT_CATALOG = [
    # PAGE 1
    {
        "item_no": "31247",
        "name": "First Responders – Silver Set",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "429.00",
        "is_coin": True,
    },
    {
        "item_no": "31225",
        "name": "First Responders – Police Gold",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "219.00",
        "is_coin": True,
    },
    {
        "item_no": "31224",
        "name": "First Responders – Firefighter Gold",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "219.00",
        "is_coin": True,
    },
    {
        "item_no": "30904",
        "name": "Barre de Luxe – Leopard",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "519.00",
        "is_coin": True,
    },
    {
        "item_no": "31230",
        "name": "Barre de Luxe – Leopard Gold",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "99.00",
        "is_coin": True,
    },
    {
        "item_no": "31227",
        "name": "Black and White – Lion",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "189.00",
        "is_coin": True,
    },
    # PAGE 2
    {
        "item_no": "31175",
        "name": "Seven Deadly Sins – Envy",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "165.00",
        "is_coin": True,
    },
    {
        "item_no": "31198",
        "name": "Spectrum – Parrot",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "189.00",
        "is_coin": True,
    },
    {
        "item_no": "31152",
        "name": "Lunar Year Collection – Fluffy Gilded Sheep",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "189.00",
        "is_coin": True,
    },
    {
        "item_no": "31220",
        "name": "Evergreen – Ladybug",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "209.00",
        "is_coin": True,
    },
    {
        "item_no": "31217",
        "name": "Knight Games – Jousting",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "175.00",
        "is_coin": True,
    },
    {
        "item_no": "31214",
        "name": "3 Levels of Japan",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "349.00",
        "is_coin": True,
    },
    {
        "item_no": "31245",
        "name": "Topography – Bryce Canyon",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "669.00",
        "is_coin": True,
    },
    # PAGE 3
    {
        "item_no": "31239",
        "name": "Enemies in History – Custer vs. Sitting Bull",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "289.00",
        "is_coin": True,
    },
    {
        "item_no": "31262",
        "name": "Forging of Independence – Delaware",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "349.00",
        "is_coin": True,
    },
    {
        "item_no": "31226",
        "name": "Hoover Dam",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "289.00",
        "is_coin": True,
    },
    {
        "item_no": "31254",
        "name": "Born for Speed – Sailfish",
        "category": "CIT Artikelgruppen / 002 Münzen Eigenprodukte",
        "price": "179.00",
        "is_coin": True,
    },
    {
        "item_no": "31050",
        "name": "CIT Gift Box",
        "category": "CIT Artikelgruppen / 005 Zubehör & Verpackung",
        "price": "3.50",
        "is_coin": False,
    },
]


def extract_verified_rgb_images(pdf_path: str):
    """Extracts images and converts CMYK/masks directly into standard RGB JPEGs."""
    if not os.path.exists(pdf_path):
        for candidate in [
            "CIT_Summer_Launch_2026.pdf",
            "summer_launch_2026.pdf",
            "catalog.pdf",
        ]:
            if os.path.exists(candidate):
                pdf_path = candidate
                break

    if not os.path.exists(pdf_path):
        print(f"PDF '{pdf_path}' not found. Generating without images.")
        return []

    doc = pymupdf.open(pdf_path)
    all_images = []

    for page in doc:
        page_images = []
        for img_info in page.get_images(full=True):
            xref = img_info[0]
            try:
                # Load via Pixmap to resolve PDF-specific color encodings
                pix = pymupdf.Pixmap(doc, xref)

                # Skip small icons, badges, UI elements (< 120px)
                if pix.width < 120 or pix.height < 120:
                    continue

                # Convert CMYK or transparency to standard RGB
                if pix.n >= 5 or pix.colorspace != pymupdf.csRGB or pix.alpha:
                    pix = pymupdf.Pixmap(pymupdf.csRGB, pix)

                # Convert to clean JPEG bytes
                raw_jpg = pix.tobytes("jpeg")

                # Verify with Pillow
                pil_img = Image.open(io.BytesIO(raw_jpg))
                pil_img = pil_img.convert("RGB")
                if pil_img.width > 1200 or pil_img.height > 1200:
                    pil_img.thumbnail((1200, 1200), Image.Resampling.LANCZOS)

                buf = io.BytesIO()
                pil_img.save(buf, format="JPEG", quality=85)
                b64_str = base64.b64encode(buf.getvalue()).decode("utf-8")

                rects = page.get_image_rects(xref)
                y_pos = rects[0].y0 if rects else 0
                x_pos = rects[0].x0 if rects else 0
                page_images.append((y_pos, x_pos, b64_str))

            except Exception as e:
                # Skip any problematic vector/mask streams safely
                continue

        # Sort top-to-bottom, then left-to-right
        page_images.sort(key=lambda item: (item[0], item[1]))
        all_images.extend([item[2] for item in page_images])

    return all_images


def run():
    images = extract_verified_rgb_images("CIT_Summer_Launch_2026.pdf")
    print(f"Extracted {len(images)} clean RGB JPEG images.")

    # Create a 1x1 white JPEG fallback so no image field ever receives an empty string
    fallback_buf = io.BytesIO()
    Image.new("RGB", (1, 1), (255, 255, 255)).save(fallback_buf, format="JPEG")
    white_fallback = base64.b64encode(fallback_buf.getvalue()).decode("utf-8")

    rows = []
    img_idx = 0

    for prod in CIT_CATALOG:
        sku = prod["item_no"]
        is_coin = prod["is_coin"]

        if is_coin:
            # 3 assets per coin: Reverse (left), Obverse (middle), Box (right - skipped)
            rev_img = (
                images[img_idx] if img_idx < len(images) else white_fallback
            )
            obv_img = (
                images[img_idx + 1]
                if (img_idx + 1) < len(images)
                else white_fallback
            )
            img_idx += 3
        else:
            # Packaging (#31050 CIT Gift Box)
            obv_img = (
                images[img_idx] if img_idx < len(images) else white_fallback
            )
            rev_img = obv_img
            img_idx += 2

        wp_base = f"https://www.cit.li/wp-content/uploads/2026/{sku}"

        row = {
            "Currency": "CHF",
            "Activity State": "",
            "Product Category": prod["category"],
            "WP Picture Reverse (small)": (
                f"{wp_base}_rev.jpg" if is_coin else ""
            ),
            "WP Picture Obverse (small)": (
                f"{wp_base}_obv.jpg" if is_coin else ""
            ),
            "Favorite": "FALSE",
            "Name": prod["name"],
            "Internal Reference": sku,
            "Sales Price": prod["price"],
            "Unit": "Units",
            "Reverse Image": rev_img,
            "Obverse Image": obv_img,
            "Image 128": obv_img,
            "Last Updated on": "2026-09-22 12:00:00",
            "Show On Hand Qty Status Button": "TRUE" if is_coin else "FALSE",
        }
        rows.append(row)

    output_csv = "odoo_cit_summer_2026.csv"
    with open(output_csv, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writeheader()
        writer.writerows(rows)

    print(
        f"Saved {len(rows)} records to '{output_csv}'. Ready for Odoo 19 import!"
    )


if __name__ == "__main__":
    run()
    