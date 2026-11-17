import os
import json
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

url = "https://www.pvoil.com.vn/tin-gia-xang-dau"
print(f"Đang khởi động trình duyệt tự động để vượt qua Cloudflare: {url}")

try:
    with sync_playwright() as p:
        # Khởi động trình duyệt Chromium ở chế độ không giao diện (headless)
        browser = p.chromium.launch(headless=True)
        # Tạo ngữ cảnh giả lập một người dùng thật trên trình duyệt máy tính
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        # Truy cập trang web và chờ cho đến khi trang tải xong hoàn toàn (vượt qua màn hình Cloudflare)
        page.goto(url, timeout=60000)
        
        # Chờ thêm vài giây để Cloudflare hoàn tất xác minh ngầm và nội dung bảng giá xuất hiện
        page.wait_for_timeout(5000)
        
        # Lấy toàn bộ mã HTML sau khi trang đã render xong
        html_content = page.content()
        browser.close()

    # Dùng BeautifulSoup để bóc tách bảng giá
    soup = BeautifulSoup(html_content, 'html.parser')
    table = soup.find('table')
    
    gas_items = []
    if table:
        rows = table.find_all('tr')
        print(f"Đã vượt rào thành công! Tìm thấy bảng dữ liệu với {len(rows)} hàng.")
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 4:
                stt = cols[0].text.strip()
                if stt.isdigit():
                    product = cols[1].text.strip()
                    price = cols[2].text.strip()
                    change = cols[3].text.strip()
                    
                    gas_items.append({
                        "stt": stt,
                        "product": product,
                        "price": price,
                        "change": change
                    })
                    print(f"Đã đọc: {product} - {price} (Chênh lệch: {change})")

    # Lưu dữ liệu vào file JSON nếu cào thành công
    if gas_items:
        os.makedirs("src/data", exist_ok=True)
        json_path = "src/data/gas_prices.json"
        
        vn_time = datetime.now(timezone(timedelta(hours=7)))
        formatted_time = vn_time.strftime("%d/%m/%Y lúc %H:%M:%S")

        output_data = {
            "last_updated": formatted_time,
            "prices": gas_items
        }

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=4)
            
        print(f"Đã cập nhật thành công {len(gas_items)} bản ghi vào {json_path} lúc {formatted_time}!")
    else:
        print("CẢNH BÁO: Đã vào được trang nhưng không tìm thấy dữ liệu bảng sản phẩm.")

except Exception as e:
    print(f"Lỗi khi cào dữ liệu bằng Playwright: {e}")