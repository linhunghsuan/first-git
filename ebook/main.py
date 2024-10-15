import json
import os

def clean_highlighted_text(text):
    # 刪除換行
    return text.replace("\n", "").strip()

def extract_and_organize_content(file_path):
    with open(file_path, 'r', encoding='utf-8-sig') as file:
        data = json.load(file)

    chapter_structure = {}
    color_structure = {}

    # 處理每個高亮
    for highlight in data.get("highlights", []):
        # 清理 highlighted_text
        content = clean_highlighted_text(highlight.get("highlighted_text", "未找到內容"))
        color = highlight.get("style", {}).get("which", "未找到顏色")
        chapters = highlight.get("toc_family_titles", ["未找到章節"])

        # 章節結構：顏色作為內部層級
        for chapter in chapters:
            if chapter not in chapter_structure:
                chapter_structure[chapter] = {}
            if color not in chapter_structure[chapter]:
                chapter_structure[chapter][color] = []
            chapter_structure[chapter][color].append(content)

        # 顏色結構：合併章節
        if color not in color_structure:
            color_structure[color] = {}
        for chapter in chapters:
            if chapter not in color_structure[color]:
                color_structure[color][chapter] = []
            color_structure[color][chapter].append(content)

    # 準備輸出檔案的路徑
    directory, original_filename = os.path.split(file_path)
    chapter_filename = f"{os.path.splitext(original_filename)[0]}_chapter.json"
    class_filename = f"{os.path.splitext(original_filename)[0]}_class.json"
    chapter_file_path = os.path.join(directory, chapter_filename)
    class_file_path = os.path.join(directory, class_filename)

    # 將章節結構寫入新檔案
    with open(chapter_file_path, 'w', encoding='utf-8') as chapter_file:
        json.dump(chapter_structure, chapter_file, ensure_ascii=False, indent=4)

    # 將顏色結構寫入新檔案
    with open(class_file_path, 'w', encoding='utf-8') as class_file:
        json.dump(color_structure, class_file, ensure_ascii=False, indent=4)

    print(f"已儲存到: {chapter_file_path}")
    print(f"已儲存到: {class_file_path}")

# 使用範例：傳入檔案路徑
extract_and_organize_content(r"C:\Users\11202510\Downloads\456.calibre_highlights")


