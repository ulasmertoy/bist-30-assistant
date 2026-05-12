from pathlib import Path
from datetime import datetime
import hashlib
import time

import requests
import pandas as pd
from bs4 import BeautifulSoup


BIST30_COMPANIES = {
    "AKBNK": ["AKBNK", "Akbank"],
    "ARCLK": ["ARCLK", "Arçelik", "Arcelik"],
    "ASELS": ["ASELS", "Aselsan"],
    "BIMAS": ["BIMAS", "BİM", "BIM"],
    "EKGYO": ["EKGYO", "Emlak Konut"],
    "EREGL": ["EREGL", "Ereğli", "Eregli"],
    "FROTO": ["FROTO", "Ford Otosan"],
    "GARAN": ["GARAN", "Garanti"],
    "KCHOL": ["KCHOL", "Koç Holding", "Koc Holding"],
    "MGROS": ["MGROS", "Migros"],
    "PETKM": ["PETKM", "Petkim"],
    "PGSUS": ["PGSUS", "Pegasus"],
    "SAHOL": ["SAHOL", "Sabancı Holding", "Sabanci Holding"],
    "SISE": ["SISE", "Şişecam", "Sisecam"],
    "TAVHL": ["TAVHL", "TAV"],
    "TCELL": ["TCELL", "Turkcell"],
    "THYAO": ["THYAO", "THY", "Türk Hava Yolları", "Turkish Airlines"],
    "TOASO": ["TOASO", "Tofaş", "Tofas"],
    "TUPRS": ["TUPRS", "Tüpraş", "Tupras"],
    "YKBNK": ["YKBNK", "Yapı Kredi", "Yapi Kredi"],
}


def make_news_id(url: str, title: str) -> str:
    raw = f"{url}_{title}"
    return hashlib.md5(raw.encode("utf-8")).hexdigest()


def match_tickers(text: str) -> list[str]:
    text_lower = text.lower()
    matched = []

    for ticker, aliases in BIST30_COMPANIES.items():
        for alias in aliases:
            if alias.lower() in text_lower:
                matched.append(ticker)
                break

    return matched


def scrape_bloomberght() -> pd.DataFrame:
    url = "https://www.bloomberght.com/tumhaberler"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    records = []

    for a in soup.find_all("a", href=True):
        title = a.get_text(" ", strip=True)
        href = a["href"]

        if len(title) < 30:
            continue

        if href.startswith("/"):
            href = "https://www.bloomberght.com" + href

        tickers = match_tickers(title)

        records.append({
            "news_id": make_news_id(href, title),
            "source": "bloomberght",
            "published_at": None,
            "title": title,
            "summary": None,
            "url": href,
            "matched_tickers": tickers,
            "market_tag": "stock_specific" if tickers else "general_market",
            "scraped_at": datetime.now().isoformat(timespec="seconds"),
        })

    df = pd.DataFrame(records)

    if len(df) == 0:
        return df

    df = df.drop_duplicates(subset=["news_id"])
    return df


def scrape_all_news(delay: float = 1.0) -> pd.DataFrame:
    all_dfs = []

    print("Fetching Bloomberg HT...")
    try:
        df_bloomberg = scrape_bloomberght()
        print(f"  ✅ {len(df_bloomberg)} haber çekildi")
        all_dfs.append(df_bloomberg)
    except Exception as e:
        print(f"  ❌ Bloomberg HT hata: {e}")

    time.sleep(delay)

    if not all_dfs:
        return pd.DataFrame()

    return pd.concat(all_dfs, ignore_index=True)


if __name__ == "__main__":
    out_dir = Path("../data/raw/news")
    out_dir.mkdir(parents=True, exist_ok=True)

    df = scrape_all_news()

    output_path = out_dir / "news_raw.parquet"
    df.to_parquet(output_path, index=False)

    print(f"\n✅ Kaydedildi: {output_path}")
    print(f"Toplam haber: {len(df)}")

    if len(df) > 0:
        print(df["market_tag"].value_counts())
