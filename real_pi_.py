import requests
import time
import math

# --- 1. 設定區 (每次跑都要檢查這裡！) ---

# 請貼上您 Colab "儲存格 5" 跑出來的那個 ngrok 網址
# 注意：結尾不要有斜線 /
FLASK_SERVER_URL = "https://convoluted-emeline-counteractingly.ngrok-free.dev/" 

# 檢查任務的頻率 (秒)
POLL_INTERVAL = 5 

# --- 2. 機械手臂地圖 (這就是您要拿尺量的東西) ---
# 假設手臂底座中心是 (0,0)
BASE_X = 150.0  # 底板左下角 X 座標
BASE_Y = 0.0    # 底板左下角 Y 座標
BASE_Z = 50.0   # 底板高度

# 供料區座標 (假設您有兩個倉庫)
FEEDER_LOCATIONS = {
    "1x2": {"x": 50, "y": 200, "z": 20}, 
    "2x2": {"x": -50, "y": 200, "z": 20},
    "2x4": {"x": 0, "y": 250, "z": 20},
    # 如果遇到沒定義的積木，程式會報錯，您可以之後慢慢補
}

# -------------------------------------------

def get_job_from_server():
    """ 去 Colab 問問看有沒有工作 """
    print(f"[{time.strftime('%H:%M:%S')}] 正在詢問伺服器...")
    try:
        response = requests.get(f"{FLASK_SERVER_URL}/get-job", timeout=5)
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "pending":
                return data['bricks'] # 拿到積木列表了！
    except Exception as e:
        print(f"連線錯誤: {e}")
    return None

# --- 3. 模擬動作函式 (假裝自己在動) ---

def inverse_kinematics_simulation(x, y, z):
    """ 
    這是【逆向運動學】的空殼函式 
    未來您要在這裡填入數學公式，把 (x,y,z) 轉成 (angle1, angle2...)
    """
    # 這裡我們先隨便回傳假的角度，假裝有在算
    print(f"   [數學運算] 目標 ({x}, {y}, {z}) -> 算出馬達角度: [45, 90, 60, 0]")
    return [45, 90, 60, 0]

def move_arm_to(x, y, z, description):
    """ 模擬手臂移動 """
    print(f"➡️ [動作] 手臂移動到: {description} (座標: {x}, {y}, {z})")
    
    # 1. 呼叫數學函式
    angles = inverse_kinematics_simulation(x, y, z)
    
    # 2. 假裝送訊號給馬達 (未來這裡要寫 pi.set_servo_pulsewidth...)
    print(f"   [硬體訊號] 滋...滋... (馬達轉到 {angles})")
    
    # 3. 假裝花了一點時間移動
    time.sleep(1) 

def gripper_action(action):
    """ 模擬夾爪 """
    print(f"🖐 [夾爪] {action}！")
    time.sleep(0.5)

# --- 4. 主要工作流程 ---

def process_job(bricks):
    print(f"\n🚀 收到新任務！總共要拼 {len(bricks)} 塊積木\n")
    
    for i, brick in enumerate(bricks):
        print(f"--- 第 {i+1} 塊積木 ({brick['type']}) ---")
        
        # 1. 查表：去哪裡拿？
        brick_type = brick['type']
        if brick_type not in FEEDER_LOCATIONS:
            print(f"❌ 找不到 {brick_type} 的供料位置，跳過！")
            # 為了模擬順利，我們先假裝去 (0,0,0) 拿
            feeder = {"x":0, "y":200, "z":20}
        else:
            feeder = FEEDER_LOCATIONS[brick_type]
            
        # 2. 計算：要放哪裡？ (網格 -> 真實毫米)
        target_x = BASE_X + (brick['x'] * 8)  # 假設 1 stud = 8mm
        target_y = BASE_Y + (brick['y'] * 8)
        target_z = BASE_Z + (brick['z'] * 9.6) # 假設 1 brick = 9.6mm
        
        # === 開始執行動作序列 ===
        
        # A. 去供料區拿
        move_arm_to(feeder['x'], feeder['y'], feeder['z'] + 20, "供料區上方")
        gripper_action("張開")
        move_arm_to(feeder['x'], feeder['y'], feeder['z'], "供料區取料")
        gripper_action("夾緊")
        move_arm_to(feeder['x'], feeder['y'], feeder['z'] + 50, "抬起")
        
        # B. 去目標區放
        move_arm_to(target_x, target_y, target_z + 20, "目標位置上方")
        move_arm_to(target_x, target_y, target_z, "放置積木")
        gripper_action("張開")
        move_arm_to(target_x, target_y, target_z + 50, "離開")
        
    print("\n✅ 任務完成！手臂回到休息位置。\n")

# --- 5. 主程式迴圈 ---
if __name__ == "__main__":
    print("🤖 樹莓派客戶端 (模擬模式) 啟動中...")
    print(f"🔗 目標伺服器: {FLASK_SERVER_URL}")
    
    try:
        while True:
            job_bricks = get_job_from_server()
            if job_bricks:
                process_job(job_bricks)
            else:
                print(".", end="", flush=True)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\n程式已停止。")