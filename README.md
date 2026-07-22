# Investment Analyzer

A personal tool for screening Brazilian stocks and REITs (FIIs), managing a portfolio, and visualizing price history — built with real market data.

Originally built for personal use as part of a long-term dividend investing strategy, but designed to be useful for anyone getting started with the Brazilian stock market.

---

## What it does

**Screener** — analyzes a list of stocks and REITs and ranks them by a combined score based on dividend yield, price-to-book ratio, and dividend consistency. Results are saved as a dated CSV file.

**Portfolio tracker** — keeps a local record of your positions. Tracks average cost, current price, profit/loss, and estimated monthly income from dividends. Updates in real time every time you run it.

**Price history chart** — generates a 12-month price chart with a 30-day moving average for any asset in the screener. Can be saved as a PDF.

---

## Scoring method

Each asset receives a score from 0 to 10 based on three factors:

- **Dividend Yield** (up to 4 points) — higher yield relative to price scores higher
- **P/VP — Price to Book** (up to 3 points) — assets trading below book value score higher
- **Consistency** (up to 3 points) — number of dividend payments in the last 12 months

This avoids ranking assets purely by yield, which can be misleading when a high DY comes from a falling price.

---

## Stack

- Python
- yfinance
- pandas
- matplotlib

---

## How to use

Clone the repository and install dependencies:

```bash
git clone https://github.com/LuisOtavioo/investment-analyzer.git
cd investment-analyzer
python3 -m venv .venv
source .venv/bin/activate
pip install yfinance pandas matplotlib
```

Run:

```bash
python screener.py
```

Menu options:

```
[1] Run screener
[2] Add purchase to portfolio
[3] Remove asset from portfolio
[4] Analyze portfolio
[0] Exit
```

---

## Portfolio

Positions are saved locally in `carteira.csv`. Each time you make a new purchase of an asset already in the portfolio, the quantity and average cost are updated automatically.

Screener results are saved in the `resultados/` folder with the date in the filename, so you can track how rankings change over time.

---

## Default assets

The screener comes with a starter list that mixes dividend-paying stocks and REITs:

`BBAS3, TAEE11, EGIE3, ITUB4, VALE3, VIVT3, MXRF11, HGLG11, XPML11`

You can edit this list directly in `screener.py` to add or remove assets.

---

## Author

[Luís Otávio](https://github.com/LuisOtavioo) — Back-end developer and Physics student at UNESP, building projects at the intersection of finance and code.
