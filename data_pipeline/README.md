# Data Pipeline

Run `python data_pipeline/pipeline.py` from the repository root. The script scrapes five catalogue pages from Books to Scrape, producing 100 rows across the allowed catalogue scope. It uses `requests` and `BeautifulSoup`, strips the GBP symbol, maps ratings to integers, parses stock status as Boolean, and imputes unexpected numeric parse failures with the column median.

The required fixed conversion is **1 GBP = 105.50 INR**. No live exchange-rate lookup is used. The normalized SQLite schema contains `categories` and `books`, linked by `books.category_id`.

The script writes `artifacts/books.db` and `artifacts/query_results.md`. The results file includes five SQL queries covering filtering, ordering, limiting, distinct values, `BETWEEN`, `IN`, and a join. It also shows `pd.read_sql` results beside an equivalent `pd.merge` result.

## References

[1]: http://books.toscrape.com "Books to Scrape public scraping-practice site"
[2]: https://docs.python.org/3/library/sqlite3.html "Python sqlite3 documentation"
