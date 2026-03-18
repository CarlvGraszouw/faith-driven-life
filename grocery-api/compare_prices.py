import os
import requests
import json
import time
import sqlite3
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
DB_PATH = SCRIPT_DIR / "grocery_prices.db"

# Top ~100 common SA grocery items (expand as needed)
items = [
    "white bread 700g", "brown bread 700g", "maize meal 2.5kg", "rice 2kg", "pasta 500g",
    "flour 2.5kg", "sugar 2kg", "cooking oil 2L", "full cream milk 2L", "low fat milk 2L",
    "eggs large dozen", "butter 500g", "cheddar cheese 1kg", "plain yoghurt 1kg", "tea bags 100",
    "instant coffee 200g", "weetbix 450g", "cornflakes 500g", "oats 1kg", "potatoes 7kg",
    "onions 1kg", "tomatoes 1kg", "carrots 1kg", "cabbage each", "spinach bunch",
    "bananas 1kg", "apples 1kg", "oranges 1kg", "pears 1kg", "grapes 500g",
    "whole chicken 1.5kg", "chicken breasts 1kg", "beef mince 1kg", "boerewors 1kg", "pork sausages 500g",
    "canned baked beans 410g", "canned tuna 170g", "canned tomatoes 400g", "tomato sauce 700ml",
    "mayonnaise 750g", "peanut butter 400g", "jam strawberry 450g", "margarine 500g", "rusks 500g",
    "biscuits marie 200g", "chocolate bar 80g", "potato chips 125g", "biltong 100g", "droewors 100g",
    "coca cola 2L", "oros 2L", "fruit juice 1L", "sparkling water 1L", "beer 6 pack 330ml",
    "frozen peas 500g", "frozen mixed vegetables 1kg", "ice cream 2L", "frozen pizza 300g", "frozen fish fingers 400g",
    "beef stock cubes 12", "chicken stock cubes 12", "curry powder 100g", "salt 1kg", "black pepper 100g",
    "garlic clove", "ginger 100g", "chilli sauce 375ml", "soy sauce 150ml", "vinegar 750ml",
    "honey 500g", "cerevita 500g", "ace porridge 1kg", "tinned beef 300g", "polony 1kg",
    "bacon 200g", "ham 100g", "yoghurt flavoured 175g", "cream 250ml", "sour cream 250ml",
    "cottage cheese 250g", "feta cheese 200g", "mozzarella 300g", "bread rolls 6 pack", "hot dog rolls 6 pack",
    "hamburger buns 6 pack", "pita bread 6 pack", "naan bread 4 pack", "tortillas 8 pack", "couscous 500g",
    "quinoa 500g", "lentils 500g", "chickpeas 400g", "kidney beans 410g", "butter beans 410g",
    "sunflower seeds 200g", "almonds 200g", "cashews 200g", "raisins 250g", "dried apricots 250g",
    "popcorn kernels 500g", "noodles instant pack", "soup packet 50g", "bovril 125g", "marmite 125g",
]

stores = ["Shoprite", "Checkers", "Pick n Pay"]

# iGrosa via RapidAPI – get key from https://rapidapi.com, subscribe to iGrosa
API_HOST = "igrosa-api.p.rapidapi.com"
API_ENDPOINT = "/get_product"  # Adjust to actual iGrosa API docs


def get_api_key():
    key = os.environ.get("RAPIDAPI_KEY") or os.environ.get("RAPIDAPI_KEY_IGROSA")
    if not key or key == "YOUR_RAPIDAPI_KEY_HERE":
        return None
    return key


def get_price(item, store):
    api_key = get_api_key()
    if not api_key:
        return None
    try:
        url = f"https://{API_HOST}{API_ENDPOINT}"
        params = {"query": item, "store": store.lower().replace(" ", "")}
        headers = {"x-rapidapi-key": api_key, "x-rapidapi-host": API_HOST}
        response = requests.get(url, headers=headers, params=params, timeout=15)
        data = response.json()
        if data and "price" in data and data["price"] is not None:
            return float(data["price"])
        return None
    except Exception as e:
        print(f"Error fetching {item} from {store}: {e}")
        return None


def compare_prices():
    results = {}
    for item in items:
        prices = {}
        for store in stores:
            price = get_price(item, store)
            if price is not None:
                prices[store] = price
            time.sleep(1)
        if prices:
            best_store = min(prices, key=prices.get)
            results[item] = {"best_store": best_store, "price": prices[best_store], "all_prices": prices}
    return results


def add_crowdsourced_price(item, store, price, user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        """CREATE TABLE IF NOT EXISTS prices
           (item TEXT, store TEXT, price REAL, timestamp TEXT, user_id TEXT)"""
    )
    c.execute(
        "INSERT INTO prices VALUES (?, ?, ?, ?, ?)",
        (item, store, float(price), datetime.now().isoformat(), user_id),
    )
    conn.commit()
    conn.close()


def get_crowdsourced_price(item, store):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "SELECT AVG(price) FROM prices WHERE item=? AND store=? AND timestamp > date('now', '-1 day')",
        (item, store),
    )
    row = c.fetchone()
    conn.close()
    return float(row[0]) if row and row[0] is not None else None


if __name__ == "__main__":
    try:
        data = compare_prices()
    except Exception as e:
        print(f"Error during API comparison: {e}")
        data = {}

    # Hybrid: fill gaps with crowdsourced prices (last 24h average)
    for item in list(data.keys()):
        for store in stores:
            if store not in data[item]["all_prices"]:
                crowd_price = get_crowdsourced_price(item, store)
                if crowd_price is not None:
                    data[item]["all_prices"][store] = crowd_price
                    if crowd_price < data[item]["price"]:
                        data[item]["best_store"] = store
                        data[item]["price"] = crowd_price

    timestamp = datetime.now().strftime("%Y-%m-%d")
    out_file = SCRIPT_DIR / f"best_deals_{timestamp}.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

    print("Best deals for today:")
    if data:
        for item, info in data.items():
            print(f"{item}: {info['best_store']} at R{info['price']:.2f}")
    else:
        print("(No prices returned. Set RAPIDAPI_KEY and check iGrosa API docs/usage.)")
    print(f"\nSaved to {out_file}")
