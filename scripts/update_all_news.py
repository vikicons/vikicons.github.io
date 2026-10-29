import feedparser
import json
import os
from datetime import datetime
from bs4 import BeautifulSoup

# Danh sách các nguồn RSS mục Xây dựng từ baoxaydung.vn
rss_urls = [
    "https://baoxaydung.vn/rss/xay-dung.rss",
    "https://baoxaydung.vn/rss/xay-dung/chi-dao-dieu-hanh.rss",
    "https://baoxaydung.vn/rss/xay-dung/quy-hoach-kien-truc.rss",
    "https://baoxaydung.vn/rss/xay-dung/vat-lieu-xay-dung.rss",
    "https://baoxaydung.vn/rss/xay-dung/giam-dinh-chat-luong.rss",
    "https://baoxaydung.vn/rss/xay-dung/quan-ly-do-thi.rss"
]

all_articles = []
seen_links = set()

for url in rss_urls:
    print(f"Đang đọc RSS từ: {url}")
    feed = feedparser.parse(url)
    for entry in feed.entries:
        link = entry.get("link", "")
        if not link or link in seen_links:
            continue
        seen_links.add(link)

        # Trích xuất ảnh từ thẻ description hoặc content
        description_html = entry.get("description", "")
        soup = BeautifulSoup(description_html, "html.parser")
        img_tag = soup.find("img")
        img_url = img_tag["src"] if img_tag else "https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80"

        # Lấy ngày tháng xuất bản
        published_parsed = entry.get("published_parsed")
        if published_parsed:
            dt = datetime(*published_parsed[:6])
            date_str = dt.strftime("%d/%m/%Y")
            year_str = dt.strftime("%Y")
            timestamp = dt.timestamp()
        else:
            date_str = "29/10/2026"
            year_str = "2026"
            timestamp = 0

        # Phân loại danh mục sang mã tiếng Anh để lọc chính xác tuyệt đối
        category = "construction-news"
        if "chi-dao-dieu-hanh" in url:
            category = "executive-direction"
        elif "quy-hoach-kien-truc" in url:
            category = "architecture-planning"
        elif "vat-lieu-xay-dung" in url:
            category = "building-materials"
        elif "giam-dinh-chat-luong" in url:
            category = "quality-inspection"
        elif "quan-ly-do-thi" in url:
            category = "urban-management"

        article = {
            "title": entry.get("title", "").strip(),
            "link": link,
            "date": date_str,
            "year": year_str,
            "timestamp": timestamp,
            "category": category,
            "image": img_url
        }
        all_articles.append(article)

# Sắp xếp bài viết mới nhất lên đầu dựa trên timestamp
all_articles.sort(key=lambda x: x["timestamp"], reverse=True)

# Lưu vào tệp JSON tổng cho trang tin tức
os.makedirs("src/data", exist_ok=True)
json_path = "src/data/all_news.json"
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(all_articles, f, ensure_ascii=False, indent=4)

print(f"Đã tổng hợp thành công {len(all_articles)} bài viết vào {json_path}!")