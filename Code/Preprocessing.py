
import pandas as pd
import numpy as np
import os

# 기본 경로 설정
base_path = r" --경로 지정-- "

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

# 픽셀 좌표 변환
def compute_pixel_coordinates(u, v, width=2560, height=1440):
    if np.isnan(u) or np.isnan(v):  # NaN 값이 있으면 None 반환
        return None, None
    x = round(u * width)
    y = round(v * height)
    return x, y

# Tile ID 계산
def compute_tile_id(x, y, width=2560, height=1440, tile_cols=4, tile_rows=4):
    tile_width = width // tile_cols  # 640
    tile_height = height // tile_rows  # 360
    tile_x = x // tile_width
    tile_y = y // tile_height
    tile_id = tile_y * tile_cols + tile_x
    return tile_id

# 사용자 1~48 반복
for user_id in range(1, 49):
    file_path = os.path.join(base_path, str(user_id), "video_1.csv")
    
    if os.path.exists(file_path):  # 파일 존재 여부 확인
        df = pd.read_csv(file_path)
        
        # 새로운 데이터 저장 리스트
        pixel_xs, pixel_ys, tile_ids = [], [], []
        
        # 모든 프레임에 대해 좌표 변환 수행
        for i in range(len(df)):
            qx, qy, qz, qw = df.loc[i, ["UnitQuaternion.x", "UnitQuaternion.y", "UnitQuaternion.z", "UnitQuaternion.w"]]
            x, y, z = compute_forward_vector(qx, qy, qz, qw)
            v_angle, h_angle = compute_angles(x, y, z)
            u, v = compute_uv(v_angle, h_angle)
            pixel_x, pixel_y = compute_pixel_coordinates(u, v)

            # 유효한 데이터만 저장
            if pixel_x is not None and pixel_y is not None:
                tile_id = compute_tile_id(pixel_x, pixel_y)
                pixel_xs.append(pixel_x)
                pixel_ys.append(pixel_y)
                tile_ids.append(tile_id)

        # DataFrame 생성
        df_new = df.iloc[:len(pixel_xs)].copy()  # 원본 데이터와 동일한 행 유지
        df_new["Pixel_x"] = pixel_xs
        df_new["Pixel_y"] = pixel_ys
        df_new["Tile_ID"] = tile_ids

        # 새 파일 저장
        save_path = os.path.join(base_path, str(user_id), "video_1_with_tile.csv")
        df_new.to_csv(save_path, index=False)

        print(f"✅ 사용자 {user_id} 데이터 저장 완료: {save_path}")
