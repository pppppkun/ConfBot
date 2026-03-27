# ConfBot

ConfBot crawls conference paper metadata, optionally generates keywords with an LLM, and visualizes the collected data in a Streamlit dashboard.

The project now uses `uv` for dependency management and Playwright for browser automation.

## Features

- Crawl paper titles, authors, and abstracts from conference program pages
- Save normalized metadata into a CSV file
- Generate keywords with an LLM-based pipeline
- Explore results in a Streamlit analysis dashboard

## Requirements

- Python `3.11+`
- `uv`

## Setup

```bash
uv sync
uv run playwright install chromium
```

If keyword generation depends on environment variables, create a `.env` file before running the keyword pipeline.

Example variables:

- `API_KEY`
- `BASE_URL`
- `MODEL`

## Usage

Run the crawler and keyword pipeline:

```bash
uv run python main.py
```

Run only the crawler for a specific track:

```bash
uv run python main.py --urls "https://conf.researchr.org/track/fse-2025/fse-2025-research-papers" --no-keyword
```

Launch the dashboard:

```bash
uv run streamlit run app.py
```

## Validation

Compile the main entrypoints:

```bash
uv run python -m py_compile crawler.py test_playwright.py main.py
```

Run the Playwright smoke test:

```bash
uv run python test_playwright.py
```

If Playwright reports that the browser executable is missing, run:

```bash
uv run playwright install chromium
```

## Project Files

- `crawler.py` - Playwright-based crawler
- `main.py` - CLI entrypoint for crawling and keyword generation
- `genkw.py` - keyword generation logic
- `analysis.py` - analysis helpers
- `app.py` - Streamlit dashboard

## Disclaimer

This project is intended strictly for academic research and educational use.
You are responsible for complying with the target website's Terms of Service and `robots.txt` policy.
The developer is not liable for any misuse or legal issues caused by using this code.
