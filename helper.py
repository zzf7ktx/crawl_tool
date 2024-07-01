"""
This module provides helper functions for scraping.
"""

from bs4 import BeautifulSoup
import json
import random
import string
import pandas as pd
import os


def create_random_dir(prefix="", suffix=""):
    new_dir = f"{prefix}{random_word(5)}{suffix}"
    os.makedirs(new_dir)
    return new_dir


def to_soup(driver):
    html = driver.page_source
    soup = BeautifulSoup(html, "html.parser")
    return soup


def array_to_json(arr=[], file_name="json_file"):
    with open(f"{file_name}.json", "w") as f:
        json.dump(arr, f)


def random_word(length):
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))


def stringify_image_fields(images):
    return ", ".join([f'{image["src"]}' for image in images])


def to_shopify_template(products, export_csv=False, csv_name="shopify_products"):
    all_rows = []
    for product in products:
        base_row = {
            "Title": product["title"],
            "Body (HTML)": product["description"],
            "Image Src": stringify_image_fields(product["images"]),
        }
        variations = product.get("variations", [])
        num_variations = len(variations)
        max_options = max([len(v["options"]) for v in variations], default=0)

        for i in range(max_options):
            row = base_row.copy()
            for j in range(num_variations):
                if i < len(variations[j]["options"]):
                    row[f"Option{j+1} Name"] = variations[j]["name"]
                    row[f"Option{j+1} Value"] = variations[j]["options"][i]
                if i > 0:
                    row["Title"] = None
                    row["Body (HTML)"] = None
                    row["Image Src"] = None
                    row[f"Option{j+1} Name"] = None
            all_rows.append(row)

    df = pd.DataFrame(all_rows)

    if export_csv:
        df.to_csv(f"{csv_name}.csv", index=False)
    return df
