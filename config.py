import pigpio
import time
import config  # 讀取您的設定檔

# 連線
pi = pigpio.pi()
if not pi.connected:
    print("❌ pigpiod 沒開！")
    exit()

# 定義要測試的清單 (名稱對應 config 裡的變數)
motors = [
    ("底座 (Base)", config.PIN_BASE),
    ("左臂 (Shoulder)", config.PIN_SHOULDER),
    ("右臂/肘 (Middle)", config.PIN_ELBOW),
    ("夾爪 (Gripper)", config.PIN_GRIPPER)
]

print("=== 硬體接線檢查 ===")
print("請盯著手臂看，確認動的部位跟螢幕顯示的一樣！")
print("按 Ctrl+C 強制停止\n")

try:
    for name, pin in motors:
        print(f"👉 正在測試：[{name}] - GPIO {pin}")
        
        # 1. 回中間 (1500)
        print("   -> 回正 (1500)")
        pi.set_servo_pulsewidth(pin, 1500)
        time.sleep(1)
        
        # 2. 轉一點點 (1300)
        print("   ->轉動測試 (1300)")
        pi.set_servo_pulsewidth(pin, 1300)
        time.sleep(1)
        
        # 3. 回中間 (1500)
        print("   -> 回正 (1500)")
        pi.set_servo_pulsewidth(pin, 1500)
        time.sleep(1)
        
        # 4. 放鬆
        pi.set_servo_pulsewidth(pin, 0)
        print(f"✅ [{name}] 測試結束\n")
        time.sleep(0.5)

    print("🎉 全部測試完成！如果動的順序是對的，接線就沒問題。")

except KeyboardInterrupt:
    print("\n使用者中斷")
finally:
    # 關閉所有馬達
    for _, pin in motors:
        pi.set_servo_pulsewidth(pin, 0)
    pi.stop()