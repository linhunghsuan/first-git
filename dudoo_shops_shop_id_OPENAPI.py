import requests
import json
import hashlib
import hmac

def fetch_data(full_url):
    # 設定 API 相關資訊
    app_id = 'df82a469-eb6b-4e81-bb27-dd06a4028547'
    hmac_key = 'V7nkqFlbAIjTItzz52KEHxJYlnzNeZeJ'
    method = 'GET'

    message = full_url.encode('utf-8')
    hmac_key_bytes = hmac_key.encode('utf-8')
    signature = hmac.new(hmac_key_bytes, message, hashlib.sha256).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'X-Dudoo-App-Id': app_id,
        'X-Dudoo-Signature': signature
    }
    request = requests.Request(method, full_url, headers=headers)
    response = requests.Session().send(request.prepare())

    if response.status_code == 200:
        return response.json()
    else:
        print('Error_Code:', response.status_code)
        return None

def main():
    base_url = 'https://api.dudooeat.com/latest/shops/'
    shop_ids = ['13580','8428','13578','13579','13581','8439','13659','13583','13577','13657','8437','13658','8438','13582','8470','13661','13660','8430']

    all_data = []  # 用於儲存所有的記錄

    # 迴圈查詢每個店鋪
    for shop_id in shop_ids:
        full_url = base_url + shop_id

        # 請求每個店鋪的資料
        shop_data = fetch_data(full_url)

        if shop_data:  # 確認請求成功
            all_data.append(shop_data)  # 添加該店鋪的數據到列表

    # 寫入 JSON 檔案
    path = 'C:/duduget_new/'
    file_name = 'shop.json'
    full_name = path + file_name
    
    with open(full_name, 'w', encoding='utf-16', errors='ignore') as file:
        json.dump({"shops": all_data}, file, ensure_ascii=False, indent=4)
    
    print(f"已將所有店鋪的資料寫入檔案：{full_name}")

if __name__ == '__main__':
    main()
