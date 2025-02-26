import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# 기본 경로 설정
base_path = r"  --직접 설정--"

# Forward Vector 계산
def compute_forward_vector(qx, qy, qz, qw):
    x = 2 * (qx * qz + qy * qw)
    y = 2 * (qy * qz - qx * qw)
    z = 1 - 2 * (qx**2 + qy**2)
    return x, y, z

# 각도 계산
def compute_angles(x, y, z):
    vertical_angle = np.arctan2(-z, x)
    horizontal_angle = np.arccos(-y)
    if vertical_angle < 0:
        vertical_angle = 2 * np.pi + vertical_angle
    return vertical_angle, horizontal_angle

# 텍스처 좌표 변환
def compute_uv(vertical_angle, horizontal_angle):
    u = vertical_angle / (2.0 * np.pi)
    v = horizontal_angle / np.pi
    return u, v

# 픽셀 좌표 변환
def compute_pixel_coordinates(u, v, width=2560, height=1440):
    x = round(u * width)
    y = round(v * height)
    return x, y

# 시각화용 데이터 저장 리스트
pixel_xs = []
pixel_ys = []

# 찾고자 하는 PlaybackTime
target_playback_time =  142  # 시각화하고 싶은 초 단위 (ex. 02:22 의 경우, 142로 설정)

# 사용자 1~48 반복
for user_id in range(1, 49):
    file_path = os.path.join(base_path, str(user_id), "video_1.csv")
    
    if os.path.exists(file_path):  # 파일 존재 여부 확인
        df = pd.read_csv(file_path)
        
        # PlaybackTime이 22초와 가장 가까운 값 찾기
        closest_index = (df["PlaybackTime"] - target_playback_time).abs().idxmin()
        
        # Forward Vector 계산
        qx, qy, qz, qw = df.loc[closest_index, ["UnitQuaternion.x", "UnitQuaternion.y", "UnitQuaternion.z", "UnitQuaternion.w"]]
        x, y, z = compute_forward_vector(qx, qy, qz, qw)
        
        # 각도 계산
        v_angle, h_angle = compute_angles(x, y, z)
        
        # UV 좌표 변환
        u, v = compute_uv(v_angle, h_angle)
        
        # 픽셀 좌표 변환
        pixel_x, pixel_y = compute_pixel_coordinates(u, v)
        
        # 리스트에 저장
        pixel_xs.append(pixel_x)
        pixel_ys.append(pixel_y)

# 그래프 시각화
plt.figure(figsize=(10, 6))
plt.scatter(pixel_xs, pixel_ys, color='green', s=50, label="Users' Playback ??:?? point") # ??:?? 재생 시간 수정
plt.xlim(0, 2560)
plt.ylim(0, 1440)  # y축을 0부터 1440까지 증가하도록 설정
plt.xlabel("Pixel X")
plt.ylabel("Pixel Y")
plt.title("PlaybackTime ??:?? Data Points for Users 1 to 48")  # ??:?? 재생 시간 수정
plt.legend()
plt.grid(True)

# 그래프 출력
plt.show()
