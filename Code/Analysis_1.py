import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 기본 경로 설정
base_path = r"  --직접 설정--  "

# Forward Vector 계산 (쿼터니언 → 벡터)
def compute_forward_vector(qx, qy, qz, qw):
    x = 2 * (qx * qz + qy * qw)
    y = 2 * (qy * qz - qx * qw)
    z = 1 - 2 * (qx**2 + qy**2)
    return x, y, z

# 수직 & 수평 각도 변환 (NaN 방지 처리)
def compute_angles(x, y, z):
    vertical_angle = np.arctan2(-z, x)
    horizontal_angle = np.arccos(np.clip(-y, -1.0, 1.0))  # -1~1 범위 제한하여 NaN 방지
    if vertical_angle < 0:
        vertical_angle = 2 * np.pi + vertical_angle
    return vertical_angle, horizontal_angle

# UV 텍스처 좌표 변환
def compute_uv(vertical_angle, horizontal_angle):
    u = vertical_angle / (2.0 * np.pi)
    v = horizontal_angle / np.pi
    return u, v

# 픽셀 좌표 변환 (NaN 체크 포함)
def compute_pixel_coordinates(u, v, width=2560, height=1440):
    if np.isnan(u) or np.isnan(v):  # NaN 값이 있으면 None 반환
        return None, None
    x = round(u * width)
    y = round(v * height)
    return x, y

# 시각화용 데이터 저장 리스트
pixel_xs = []
pixel_ys = []

# 사용자 1~48 반복
for user_id in range(1, 49):
    file_path = os.path.join(base_path, str(user_id), "video_1.csv")
    
    if os.path.exists(file_path):  # 파일 존재 여부 확인
        df = pd.read_csv(file_path)
        
        # 모든 프레임에 대해 좌표 변환 수행
        for i in range(len(df)):
            qx, qy, qz, qw = df.loc[i, ["UnitQuaternion.x", "UnitQuaternion.y", "UnitQuaternion.z", "UnitQuaternion.w"]]
            x, y, z = compute_forward_vector(qx, qy, qz, qw)
            v_angle, h_angle = compute_angles(x, y, z)
            u, v = compute_uv(v_angle, h_angle)
            pixel_x, pixel_y = compute_pixel_coordinates(u, v)

            # NaN 값이 아닌 경우만 저장
            if pixel_x is not None and pixel_y is not None:
                pixel_xs.append(pixel_x)
                pixel_ys.append(pixel_y)

# 그래프 시각화
plt.figure(figsize=(12, 7))
plt.scatter(pixel_xs, pixel_ys, color='blue', s=0.5, alpha=0.1)  # 작은 점과 낮은 투명도 설정
plt.xlim(0, 2560)
plt.ylim(0, 1440)  # y축을 0부터 1440까지 증가하도록 설정
plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")
plt.title("All Users' Viewing Records")
plt.grid(True)

# 그래프 출력
plt.show()
