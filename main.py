# --- 在 main.py 最上面設定 ---
# 這是您拿尺量出來的數據
OFFSET_X = 150.0  # 底板(0,0) 距離 手臂中心 的 X 距離 (mm)
OFFSET_Y = -50.0  # 底板(0,0) 距離 手臂中心 的 Y 距離 (mm) (負數代表在右邊，正數在左邊)
OFFSET_Z = 10.0   # 底板表面的高度 (mm)

def brick_to_real(b_x, b_y, b_z):
    """
    將 BrickGPT 座標 (格數) 轉換為 機械手臂座標 (mm)
    """
    # 1. 單位換算
    mm_x = b_x * 8.0
    mm_y = b_y * 8.0
    mm_z = b_z * 9.6
    
    # 2. 加上偏移量
    real_x = OFFSET_X + mm_x
    real_y = OFFSET_Y + mm_y
    real_z = OFFSET_Z + mm_z
    
    return real_x, real_y, real_z

# --- 使用範例 ---
# 假設 BrickGPT 說: 2x4 (10, 5, 0)
real_x, real_y, real_z = brick_to_real(10, 5, 0)
print(f"手臂要去的位置: X={real_x}, Y={real_y}, Z={real_z}")
# 接著呼叫 IK 運算: calculate_ik(real_x, real_y, real_z)