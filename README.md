# Codex-2

This repository contains a simple Python script to display urgent Bitcoin news from various RSS feeds.

## Usage

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the script:

```bash
python bitcoin_news.py
```

If a feed cannot be retrieved (for example due to network restrictions), the
script prints a warning and continues.

You can specify custom feeds or limit the number of headlines shown:

```bash
python bitcoin_news.py --feeds <feed1> <feed2> --limit 5
```



