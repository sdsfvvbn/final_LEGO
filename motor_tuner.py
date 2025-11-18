import pigpio
import time

# --- 您的接線設定 ---
PINS = {
    "底座": 18,  # 請確認您的實際 GPIO
    "肩膀": 23,
    "手肘": 24,
    "夾爪": 25
}

pi = pigpio.pi()
if not pi.connected:
    exit()

def set_angle(pin, angle):
    # 將 0-180 度轉換為 500-2500 脈衝
    # 為了安全，我們限制在 20-160 度之間，避免剛裝好就撞壞
    safe_angle = max(20, min(160, angle))
    duty = 500 + (safe_angle / 180.0) * 2000
    pi.set_servo_pulsewidth(pin, duty)

print("=== 馬達微調工具 ===")
print("輸入格式: [馬達名稱] [角度]")
print("例如輸入: 底座 90")
print("輸入 q 離開")

try:
    while True:
        cmd = input(">> ").strip().split()
        if not cmd: continue
        if cmd[0] == 'q': break
        
        if len(cmd) != 2:
            print("格式錯誤！")
            continue
            
        name = cmd[0]
        try:
            angle = float(cmd[1])
        except:
            print("角度必須是數字")
            continue

        if name in PINS:
            print(f"設定 {name} (GPIO {PINS[name]}) -> {angle} 度")
            set_angle(PINS[name], angle)
        else:
            print(f"找不到馬達: {name}。可用名稱: {list(PINS.keys())}")

except KeyboardInterrupt:
    pass
finally:
    for pin in PINS.values():
        pi.set_servo_pulsewidth(pin, 0) # 放鬆所有馬達
    pi.stop()