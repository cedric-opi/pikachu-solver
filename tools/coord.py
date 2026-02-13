import pyautogui
import time
from selenium.webdriver.common.by import By
from selenium import webdriver

GAME_URL = "https://www.pikachucodien.net/"

driver = webdriver.Chrome()
driver.get("https://www.pikachucodien.net/")
driver.maximize_window()

print("TOOL LẤY TỌA ĐỘ PIKACHU")
print("Hãy mở trình duyệt, để game hiển thị trọn vẹn.")
print("Di chuột vào GÓC TRÊN BÊN TRÁI của Board game (vùng chứa các con thú).")
time.sleep(20)
x1, y1 = pyautogui.position()
print(f"-> Đã ghi nhận Góc Trái: ({x1}, {y1})")

print("Di chuột vào GÓC DƯỚI BÊN PHẢI của Board game.")
time.sleep(20)
x2, y2 = pyautogui.position()
print(f"-> Đã ghi nhận Góc Phải: ({x2}, {y2})")

width = x2 - x1
height = y2 - y1
print(f"REGION = ({x1}, {y1}, {width}, {height})")
