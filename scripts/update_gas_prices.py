import os
import json
from datetime import datetime, timezone, timedelta
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

# Sử dụng trang chuyên đề giá xăng dầu của VnExpress
url = "https://vnexpress.net/chu-de/gia-xang-dau-3026"
print(f"Đang kết nối tới VnExpress: {url}")

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1280, "height": 800}
        )
        page = context.new_page()
        
        # Mở trang web VnExpress
        page.goto(url, timeout=60000)
        page.wait_for_timeout(3000) # Chờ trang load hoàn tất nội dung động (nếu có)

        html_content = page.content()
        browser.close()

    # Dùng BeautifulSoup để bóc tách dữ liệu
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Tìm bảng (table) hiển thị giá xăng dầu trong trang
    table = soup.find('table')
    gas_items = []
    
    if table:
        rows = table.find_all('tr')
        print(f"Đã tìm thấy bảng dữ liệu với {len(rows)} hàng.")
        
        for row in rows:
            cols = row.find_all(['td', 'th'])
            # Bảng giá VnExpress thường có 3 cột: Mặt hàng, Giá, So với kỳ trước
            if len(cols) >= 3:
                product = cols[0].text.strip()
                price = cols[1].text.strip()
                change = cols[2].text.strip()
                
                # Bỏ qua dòng tiêu đề của bảng
                if product and product.lower() != "mặt hàng" and "giá từ" not in product.lower():
                    gas_items.append({
                        "stt": str(len(gas_items) + 1),
                        "product": product,
                        "price": f"{price} đ" if not price.endswith("đ") else price,
                        "change": change
                    })
                    print(f"Đã đọc: {product} - Giá: {price} - Biến động: {change}")

    # Ghi dữ liệu vào file JSON nếu cào thành công
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
            
        print(f"Cập nhật thành công {len(gas_items)} bản ghi vào {json_path} lúc {formatted_time}!")
    else:
        print("CẢNH BÁO: Không tìm thấy dữ liệu dòng sản phẩm nào trong bảng VnExpress.")

except Exception as e:
    print(f"Lỗi khi cào dữ liệu từ VnExpress: {e}")