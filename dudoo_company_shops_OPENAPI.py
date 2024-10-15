import requests
import json
import hashlib
import hmac
import datetime as dt

def fetch_data(full_url, page):
    # 設定 API 相關資訊
    app_id = 'df82a469-eb6b-4e81-bb27-dd06a4028547'
    hmac_key = 'V7nkqFlbAIjTItzz52KEHxJYlnzNeZeJ'
    method = 'GET'

    url_with_page = full_url.format(page=page)

    message = url_with_page.encode('utf-8')
    hmac_key_bytes = hmac_key.encode('utf-8')
    signature = hmac.new(hmac_key_bytes, message, hashlib.sha256).hexdigest()
    
    headers = {
        'Content-Type': 'application/json',
        'X-Dudoo-App-Id': app_id,
        'X-Dudoo-Signature': signature
    }
    request = requests.Request(method, url_with_page, headers=headers)
    response = requests.Session().send(request.prepare())
    # response = requests.get(url_with_page, headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        print('Error_Code:', response.status_code)
        return None

def main():
    base_url = 'https://api.dudooeat.com/latest/'
    invoice_details_url = base_url + 'headquarters/8727/shops'
    
    url = invoice_details_url + '?page={page}&size=50'

    payload = f''
    full_url = url #+ '&' + payload

    # 第一次請求以獲取total_records和pages
    initial_data = fetch_data(full_url, 1)
    pages = initial_data['pages']
    total = initial_data['total']

    all_data = []  # 用於儲存所有的記錄
    all_data.extend(initial_data['items'])  # 添加第一頁的數據

    # 循環下載剩餘頁面的數據
    if pages > 1:
        for page in range(2, pages + 1):  # 確保包括最後一頁
            data = fetch_data(full_url, page)
            if data is not None:
                all_data.extend(data['items'])
    
    # 寫入 JSON 檔案，僅寫入明細部分
    path = 'C:/duduget_new/'
    file_name = 'shops.json'
    full_name = path + file_name
    
    # if total > 1:
    with open(full_name, 'w', encoding='utf-16', errors='ignore') as file:
        json.dump({"items": all_data}, file, ensure_ascii=False, indent=4)
    print(f"已將門店資料寫入檔案：{full_name}")
if __name__ == '__main__':
    main()
