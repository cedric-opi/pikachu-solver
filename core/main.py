from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
import re   
from pikachu import PikachuSolver, Point, add_border

# Khởi tạo
driver = webdriver.Chrome()
driver.get("https://www.pikachucodien.net/")
print("Đang tải trang...")
time.sleep(8) 

# Hàm click vào ô thú 
def click_cell(element):
    try:
        # Lấy thẻ img bên trong div để click chính xác hơn
        target = element.find_element(By.TAG_NAME, "img")
        
        # Cách 1: Click vật lý
        actions = ActionChains(driver)
        actions.move_to_element(target).click().perform()
        
        # Cách 2: Thêm JavaScript click
        driver.execute_script("arguments[0].click();", target)
    except:
        # Nếu ko tìm thấy img thì click thẳng vào div
        driver.execute_script("arguments[0].click();", element)

# Hàm quét bảng game và trả về ma trận cùng map tọa độ 
def get_board_from_web():
    try:
        # Tìm tất cả các div có chứa img nằm bất cứ đâu bên trong thẻ có id='board'
        pieces = driver.find_elements(By.XPATH, "//td[@id='board']//div[img]")
        
        visible_pieces = []
        for p in pieces:
            style = p.get_attribute("style") or ""
            # Kiểm tra style chứa 'visibility: visible'
            if "visibility: visible" in style:
                visible_pieces.append(p)
                
        if not visible_pieces: return None, None

        # Logic xử lý tọa độ và tạo ma trận 
        raw_data = []
        max_col, max_row = 0, 0
        for p in visible_pieces:
            style = p.get_attribute("style")
            l_m = re.search(r"left:\s*(\d+)px", style)
            t_m = re.search(r"top:\s*(\d+)px", style)
            if l_m and t_m:
                c = (int(l_m.group(1)) - 42) // 42
                r = (int(t_m.group(1)) - 52) // 52
                
                img_src = p.find_element(By.TAG_NAME, "img").get_attribute("src")
                img_id = int(re.search(r"pieces(\d+)\.png", img_src).group(1))
                raw_data.append((r, c, img_id, p))
                max_row, max_col = max(max_row, r), max(max_col, c)

        matrix = [[0 for _ in range(max_col + 1)] for _ in range(max_row + 1)]
        elements_map = {}
        for r, c, i, p in raw_data:
            matrix[r][c] = i
            elements_map[(r, c)] = p
        return matrix, elements_map
    except Exception as e:
        print(f"Lỗi khi quét: {e}")
        return None, None

def main_solve():
    print("Bot bắt đầu giải...")
    last_move = None
    retry_count = 0

    while True:
        matrix, elements_map = get_board_from_web()
        if not matrix or len(elements_map) == 0:
            print("Đang chờ ô thú hiện ra...")
            time.sleep(2)
            continue
            
        board_ready = add_border(matrix)
        solver = PikachuSolver(board_ready)
        move = solver.find_any_move()
        
        if move:
            p1, p2 = move
            c1, c2 = (p1.r - 1, p1.c - 1), (p2.r - 1, p2.c - 1)
            
            # Xử lý nếu bị kẹt (Click trượt)
            if last_move == (c1, c2):
                retry_count += 1
                if retry_count > 2:
                    print(f"Bỏ qua cặp {c1}-{c2} do click ko ăn...")
                    # Đánh dấu ảo là 0 để tìm cặp khác trong lượt này
                    matrix[c1[0]][c1[1]] = 0
                    matrix[c2[0]][c2[1]] = 0
                    board_ready = add_border(matrix)
                    solver = PikachuSolver(board_ready)
                    move = solver.find_any_move()
                    if not move: continue
                    p1, p2 = move
                    c1, c2 = (p1.r - 1, p1.c - 1), (p2.r - 1, p2.c - 1)
                    retry_count = 0
            else:
                retry_count = 0

            last_move = (c1, c2)
            print(f"Thực hiện Click: {c1} - {c2}")
            
            click_cell(elements_map[c1])
            time.sleep(0.15) 
            click_cell(elements_map[c2])
            
            time.sleep(0.8) # Đợi game xử lý biến mất
        else:
            print("Hết nước đi tạm thời.")
            time.sleep(2)

# Luồng chạy chính
driver.switch_to.default_content()
time.sleep(2)
iframes = driver.find_elements(By.TAG_NAME, "iframe")
target_found = False

for i in range(len(iframes)):
    try:
        driver.switch_to.default_content()
        driver.switch_to.frame(i)
        # Kiểm tra sự tồn tại của td#board
        if len(driver.find_elements(By.ID, "board")) > 0:
            print(f"==> Đã khóa mục tiêu tại Iframe số {i}")
            target_found = True
            break
    except:
        continue

if target_found:
    main_solve()
else:
    print("Không tìm thấy Iframe game.")