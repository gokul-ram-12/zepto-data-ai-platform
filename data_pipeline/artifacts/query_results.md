# Executed SQL results

Dataset rows: **100**
Fixed rate: **1 GBP = 105.50 INR**

## 1_select_where
```sql
SELECT title, price_gbp FROM books WHERE rating >= 4 ORDER BY price_gbp DESC LIMIT 10;
```

| title                                                                                                     |   price_gbp |
|:----------------------------------------------------------------------------------------------------------|------------:|
| The Death of Humanity: and the Case for Life                                                              |       58.11 |
| The Past Never Ends                                                                                       |       56.5  |
| Sapiens: A Brief History of Humankind                                                                     |       54.23 |
| Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)                                                   |       52.29 |
| Behind Closed Doors                                                                                       |       52.22 |
| We Love You, Charlie Freeman                                                                              |       50.27 |
| Sharp Objects                                                                                             |       47.82 |
| Private Paris (Private #10)                                                                               |       47.61 |
| Wall and Piece                                                                                            |       44.18 |
| Unseen City: The Majesty of Pigeons, the Discreet Charm of Snails & Other Wonders of the Urban Wilderness |       44.18 |

## 2_distinct
```sql
SELECT DISTINCT category_name FROM categories ORDER BY category_name;
```

| category_name   |
|:----------------|
| Books           |

## 3_between
```sql
SELECT title, price_inr FROM books WHERE price_gbp BETWEEN 10 AND 30 ORDER BY price_inr LIMIT 10;
```

| title                                                                               |   price_inr |
|:------------------------------------------------------------------------------------|------------:|
| Patience                                                                            |     1071.88 |
| In Her Wake                                                                         |     1354.62 |
| Princess Between Worlds (Wide-Awake Princess #5)                                    |     1407.37 |
| Princess Jellyfish 2-in-1 Omnibus, Vol. 01 (Princess Jellyfish 2-in-1 Omnibus #1)   |     1435.86 |
| Starving Hearts (Triangular Trade Trilogy, #1)                                      |     1475.94 |
| Mama Tried: Traditional Italian Cooking for the Screwed, Crude, Vegan, and Tattooed |     1479.11 |
| On a Midnight Clear                                                                 |     1484.38 |
| Untitled Collection: Sabbath Poems 2014                                             |     1505.48 |
| Obsidian (Lux #1)                                                                   |     1567.73 |
| Outcast, Vol. 1: A Darkness Surrounds Him (Outcast #1)                              |     1628.92 |

## 4_in
```sql
SELECT title, rating FROM books WHERE rating IN (1, 5) ORDER BY rating DESC, title LIMIT 10;
```

| title                                                                             |   rating |
|:----------------------------------------------------------------------------------|---------:|
| #HigherSelfie: Wake Up Your Life. Free Your Soul. Find Your Tribe.                |        5 |
| Black Dust                                                                        |        5 |
| Chase Me (Paris Nights #2)                                                        |        5 |
| Join                                                                              |        5 |
| Princess Between Worlds (Wide-Awake Princess #5)                                  |        5 |
| Princess Jellyfish 2-in-1 Omnibus, Vol. 01 (Princess Jellyfish 2-in-1 Omnibus #1) |        5 |
| Private Paris (Private #10)                                                       |        5 |
| Rip it Up and Start Again                                                         |        5 |
| Sapiens: A Brief History of Humankind                                             |        5 |
| Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)                           |        5 |

## 5_join
```sql
SELECT c.category_name, b.title, b.rating, b.price_inr FROM books b JOIN categories c ON b.category_id = c.category_id ORDER BY b.rating DESC, b.price_inr DESC LIMIT 10;
```

| category_name   | title                                                               |   rating |   price_inr |
|:----------------|:--------------------------------------------------------------------|---------:|------------:|
| Books           | Sapiens: A Brief History of Humankind                               |        5 |     5721.26 |
| Books           | Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)             |        5 |     5516.6  |
| Books           | We Love You, Charlie Freeman                                        |        5 |     5303.48 |
| Books           | Private Paris (Private #10)                                         |        5 |     5022.85 |
| Books           | Worlds Elsewhere: Journeys Around Shakespeareâs Globe             |        5 |     4251.65 |
| Books           | Join                                                                |        5 |     3763.19 |
| Books           | Rip it Up and Start Again                                           |        5 |     3694.61 |
| Books           | Black Dust                                                          |        5 |     3642.92 |
| Books           | The Activist's Tao Te Ching: Ancient Advice for a Modern Revolution |        5 |     3401.32 |
| Books           | Chase Me (Paris Nights #2)                                          |        5 |     2665.98 |

## SQL JOIN versus pandas.merge
The following two outputs are equivalent after resetting the index.

### `pd.read_sql`
| category_name   | title                                                               |   rating |   price_inr |
|:----------------|:--------------------------------------------------------------------|---------:|------------:|
| Books           | Sapiens: A Brief History of Humankind                               |        5 |     5721.26 |
| Books           | Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)             |        5 |     5516.6  |
| Books           | We Love You, Charlie Freeman                                        |        5 |     5303.48 |
| Books           | Private Paris (Private #10)                                         |        5 |     5022.85 |
| Books           | Worlds Elsewhere: Journeys Around Shakespeareâs Globe             |        5 |     4251.65 |
| Books           | Join                                                                |        5 |     3763.19 |
| Books           | Rip it Up and Start Again                                           |        5 |     3694.61 |
| Books           | Black Dust                                                          |        5 |     3642.92 |
| Books           | The Activist's Tao Te Ching: Ancient Advice for a Modern Revolution |        5 |     3401.32 |
| Books           | Chase Me (Paris Nights #2)                                          |        5 |     2665.98 |

### `pd.merge`
| category_name   | title                                                               |   rating |   price_inr |
|:----------------|:--------------------------------------------------------------------|---------:|------------:|
| Books           | Sapiens: A Brief History of Humankind                               |        5 |     5721.26 |
| Books           | Scott Pilgrim's Precious Little Life (Scott Pilgrim #1)             |        5 |     5516.6  |
| Books           | We Love You, Charlie Freeman                                        |        5 |     5303.48 |
| Books           | Private Paris (Private #10)                                         |        5 |     5022.85 |
| Books           | Worlds Elsewhere: Journeys Around Shakespeareâs Globe             |        5 |     4251.65 |
| Books           | Join                                                                |        5 |     3763.19 |
| Books           | Rip it Up and Start Again                                           |        5 |     3694.61 |
| Books           | Black Dust                                                          |        5 |     3642.92 |
| Books           | The Activist's Tao Te Ching: Ancient Advice for a Modern Revolution |        5 |     3401.32 |
| Books           | Chase Me (Paris Nights #2)                                          |        5 |     2665.98 |

Equivalent: **True**