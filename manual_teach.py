import sys
import select
import tty
import termios
import time
from arm_driver import MeArm

# --- 初始化 ---
bot = MeArm()

# 初始位置 (全部 50%)
pos = {
    'base': 50,
    'shoulder': 50,
    'elbow': 50,
    'gripper': 0  # 0=張開
}

# 移動步距 (按一下動多少)
STEP = 2 

def get_key():
    """ 讀取鍵盤輸入 (不需按 Enter) """
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return key

def apply_moves():
    """ 將目前的 pos 數值發送給馬達 """
    bot.move_base(pos['base'])
    bot.move_shoulder(pos['shoulder'])
    bot.move_middle(pos['elbow']) # 注意：您的 driver 裡可能是叫 move_middle 或 move_elbow
    bot.move_gripper(pos['gripper'])

def save_record(name):
    """ 將目前位置寫入檔案 """
    with open("saved_positions.txt", "a") as f:
        line = f"{name} = {pos}\n"
        f.write(line)
    print(f"\n✅ 已儲存紀錄: {name} -> {pos}")

# --- 主程式 ---
print("=== 機械手臂手動示教模式 ===")
print(" [W/S] 肩膀 (Shoulder) 前後")
print(" [A/D] 底座 (Base) 左右")
print(" [I/K] 手肘 (Elbow) 上下")
print(" [O/L] 夾爪 (Gripper) 開閉")
print(" -------------------------")
print(" [1] 儲存為 '2x4_feeder' (2x4供料點)")
print(" [2] 儲存為 '2x2_feeder' (2x2供料點)")
print(" [0] 儲存為 'origin_0_0' (底板原點)")
print(" [Space] 顯示目前數值")
print(" [Q] 離開")
print("==========================")

# 先移動到初始位置
apply_moves()

try:
    while True:
        key = get_key()
        if key == '': continue # 沒按鍵就略過
        
        key = key.lower() # 轉小寫方便判斷

        # --- 控制邏輯 ---
        
        # 1. 底座 (A/D)
        if key == 'a': pos['base'] = min(100, pos['base'] + STEP)
        elif key == 'd': pos['base'] = max(0, pos['base'] - STEP)
        
        # 2. 肩膀 (W/S)
        elif key == 'w': pos['shoulder'] = min(100, pos['shoulder'] + STEP)
        elif key == 's': pos['shoulder'] = max(0, pos['shoulder'] - STEP)
        
        # 3. 手肘 (I/K)
        elif key == 'i': pos['elbow'] = min(100, pos['elbow'] + STEP)
        elif key == 'k': pos['elbow'] = max(0, pos['elbow'] - STEP)
        
        # 4. 夾爪 (O/L)
        elif key == 'l': pos['gripper'] = min(100, pos['gripper'] + 5) # 夾緊 (步距大一點)
        elif key == 'o': pos['gripper'] = max(0, pos['gripper'] - 5)   # 張開

        # --- 儲存指令 ---
        elif key == '1': save_record("FEEDER_2x4")
        elif key == '2': save_record("FEEDER_2x2")
        elif key == '0': save_record("ORIGIN_0_0_0")
        
        # --- 其他 ---
        elif key == ' ': # 空白鍵看數據
            print(f"\r目前狀態: {pos}", end="")
        elif key == 'q':
            break
            
        # 執行移動
        apply_moves()
        # 稍微延遲避免 CPU 飆高
        time.sleep(0.05)

except KeyboardInterrupt:
    pass
finally:
    print("\n程式結束，放鬆馬達...")
    bot.close()