import feedparser
import json
import os
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup

rss_url = "https://baoxaydung.vn/rss/xay-dung.rss"
feed = feedparser.parse(rss_url)

VN_TZ = timezone(timedelta(hours=7))
DEFAULT_IMG = "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80"


def get_date(entry):
    """Lấy ngày đăng từ RSS, đổi sang giờ Việt Nam. Nếu thiếu thì dùng hôm nay."""
    parsed = entry.get("published_parsed") or entry.get("updated_parsed")
    if parsed:
        dt = datetime(*parsed[:6], tzinfo=timezone.utc).astimezone(VN_TZ)
    else:
        dt = datetime.now(VN_TZ)
    return dt.strftime("%d/%m/%Y")


def get_image(entry):
    # Ưu tiên enclosure / media_content nếu RSS có
    if entry.get("enclosures"):
        url = entry.enclosures[0].get("href")
        if url:
            return url
    if entry.get("media_content"):
        url = entry.media_content[0].get("url")
        if url:
            return url
    soup = BeautifulSoup(entry.get("description", ""), "html.parser")
    img_tag = soup.find("img")
    if img_tag and img_tag.get("src"):
        return img_tag["src"]
    return DEFAULT_IMG


if feed.entries:
    news_list = []
    for entry in feed.entries[:6]:
        news_list.append({
            "title": entry.title.strip(),
            "link": entry.link,
            "date": get_date(entry),
            "category": "Tin Xây Dựng",
            "image": get_image(entry),
        })

    os.makedirs("src/data", exist_ok=True)
    with open("src/data/latest_news.json", "w", encoding="utf-8") as f:
        json.dump(news_list, f, ensure_ascii=False, indent=4)
    print(f"Đã cập nhật thành công {len(news_list)} bài viết!")
else:
    print("Cảnh báo: Không đọc được RSS, giữ nguyên file JSON cũ.")