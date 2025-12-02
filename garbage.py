import pigpio

import time



# ==========================================

# 1. 硬體參數設定 (直接寫死在這裡)

# ==========================================



# GPIO 腳位

PIN_BASE     = 19  # 底座

PIN_SHOULDER = 13  # 左臂 (肩)

PIN_ELBOW    = 12  # 右臂 (肘/Middle)

PIN_GRIPPER  = 18  # 夾爪



# 三檔位設定 (PWM 脈衝)

# [第1檔, 第2檔(中間), 第3檔]

DATA = {

    "1": {

        "name": "底座 (Base)",

        "pin": PIN_BASE,

        "levels": [900, 1500, 2000],  # 左, 中, 右

        "desc": ["左 (900)", "中 (1500)", "右 (2000)"]

    },

    "2": {

        "name": "肩膀 (Shoulder)",

        "pin": PIN_SHOULDER,

        "levels": [1000, 1500, 1700], # 下/前, 中, 上/後 (依您最後測試的範圍)

        "desc": ["位置A (1000)", "中 (1500)", "位置B (1700)"]

    },

    "3": {

        "name": "手肘 (Elbow)",

        "pin": PIN_ELBOW,

        "levels": [2000, 1550, 2350], # 後, 中, 前

        "desc": ["後 (2000)", "中 (1550)", "前 (2350)"]

    },

    "4": {

        "name": "夾爪 (Gripper)",

        "pin": PIN_GRIPPER,

        "levels": [1600, 2350],       # 只有兩檔：開, 合

        "desc": ["張開 (1600)", "閉合 (2350)"]

    }

}



# 移動速度 (秒)

SPEED = 0.01 

STEP = 10



# ==========================================

# 2. 驅動邏輯

# ==========================================



pi = pigpio.pi()

if not pi.connected:

    print("❌ pigpiod 沒開！請輸入 sudo systemctl start pigpiod")

    exit()



# 記錄目前各馬達的位置 (預設都給 1500，避免第一步暴衝太快)

current_pos = {

    PIN_BASE: 1500,

    PIN_SHOULDER: 1500,

    PIN_ELBOW: 1500,

    PIN_GRIPPER: 1600

}



def slow_move(pin, target):

    """ 讓馬達慢慢轉過去，比較安全 """

    start = current_pos[pin]

    

    if target > start: step_dir = STEP

    else: step_dir = -STEP

    

    # 開始移動

    for pwm in range(start, target, step_dir):

        pi.set_servo_pulsewidth(pin, pwm)

        time.sleep(SPEED)

        

    # 確保到位

    pi.set_servo_pulsewidth(pin, target)

    current_pos[pin] = target # 更新記憶



# ==========================================

# 3. 主程式選單

# ==========================================



print("\n🤖 機械手臂 分檔測試器 🤖")

print("---------------------------")



try:

    while True:

        print("\n請選擇要操作的馬達:")

        print(" [1] 底座 (Base)")

        print(" [2] 肩膀 (Shoulder)")

        print(" [3] 手肘 (Elbow)")

        print(" [4] 夾爪 (Gripper)")

        print(" [q] 離開並放鬆")

        

        motor_choice = input(">> ").strip().lower()

        

        if motor_choice == 'q':

            break

            

        if motor_choice not in DATA:

            print("❌ 輸入錯誤，請選 1~4")

            continue

            

        # 取得該馬達的資料

        motor = DATA[motor_choice]

        print(f"\n👉 您選擇了: {motor['name']}")

        print("請選擇檔位:")

        

        # 動態顯示檔位選項

        for i, desc in enumerate(motor['desc']):

            print(f"   [{i+1}] {desc}")

            

        level_choice = input(">> ").strip()

        

        # 檢查輸入是否合法

        try:

            idx = int(level_choice) - 1

            if 0 <= idx < len(motor['levels']):

                target_pwm = motor['levels'][idx]

                print(f"   ---> 執行移動... 目標: {target_pwm}")

                slow_move(motor['pin'], target_pwm)

                print("   ✅ 完成")

            else:

                print("❌ 無效的檔位")

        except ValueError:

            print("❌ 請輸入數字")



except KeyboardInterrupt:

    pass

finally:

    print("\n程式結束，放鬆所有馬達...")

    for p in [PIN_BASE, PIN_SHOULDER, PIN_ELBOW, PIN_GRIPPER]:

        pi.set_servo_pulsewidth(p, 0)

    pi.stop()