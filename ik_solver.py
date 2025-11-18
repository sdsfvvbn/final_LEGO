import math

# ==========================================
# 1. 請拿出尺，測量您的手臂長度 (單位: mm)
# ==========================================
# L0 = 底座高度 (從地面到第二個馬達軸心的垂直距離)
# L1 = 大臂長度 (第二個馬達軸心 到 第三個馬達軸心)
# L2 = 小臂長度 (第三個馬達軸心 到 第四個馬達軸心)
# L3 = 夾爪長度 (第四個馬達軸心 到 夾爪尖端)
L1 = 105.0 
L2 = 90.0 
# 我們簡化計算，假設夾爪永遠垂直向下，或者把 L2+L3 當作一段
# 這裡提供一個標準 3軸 (底座+肩+肘) 的算法

def solve_angles(x, y, z):
    """
    輸入: 目標座標 (x, y, z)
    輸出: [底座角度, 肩膀角度, 手肘角度] (度)
    如果回傳 None，代表那個位置手伸不到
    """
    try:
        # --- 1. 計算底座旋轉 (Base Yaw) ---
        # 使用 atan2 算出水平面角度
        theta_base = math.atan2(y, x)
        angle_base = math.degrees(theta_base)

        # --- 2. 計算手臂伸展 (幾何解法) ---
        # 目標點在水平面上的投影距離 (不含 Z)
        r_target = math.sqrt(x**2 + y**2)
        
        # 我們要算的三角形邊長：
        # c = 從肩膀關節直接連到目標點的直線距離
        # z_offset = 目標高度 - 底座高度 (相對高度)
        # 這裡假設底座高度約 50mm (請依實際修改)
        base_height = 50.0 
        z_relative = z - base_height
        
        # 斜邊 c 的長度 (畢氏定理)
        c = math.sqrt(r_target**2 + z_relative**2)
        
        # 如果 c 太長 (超過手臂總長)，代表伸不到
        if c > (L1 + L2):
            print(f"❌ 錯誤：目標太遠了！距離 {c:.1f} > 手臂總長 {L1+L2}")
            return None

        # --- 3. 餘弦定理 (Law of Cosines) ---
        # 計算三角形的三個角
        # alpha: 肩膀仰角的一部分
        # beta:  手肘彎曲角
        
        # 算出肩膀對於「斜邊c」的夾角 (a1)
        acos_arg1 = (L1**2 + c**2 - L2**2) / (2 * L1 * c)
        # 限制範圍避免數學錯誤 (-1 ~ 1)
        acos_arg1 = max(-1, min(1, acos_arg1))
        a1 = math.acos(acos_arg1)
        
        # 算出斜邊c對於水平線的仰角 (a2)
        a2 = math.atan2(z_relative, r_target)
        
        # 肩膀總角度 = a1 + a2
        theta_shoulder = a1 + a2
        angle_shoulder = math.degrees(theta_shoulder)
        
        # 算出手肘內角
        acos_arg2 = (L1**2 + L2**2 - c**2) / (2 * L1 * L2)
        acos_arg2 = max(-1, min(1, acos_arg2))
        theta_elbow = math.acos(acos_arg2)
        
        # 轉換成馬達角度 (視您的馬達安裝方向而定，可能要用 180 去減)
        angle_elbow = 180 - math.degrees(theta_elbow)

        return [angle_base, angle_shoulder, angle_elbow]

    except Exception as e:
        print(f"計算錯誤: {e}")
        return None

# --- 本地測試 (不接馬達也能測) ---
if __name__ == "__main__":
    print("測試 IK 計算...")
    # 測試點：前方 100mm, 高度 50mm
    result = solve_angles(100, 0, 50)
    if result:
        print(f"目標 (100, 0, 50) -> 馬達角度: {result}")
    else:
        print("計算失敗")