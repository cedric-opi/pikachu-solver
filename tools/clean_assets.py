import cv2
import os
import numpy as np

RAW_DIR = "temp_assets"
FINAL_DIR = "assets"

def clean_and_rename():
    if not os.path.exists(FINAL_DIR):
        os.makedirs(FINAL_DIR)

    files = sorted([f for f in os.listdir(RAW_DIR) if f.endswith('.png')])
    unique_samples = []
    count = 1

    target_size = (50, 50) 

    print(f"Bắt đầu lọc mẫu duy nhất từ {len(files)} ảnh...")

    for file in files:
        img_path = os.path.join(RAW_DIR, file)
        img = cv2.imread(img_path)
        if img is None: continue

        # Ép mọi ảnh về cùng một kích thước chuẩn
        img_resized = cv2.resize(img, target_size)

        is_duplicate = False
        current_best_match = 0.0 

        # So sánh với danh sách ảnh duy nhất đã tìm thấy
        for unique_img in unique_samples:
            # matchTemplate yêu cầu (image, template)
            res = cv2.matchTemplate(img_resized, unique_img, cv2.TM_CCOEFF_NORMED)
            _, val, _, _ = cv2.minMaxLoc(res)
            
            if val > 0.92: 
                is_duplicate = True
                current_best_match = val
                break
        
        # Nếu là con thú mới, hãy lưu lại
        if not is_duplicate:
            unique_samples.append(img_resized)
            save_path = os.path.join(FINAL_DIR, f"{count}.png")
            cv2.imwrite(save_path, img) 
            print(f"Đã lưu mẫu thú mới: {count}.png")
            count += 1
            
        if count > 36:
            print("Đã tìm đủ 36 mẫu thú!")
            break

    print(f"\n--- THÀNH CÔNG ---")
    print(f"Đã lọc xong {count-1} mẫu thú vào thư mục '{FINAL_DIR}'.")

if __name__ == "__main__":
    clean_and_rename()