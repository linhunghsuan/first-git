import pandas as pd

# 讀取 Excel 檔案
def read_excel(file_path):
    return pd.read_excel(file_path)

# 資料前處理，更新甲的交易序號
def preprocess_jia(df_jia):
    # 更新甲的交易序號
    df_jia['交易序號'] = df_jia.apply(lambda row: f"{row['分店代碼']}{row['交易序號'][:8]}{row['交易序號'][9:]}",
                                     axis=1)
    return df_jia

# 資料比對處理，檢核結果
def compare_data(df_jia, df_yi):
    # 保留標籤欄位的資訊
    basic_columns = [
        '分店代碼', '分店名稱', '建立時間', '交易序號', '單號', '發票號碼', '商品編號', '商品名稱',
        '標籤名稱', '標籤價錢', '商品單價', '數量', '銷售金額', '單品折扣總額', '折扣名稱', '折扣總額',
        '實收金額', '淨額', '商品分類', '用餐方式', '訂單來源'
    ]
    
    # 找出標籤欄位
    label_columns = [col for col in df_jia.columns if col not in basic_columns]

    # 進行 Group By 操作，聚合數量、商品單價與標籤價錢
    df_jia_grouped = df_jia.groupby(['交易序號', '商品編號'], as_index=False).agg({
        '數量': 'sum',  # 合併數量
        '商品單價': 'first',  # 假設商品單價相同，取第一個值
        '標籤價錢': 'first'  # 假設標籤價錢相同，取第一個值
    })

    # 聚合標籤資料
    df_jia_labels = df_jia.groupby(['交易序號', '商品編號'], as_index=False)[label_columns].first()

    # 合併 group by 後的資料與標籤資訊
    df_jia_merged = pd.merge(df_jia_grouped, df_jia_labels, on=['交易序號', '商品編號'], how='left')

    # 資料比對邏輯
    results = []
    yi_checked = set()  # 用來追蹤已比對的乙資料

    for idx, row in df_jia_merged.iterrows():
        # 從甲取得交易資訊
        jia_pos_no = row['交易序號']
        jia_prod_no = row['商品編號']
        jia_qty = row['數量']
        jia_sales_amount = row['商品單價'] * row['數量']  # 單價*數量

        # 在乙中找到相同的 POS 單號和產品編號
        matched_row = df_yi[(df_yi['POS單號'] == jia_pos_no) & (df_yi['產品編號'] == jia_prod_no)]

        # 初始化比對結果
        check_qty = "數量不符"
        check_amount = "金額不符"
        jia_tag_sales_amount = None

        # 主要商品編號的比對
        if not matched_row.empty:
            yi_sales_qty = matched_row.iloc[0]['銷售數量']
            yi_sales_amount = matched_row.iloc[0]['銷售含稅金額']

            # 檢查數量和金額
            check_qty = "數量正確" if jia_qty == yi_sales_qty else "數量不符"
            check_amount = "金額正確" if jia_sales_amount == yi_sales_amount else "金額不符"

            # 追蹤該筆乙資料已檢核
            yi_checked.add(matched_row.index[0])
        else:
            check_qty = "未找到對應資料"

        # 檢查標籤的比對
        for label_col in label_columns:
            label_value = row[label_col]
            if pd.notna(label_value):
                jia_tag_sales_amount = row['標籤價錢'] * jia_qty  # 標籤價錢*數量
                matched_label_row = df_yi[(df_yi['POS單號'] == jia_pos_no) & (df_yi['產品編號'] == label_value)]
                
                if not matched_label_row.empty:
                    yi_sales_amount = matched_label_row.iloc[0]['銷售含稅金額']
                    check_amount = "標籤金額正確" if jia_tag_sales_amount == yi_sales_amount else "標籤金額不符"
                    
                    # 更新結果，輸出來自甲的標籤數量與標籤價格
                    results.append({
                        '交易單號': row['交易序號'],
                        'POS單號': jia_pos_no,
                        '產品編號': label_value,  # 使用標籤產品編號
                        '數量': jia_qty,  # 使用甲的數量
                        '銷售數量': matched_row.iloc[0]['銷售數量'] if not matched_row.empty else "N/A",
                        '單價*數量': jia_tag_sales_amount,  # 使用標籤價格*數量
                        '銷售含稅金額': yi_sales_amount if not matched_label_row.empty else "N/A",
                        '檢核結果': check_qty if check_qty == "數量正確" else f"{check_qty}; {check_amount}"
                    })

        # 總檢核結果
        check_result = "正確" if check_qty == "數量正確" and check_amount == "金額正確" else f"{check_qty}; {check_amount}"

        results.append({
            '交易單號': row['交易序號'],
            'POS單號': jia_pos_no,
            '產品編號': jia_prod_no,  # 使用更新後的產品編號
            '數量': jia_qty,
            '銷售數量': yi_sales_qty if not matched_row.empty else "N/A",
            '單價*數量': jia_sales_amount,
            '銷售含稅金額': yi_sales_amount if not matched_row.empty else "N/A",
            '檢核結果': check_result
        })

    # 檢查乙資料中未匹配到甲的部分
    for idx, row in df_yi.iterrows():
        if idx not in yi_checked:
            results.append({
                '交易單號': "N/A",
                'POS單號': row['POS單號'],
                '產品編號': row['產品編號'],
                '數量': "N/A",
                '銷售數量': row['銷售數量'],
                '單價*數量': "N/A",
                '銷售含稅金額': row['銷售含稅金額'],
                '檢核結果': "未找到對應資料"
            })

    return pd.DataFrame(results)

# 將結果輸出至 Excel
def save_result(df, output_path):
    df.to_excel(output_path, index=False)

# 主流程
def main(jia_file, yi_file, output_file):
    df_jia = read_excel(jia_file)
    df_yi = read_excel(yi_file)

    # 處理甲的交易序號
    df_jia = preprocess_jia(df_jia)
    # 比對數據
    result_df = compare_data(df_jia, df_yi)

    # 輸出結果至 Excel
    save_result(result_df, output_file)
    print(f"比對結果已輸出至 {output_file}")

# 輸入路徑與結果輸出
if __name__ == "__main__":
    jia_file = r'C:\Users\11202510\Downloads\交易明細副檔_2024年09月01日-2024年09月01日.xlsx'
    yi_file = r'C:\Users\11202510\Downloads\cxmqr001.xlsx'
    output_file = r'C:\Users\11202510\Downloads\result.xlsx'
    main(jia_file, yi_file, output_file)
