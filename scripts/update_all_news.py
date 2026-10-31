import feedparser
import json
import os
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

VN_TZ = timezone(timedelta(hours=7))
JSON_PATH = "src/data/all_news.json"
MAX_ARTICLES = 300
USER_AGENT = "Mozilla/5.0 (compatible; NewsBot/1.0)"
DEFAULT_IMG = "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80"

# QUAN TRỌNG: các mục con phải đứng TRƯỚC, feed tổng đứng CUỐI.
# Bài nào xuất hiện ở nhiều feed sẽ lấy danh mục của feed đầu tiên đọc được.
RSS_SOURCES = [
    ("https://baoxaydung.vn/rss/xay-dung/chi-dao-dieu-hanh.rss", "executive-direction"),
    ("https://baoxaydung.vn/rss/xay-dung/quy-hoach-kien-truc.rss", "architecture-planning"),
    ("https://baoxaydung.vn/rss/xay-dung/vat-lieu-xay-dung.rss", "building-materials"),
    ("https://baoxaydung.vn/rss/xay-dung/giam-dinh-chat-luong.rss", "quality-inspection"),
    ("https://baoxaydung.vn/rss/xay-dung/quan-ly-do-thi.rss", "urban-management"),
    ("https://baoxaydung.vn/rss/xay-dung.rss", "construction-news"),
]


def get_image(entry):
    for enc in entry.get("enclosures", []) or []:
        href = enc.get("href")
        if href and enc.get("type", "image").startswith("image"):
            return href
    for media in entry.get("media_content", []) or []:
        if media.get("url"):
            return media["url"]
    html = entry.get("description", "") or entry.get("summary", "")
    img = BeautifulSoup(html, "html.parser").find("img")
    if img and img.get("src"):
        return img["src"]
    return DEFAULT_IMG


def get_datetime(entry):
    """feedparser trả về struct_time theo UTC -> đổi sang giờ Việt Nam."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        return datetime(*parsed[:6], tzinfo=timezone.utc).astimezone(VN_TZ)
    return datetime.now(VN_TZ)


def parse_feed(url):
    feed = feedparser.parse(url, agent=USER_AGENT)
    status = getattr(feed, "status", "n/a")
    if not feed.entries:
        print(f"  ! Không có bài nào (HTTP {status}, lỗi: {feed.get('bozo_exception')})")
    return feed.entries


def load_old():
    if not os.path.exists(JSON_PATH):
        return []
    try:
        with open(JSON_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def main():
    fresh = {}
    for url, category in RSS_SOURCES:
        print(f"Đang đọc RSS: {url}")
        entries = parse_feed(url)
        added = 0
        for entry in entries:
            link = (entry.get("link") or "").strip()
            title = (entry.get("title") or "").strip()
            if not link or not title or link in fresh:
                continue
            dt = get_datetime(entry)
            fresh[link] = {
                "title": title,
                "link": link,
                "date": dt.strftime("%d/%m/%Y"),
                "year": dt.strftime("%Y"),
                "timestamp": dt.timestamp(),
                "category": category,
                "image": get_image(entry),
            }
            added += 1
        print(f"  -> {len(entries)} bài trong feed, thêm mới {added} bài [{category}]")

    if not fresh:
        print("Cảnh báo: không đọc được RSS nào, giữ nguyên file JSON cũ.")
        return

    # Giữ lại bài cũ không còn trong RSS để trang không bị ngắn đi theo thời gian
    merged = dict(fresh)
    for old in load_old():
        link = old.get("link")
        if link and link not in merged and old.get("title"):
            merged[link] = old

    articles = sorted(merged.values(), key=lambda a: a.get("timestamp", 0), reverse=True)
    articles = articles[:MAX_ARTICLES]

    os.makedirs("src/data", exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=4)
    print(f"Đã tổng hợp {len(articles)} bài viết vào {JSON_PATH}!")


if __name__ == "__main__":
    main()