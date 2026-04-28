"""
Multi-market news scraper — fetches commodity news for India, US, and China
via RSS feeds and web scraping.
"""

import requests
import feedparser
import logging
from typing import List, Dict, Any
from datetime import datetime
from bs4 import BeautifulSoup

from backend.config import MARKETS
from backend.data.storage import save_news, clear_old_news

logger = logging.getLogger(__name__)

# ── RSS Feed URLs (market-specific) ────────────────────────
NEWS_FEEDS = {
    "moneycontrol": [
        "https://www.moneycontrol.com/rss/commodities.xml",
    ],
    "economic_times": [
        "https://economictimes.indiatimes.com/rssfeedstopstories.cms",
    ],
    "reuters": [
        "https://news.google.com/rss/search?q=gold+silver+copper+commodities+COMEX&hl=en-US&gl=US&ceid=US:en",
    ],
    "cnbc": [
        "https://news.google.com/rss/search?q=gold+silver+copper+commodities+CNBC&hl=en-US&gl=US&ceid=US:en",
    ],
    "sina_finance": [
        "https://news.google.com/rss/search?q=gold+silver+copper+SHFE+China+commodities&hl=en&gl=US&ceid=US:en",
    ],
    "eastmoney": [
        "https://news.google.com/rss/search?q=China+metals+gold+silver+copper+Shanghai&hl=en&gl=US&ceid=US:en",
    ],
}

# ── Commodity Keywords for Filtering ───────────────────────
COMMODITY_KEYWORDS = [
    "gold", "silver", "copper", "metal", "commodity", "commodities",
    "MCX", "COMEX", "SHFE", "bullion", "precious",
    "सोना", "चांदी", "तांबा",  # Hindi
    "黄金", "白银", "铜",  # Chinese
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def _parse_rss_feed(url: str, source_name: str) -> List[Dict[str, Any]]:
    """Parse an RSS feed and return structured articles."""
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:15]:  # Limit to 15 per feed
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))

            # Strip HTML from summary
            if summary:
                summary = BeautifulSoup(summary, "html.parser").get_text()[:500]

            pub_date = ""
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    pub_date = datetime(*entry.published_parsed[:6]).strftime("%Y-%m-%d %H:%M")
                except Exception:
                    pub_date = entry.get("published", "")

            articles.append({
                "title": title,
                "source": source_name,
                "date": pub_date,
                "url": entry.get("link", ""),
                "summary": summary,
            })
    except Exception as e:
        logger.warning(f"Error parsing RSS {url}: {e}")

    return articles


def _scrape_moneycontrol_commodities() -> List[Dict[str, Any]]:
    """Scrape Moneycontrol commodity headlines."""
    articles = []
    try:
        url = "https://www.moneycontrol.com/news/business/commodities/"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            headlines = soup.find_all("h2", limit=10)
            for h in headlines:
                link = h.find("a")
                if link:
                    articles.append({
                        "title": link.get_text(strip=True),
                        "source": "Moneycontrol",
                        "date": datetime.now().strftime("%Y-%m-%d"),
                        "url": link.get("href", ""),
                        "summary": "",
                    })
    except Exception as e:
        logger.warning(f"Error scraping Moneycontrol: {e}")
    return articles


def fetch_news_for_market(market: str) -> List[Dict[str, Any]]:
    """Fetch news articles for a specific market from configured sources."""
    market_config = MARKETS.get(market)
    if not market_config:
        logger.warning(f"Unknown market: {market}")
        return []

    all_articles = []

    for source in market_config["news_sources"]:
        # Try direct scraping for Moneycontrol
        if source == "moneycontrol":
            scraped = _scrape_moneycontrol_commodities()
            all_articles.extend(scraped)

        # Try RSS feeds
        feed_urls = NEWS_FEEDS.get(source, [])
        for url in feed_urls:
            articles = _parse_rss_feed(url, source.replace("_", " ").title())
            all_articles.extend(articles)

    # Filter for commodity-relevant articles
    filtered = []
    for article in all_articles:
        text = f"{article['title']} {article['summary']}".lower()
        if any(kw.lower() in text for kw in COMMODITY_KEYWORDS):
            filtered.append(article)

    # If filter is too aggressive, keep all
    if len(filtered) < 3:
        filtered = all_articles[:15]

    # Deduplicate by title
    seen_titles = set()
    unique_articles = []
    for article in filtered:
        title_key = article["title"].strip().lower()
        if title_key not in seen_titles:
            seen_titles.add(title_key)
            article["market"] = market
            unique_articles.append(article)

    return unique_articles[:20]  # Cap at 20


def ingest_news_for_market(market: str) -> int:
    """Fetch and save news for a market. Returns number of articles saved."""
    articles = fetch_news_for_market(market)
    if articles:
        save_news(market, articles)
    logger.info(f"📰 {market}: {len(articles)} news articles ingested")
    return len(articles)


def ingest_news_all_markets() -> Dict[str, int]:
    """Fetch and save news for all markets."""
    clear_old_news(days=7)
    results = {}
    for market_key in MARKETS:
        try:
            count = ingest_news_for_market(market_key)
            results[market_key] = count
        except Exception as e:
            logger.error(f"Error fetching news for {market_key}: {e}")
            results[market_key] = 0
    return results
