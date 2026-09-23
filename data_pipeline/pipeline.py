from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd
import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/catalogue/page-{}.html"
ROOT = Path(__file__).resolve().parent
DB_PATH = ROOT / "artifacts" / "books.db"
OUTPUT_PATH = ROOT / "artifacts" / "query_results.md"
RATE = 105.50
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def scrape_books(pages: int = 5) -> pd.DataFrame:
    rows = []
    for page_no in range(1, pages + 1):
        response = requests.get(BASE.format(page_no), timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for card in soup.select("article.product_pod"):
            title_node = card.select_one("h3 a")
            price_node = card.select_one(".price_color")
            rating_node = card.select_one("p.star-rating")
            availability_node = card.select_one(".availability")
            rows.append(
                {
                    "title": title_node.get("title", "").strip() if title_node else "",
                    "price": price_node.get_text(" ", strip=True) if price_node else "",
                    "star_rating": next((c for c in (rating_node.get("class", []) if rating_node else []) if c != "star-rating"), ""),
                    "availability": availability_node.get_text(" ", strip=True) if availability_node else "",
                    "category": "Books",
                }
            )
    return pd.DataFrame(rows)


def clean_books(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    # The site can arrive with a mojibake prefix ("Â£") under an imperfect
    # response decoding, so retain only numeric price characters.
    df["price_gbp"] = pd.to_numeric(df["price"].str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
    df["rating"] = df["star_rating"].map(RATING_MAP).astype("float64")
    df["in_stock"] = df["availability"].str.contains("In stock", case=False, na=False)
    for column in ["price_gbp", "rating"]:
        df[column] = df[column].fillna(df[column].median())
    df["rating"] = df["rating"].round().astype(int)
    df["price_inr"] = (df["price_gbp"] * RATE).round(2)
    df["category"] = df["category"].fillna("Books")
    return df[["title", "price_gbp", "price_inr", "rating", "in_stock", "category"]]


def load_database(df: pd.DataFrame) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        conn.executescript("""
        DROP TABLE IF EXISTS books;
        DROP TABLE IF EXISTS categories;
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT UNIQUE NOT NULL
        );
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            price_gbp REAL NOT NULL,
            price_inr REAL NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            in_stock INTEGER NOT NULL,
            category_id INTEGER NOT NULL REFERENCES categories(category_id)
        );
        """)
        categories = pd.DataFrame({"category_name": sorted(df["category"].unique())})
        categories.to_sql("categories", conn, if_exists="append", index=False)
        category_ids = pd.read_sql("SELECT category_id, category_name FROM categories", conn)
        books = df.merge(category_ids, left_on="category", right_on="category_name")
        books["in_stock"] = books["in_stock"].astype(int)
        books[["title", "price_gbp", "price_inr", "rating", "in_stock", "category_id"]].to_sql(
            "books", conn, if_exists="append", index=False
        )


def run_queries(df: pd.DataFrame) -> None:
    queries = {
        "1_select_where": "SELECT title, price_gbp FROM books WHERE rating >= 4 ORDER BY price_gbp DESC LIMIT 10;",
        "2_distinct": "SELECT DISTINCT category_name FROM categories ORDER BY category_name;",
        "3_between": "SELECT title, price_inr FROM books WHERE price_gbp BETWEEN 10 AND 30 ORDER BY price_inr LIMIT 10;",
        "4_in": "SELECT title, rating FROM books WHERE rating IN (1, 5) ORDER BY rating DESC, title LIMIT 10;",
        "5_join": "SELECT c.category_name, b.title, b.rating, b.price_inr FROM books b JOIN categories c ON b.category_id = c.category_id ORDER BY b.rating DESC, b.price_inr DESC LIMIT 10;",
    }
    lines = ["# Executed SQL results", "", f"Dataset rows: **{len(df)}**", f"Fixed rate: **1 GBP = {RATE:.2f} INR**", ""]
    with sqlite3.connect(DB_PATH) as conn:
        for name, sql in queries.items():
            result = pd.read_sql(sql, conn)
            lines.extend([f"## {name}", "```sql", sql, "```", "", result.to_markdown(index=False), ""])
        sql_join = queries["5_join"]
        sql_result = pd.read_sql(sql_join, conn)
        books = pd.read_sql("SELECT * FROM books", conn)
        categories = pd.read_sql("SELECT * FROM categories", conn)
    merged = books.merge(categories, on="category_id")
    merged_result = merged[["category_name", "title", "rating", "price_inr"]].sort_values(
        ["rating", "price_inr"], ascending=[False, False]
    ).head(10).reset_index(drop=True)
    lines.extend(["## SQL JOIN versus pandas.merge", "The following two outputs are equivalent after resetting the index.", "", "### `pd.read_sql`", sql_result.to_markdown(index=False), "", "### `pd.merge`", merged_result.to_markdown(index=False), "", f"Equivalent: **{sql_result.reset_index(drop=True).equals(merged_result)}**"])
    OUTPUT_PATH.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    raw = scrape_books()
    cleaned = clean_books(raw)
    if len(cleaned) < 60:
        raise RuntimeError(f"Expected at least 60 books, received {len(cleaned)}")
    load_database(cleaned)
    run_queries(cleaned)
    print(f"Scraped and loaded {len(cleaned)} books into {DB_PATH}")
    print(f"Query outputs written to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
