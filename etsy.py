"""
This module provides functions for scraping product links from Etsy using Selenium and BeautifulSoup.
"""

from bs4 import BeautifulSoup
from selenium import webdriver
import time
from urllib.parse import urlparse
import helper as hp
import requests


def get_all_product_links(driver, search_url, number_of_products=48):
    gotProducts = []
    page = 1
    error_count = 0
    while len(gotProducts) < number_of_products and error_count < 50:
        print("Getting all product links in page {0} ...".format(page))
        url = search_url + "&page={0}".format(page) if page > 1 else search_url
        page += 1

        try:
            driver.delete_all_cookies()
            driver.get(url)
            time.sleep(2)
            driver.get(url)
            time.sleep(2)
            soup = hp.to_soup(driver)
            products = soup.find("ol", "tab-reorder-container").findAll(
                "a", "listing-link"
            )

            if len(products) < 1:
                break

            for product in products:
                gotProducts.append(product.attrs["href"])
                if len(gotProducts) == number_of_products:
                    break

            print("Done (got ", len(gotProducts), ")")
        except Exception as ex:
            print(f"Error: {ex}.")
            error_count += 1
            continue

    return gotProducts[: number_of_products + 1]


def get_all_product_links_shop(driver, shop_url, number_of_products=48):
    gotProducts = []

    # driver.get(shop_url)
    # time.sleep(5)
    # driver.delete_all_cookies()
    # driver.get(shop_url)
    # time.sleep(2)
    # driver.get(shop_url)
    # soup = to_soup(driver)
    shop_id = shop_url.split("/shop/")[1]

    # shop_id = soup.find('div', 'js-merch-stash-check-listing').attrs['data-shop-id']
    # print(f"shopId: {shop_id}")
    limit = 36
    page = 1
    while len(gotProducts) < number_of_products:
        print("Getting all product links in page {0} ...".format(page))
        url = f"https://www.etsy.com/api/v3/ajax/bespoke/member/shops/{shop_id}/listings-view?limit={limit}&offset={limit * (page - 1)}&sort_order=custom"
        res = requests.get(url)
        res_ = res.json()
        soup = BeautifulSoup(res_["html"], "html.parser")
        products = soup.find("div", "responsive-listing-grid").findAll(
            "a", "listing-link"
        )

        if len(products) < 1:
            break

        for product in products:
            gotProducts.append(product.attrs["href"])
            if len(gotProducts) == number_of_products:
                break

        print("Done (got ", len(gotProducts), ")")
        page += 1
    return gotProducts


# Function getting product info
def get_product_info(driver, product_url):
    driver.delete_all_cookies()
    driver.get(product_url)
    time.sleep(2)
    driver.get(product_url)
    time.sleep(2)
    soup = hp.to_soup(driver)

    # Get all images
    image_elms = soup.findAll("img", "carousel-image")
    images = []

    for img in image_elms:
        alt = img.attrs["alt"]
        src = img.attrs["src"]
        images.append({"alt": alt, "src": src})

    # Get raw price
    rawPrice = (
        soup.find("div", {"data-buy-box-region": "price"})
        .find("p", "wt-text-title-larger")
        .contents[-1]
        .getText()
        .strip()
    )

    # Get options
    variation_elms = soup.find(
        "div", {"data-selector": "listing-page-variations"}
    ).findAll("div", {"data-selector": "listing-page-variation"})
    options = []
    for variant_elm in variation_elms:
        variant_name = variant_elm.find("label").getText().strip()
        option_elms = variant_elm.find("select").findAll("option")
        variant_options = []
        for opt in option_elms:
            if opt.attrs["value"] == "":
                continue
            text = opt.text
            temp = text.split("(")
            key = temp[0].strip()
            variant_options.append(key)
        options.append({"name": variant_name, "options": variant_options})

    # Get title
    title = soup.find("h1", {"data-buy-box-listing-title": "true"}).text.strip()
    # Get detail
    detail = soup.find("h1", {"data-buy-box-listing-title": "true"}).getText().strip()

    return {
        "title": title,
        "price": rawPrice,
        "description": detail,
        "images": images,
        "variations": options,
    }


def get_driver_options():
    options = webdriver.ChromeOptions()
    my_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
    options.add_argument(f"--user-agent={my_user_agent}")
    options.add_argument("--start-maximized")


def crawl(url, number_of_items=48):
    options = get_driver_options()
    driver = webdriver.Chrome(options=options)
    path = hp.create_random_dir("result/")

    # Get links
    product_links = []

    # Check if shop or search
    if "/shop/" in url:
        product_links = get_all_product_links_shop(driver, url, number_of_items)
    else:
        product_links = get_all_product_links(driver, url, number_of_items)
    hp.array_to_json(product_links, f"{path}/product_links")

    products = []
    for link in product_links:
        try:
            product = get_product_info(driver, link)
            products.append(product)
        except Exception as ex:
            print(f"Error: {ex}")
            continue

    hp.array_to_json(products, f"{path}/products")
    return products, path


def isEtsy(url):
    url = urlparse(url)
    return url.hostname.find("etsy.com") > -1
