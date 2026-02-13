import cv2
import numpy as np
import os
import time
import pyautogui
from selenium import webdriver
from selenium.webdriver.common.by import By
from pikachu import PikachuSolver, add_border, Point

ROWS = 9
COLS = 16
ASSETS_PATH = "assets/" 

def initialize_browser():
    driver = webdriver.Chrome()
    driver.get("https://www.pikachucodien.net/")
    driver.maximize_window()
    
    print("HỆ THỐNG SẼ BẮT ĐẦU QUÉT SAU 10 GIÂY.")
    for i in range(10, 0, -1):
        print(f"Bắt đầu sau: {i}s", end="\r")
        time.sleep(1)
    print("\nBẮT ĐẦU QUÉT!")
    return driver

def load_templates():
    templates = {}
    if not os.path.exists(ASSETS_PATH):
        print(f"Lỗi: Không tìm thấy thư mục {ASSETS_PATH}")
        return templates
    
    for filename in os.listdir(ASSETS_PATH):
        if filename.endswith(".png"):
            path = os.path.join(ASSETS_PATH, filename)
            try:
                piece_id = int(filename.split(".")[0])
                # Load ảnh gốc 
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    templates[piece_id] = img
            except:
                continue
    print(f"Đã load {len(templates)} mẫu nhân vật.")
    return templates

def get_accurate_board_pyautogui():
    my_region = (642, 394, 673, 470) 
    print(f"PyAutoGUI đang chụp vùng: {my_region}")
    
    screenshot = pyautogui.screenshot(region=my_region)
    board_img = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    cv2.imwrite("current_game_view.png", board_img)
    
    return board_img, (my_region[0], my_region[1]), 1.0

def identify_piece(cell_img, templates):
    best_id = 0
    max_val = -1
    cell_gray = cv2.cvtColor(cell_img, cv2.COLOR_BGR2GRAY)
    
    for p_id, temp_img in templates.items():
        if len(temp_img.shape) == 3:
            temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2GRAY)
            
        temp_resized = cv2.resize(temp_img, (cell_gray.shape[1], cell_gray.shape[0]))
        res = cv2.matchTemplate(cell_gray, temp_resized, cv2.TM_CCOEFF_NORMED)
        _, val, _, _ = cv2.minMaxLoc(res)
        
        if val > max_val:
            max_val = val
            best_id = p_id

    # HẠ NGƯỠNG TỪ TỪ: Thử 0.4 hoặc 0.5 trước
    if max_val > 0.5: 
        return best_id
    return 0

def get_matrix_final(templates):
    board_img, offset = get_accurate_board_pyautogui()
    h, w, _ = board_img.shape
    step_h = h / ROWS
    step_w = w / COLS
    
    matrix = []
    for r in range(ROWS):
        row_data = []
        for c in range(COLS):
            # Tính tọa độ quét bằng float để không bị lệch tích lũy
            x1 = c * step_w
            y1 = r * step_h
            x2 = (c + 1) * step_w
            y2 = (r + 1) * step_h
            
            # Cắt ảnh và ép kiểu int ở bước cuối
            cell = board_img[int(y1):int(y2), int(x1):int(x2)]
            ch, cw = cell.shape[:2]

            top_cut = int(ch * 0.1)
            bottom_cut = int(ch * 0.05) # Gọt sâu hơn ở phía dưới
            left_cut = int(cw * 0.1)
            right_cut = int(cw * 0.1)

            # Gọt viền để tránh nhận diện nhầm
            ch, cw = cell.shape[:2]
            margin_h = int(ch * 0.2)
            margin_w = int(cw * 0.2)
            cell_inner = cell[top_cut : ch - bottom_cut, left_cut : cw - right_cut]            
            
            # Debug: Lưu thử 1 ô để xem nó có bị lệch không
            if r == 0 and c == 0: cv2.imwrite("debug_cell_0_0.png", cell_inner)
            if r == 4 and c == 8: cv2.imwrite("debug_cell_4_8.png", cell_inner)
            
            p_id = identify_piece(cell_inner, templates)
            row_data.append(p_id)
        matrix.append(row_data)
    return matrix, offset, (step_w, step_h)
    
def perform_auto_click(r, c, offset, cell_size):
    """
    r, c: Hàng và cột (từ 0 đến ROWS-1, COLS-1)
    offset: (642, 394)
    cell_size: (41.94, 51.89)
    """
    # Tính tọa độ tâm của ô trên màn hình thực
    target_x = offset[0] + (c * cell_size[0]) + (cell_size[0] // 2)
    target_y = offset[1] + (r * cell_size[1]) + (cell_size[1] // 2)

    print(f"--> Đang di chuyển chuột tới ô [{r},{c}] tại tọa độ: ({target_x}, {target_y})")    
    
    # Di chuyển mượt và click
    pyautogui.moveTo(target_x, target_y, duration=0.1)
    pyautogui.click()

if __name__ == "__main__":
    p_templates = load_templates()
    browser = initialize_browser()
    
    print("BOT ĐÃ SẴN SÀNG TỰ CHƠI...")
    time.sleep(5) 

    while True:
        try:
            # Quét lại toàn bộ bàn chơi (Cập nhật trạng thái mới nhất)
            matrix, offset, cell_size = get_matrix_final(p_templates)

            # Đếm số lượng ô KHÁC 0
            active_cells = sum(1 for row in matrix for val in row if val != 0)
            print(f"Số lượng thú nhận diện được: {active_cells}/144")

            if active_cells == 0:
                print("Không nhận diện được con thú nào. Đang thử quét lại sau 2 giây...")
                time.sleep(2)
                continue 
            
            # Kiểm tra xem còn hình trên bàn không
            flat_list = [item for sublist in matrix for item in sublist if item != 0]
            if not flat_list:
                print("Đã hết hình hoặc không nhận diện được nữa. Dừng.")
                break

            #  Giải ma trận
            board_with_border = add_border(matrix)
            solver = PikachuSolver(board_with_border)
            move = solver.find_any_move()
            
            if move:
                p1, p2 = move
                print(f"Ăn cặp: {p1} <-> {p2} (ID: {board_with_border[p1.r][p1.c]})")
                
                # Thực hiện Click
                perform_auto_click(p1.r - 1, p1.c - 1, offset, cell_size)
                time.sleep(0.1) 
                perform_auto_click(p2.r - 1, p2.c - 1, offset, cell_size)
                
                # ĐỢI GAME BIẾN MẤT HÌNH
                # Đây là bước quan trọng nhất để lần quét sau không bị dính hình cũ
                time.sleep(0.8) 
            else:
                print("Không tìm thấy cặp nào nối được. Đang thử quét lại...")
                time.sleep(1)

        except Exception as e:
            print(f"Lỗi trong vòng lặp: {e}")
            break