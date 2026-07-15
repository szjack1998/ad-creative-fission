#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态视频分析引擎 — 程序化版本
对每个本地视频做：
1. 基础元数据（时长/分辨率/FPS）
2. 转场检测（帧间直方图差分 → 找真实切镜点）
3. 运动幅度（逐秒帧差均值 → 节奏/快慢）
4. 色彩风格（主色调/亮度/饱和度）
5. 场景一致性（单机位 vs 多场景）
6. 映射已知文案到时间轴

输出：dynamic_analysis.json + 可喂给报告生成器的结构化数据
"""
import cv2, os, json, csv, math, numpy as np
from collections import Counter

import argparse as _ap

def _resolve_base():
    """数据根目录：放置 frames_batch/ grid_frames/ 各 csv/json。可用 --base 覆盖。"""
    _p = _ap.ArgumentParser(add_help=False)
    _p.add_argument('--base', default=r'C:\Users\Administrator\WorkBuddy\2026-07-14-11-51-15',
                    help='数据根目录(含 frames_batch/ grid_frames/ 各csv/json)')
    _a, _ = _p.parse_known_args()
    return _a.base

BASE = _resolve_base()
VID_DIR = os.path.join(BASE, 'frames_batch')
FIXED_CSV = os.path.join(BASE, 'videos_multimodal_fixed.csv')
OUT_JSON = os.path.join(BASE, 'dynamic_analysis.json')
OUT_CSV = os.path.join(BASE, 'dynamic_analysis.csv')

# 加载已知文案映射
COPY_MAP = {}
with open(FIXED_CSV, 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        COPY_MAP[row['素材ID']] = {
            'copy': row.get('通顺文案', ''),
            'cert_type': row.get('证书类别', ''),
            'hook': row.get('钩子类型', ''),
            'vtype': row.get('视频类型', ''),
            'cost': float(row.get('花费(元)', 0) or 0),
            'ctr': float(row.get('CTR(%)', 0) or 0),
            'cvr': float(row.get('CVR(%)', 0) or 0),
            'clicks': int(float(row.get('点击数', 0) or 0)),
            'conv': int(float(row.get('转化量', 0) or 0)),
        }

def analyze_video(mat_id):
    """分析单个视频的动态特征"""
    vid_path = os.path.join(VID_DIR, mat_id, 'video.mp4')
    if not os.path.exists(vid_path):
        return None

    cap = cv2.VideoCapture(vid_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total / fps if fps else 0
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # 采样：每秒取一帧做分析
    sample_interval = max(1, int(fps))
    frames_data = []
    prev_gray = None
    diffs = []
    hist_diffs = []
    colors = []

    frame_idx = 0
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
        ok, fr = cap.read()
        if not ok:
            break
        gray = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)

        # 运动幅度：与前一帧的像素差
        if prev_gray is not None:
            diff = np.mean(np.abs(gray.astype(float) - prev_gray.astype(float)))
            diffs.append(diff)
        prev_gray = gray.copy()

        # 直方图差分（用于转场检测）
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_norm = hist / (hist.sum() + 1e-7)
        colors.append(hist_norm)
        if len(colors) >= 2:
            hd = np.sum(np.abs(colors[-2] - colors[-1]))
            hist_diffs.append(hd)

        # 色彩特征
        bgr_mean = np.mean(fr, axis=(0, 1))
        hsv = cv2.cvtColor(fr, cv2.COLOR_BGR2HSV)
        sat = np.mean(hsv[:, :, 1]) / 255.0
        val = np.mean(hsv[:, :, 2]) / 255.0
        colors_bgr = {
            'r': int(bgr_mean[2]),
            'g': int(bgr_mean[1]),
            'b': int(bgr_mean[0]),
            'sat': round(sat, 3),
            'val': round(val, 3),
        }

        frames_data.append({
            'frame': frame_idx,
            'time_sec': round(frame_idx / fps, 2),
            'motion': round(diffs[-1], 3) if diffs else 0,
            **colors_bgr,
        })

        frame_idx += sample_interval

    cap.release()

    if len(frames_data) < 2:
        return None

    # === 分析结果 ===

    # 1. 转场检测：直方图差分峰值
    arr_hd = np.array(hist_diffs) if hist_diffs else np.zeros(len(diffs))
    threshold = np.mean(arr_hd) + 2.5 * np.std(arr_hd)  # 2.5 sigma 阈值
    transitions = []
    for i, hd_val in enumerate(arr_hd):
        if hd_val > threshold:
            t_sec = (i + 1) * sample_interval / fps
            transitions.append(round(t_sec, 1))

    # 如果没有超过阈值的转场点，检查是否有明显跳变
    if not transitions and len(arr_hd) > 0:
        max_hds = np.argsort(arr_hd)[-min(3, len(arr_hd)):]
        for idx in sorted(max_hds):
            t_sec = (idx + 1) * sample_interval / fps
            if arr_hd[idx] > np.mean(arr_hd) * 1.5:
                transitions.append(round(t_sec, 1))

    # 2. 节奏/运动分析
    motion_arr = np.array(diffs) if diffs else np.zeros(1)
    avg_motion = round(float(np.mean(motion_arr)), 3)
    peak_motion = round(float(np.max(motion_arr)), 3)
    motion_std = round(float(np.std(motion_arr)), 3)

    # 每秒运动强度（用于节奏曲线）
    rhythm = {}
    for fd in frames_data:
        sec = int(fd['time_sec'])
        rhythm.setdefault(sec, []).append(fd['motion'])

    rhythm_curve = {k: round(sum(v)/len(v), 3) for k, v in rhythm.items()}

    # 3. 色彩风格
    avg_sat = np.mean([fd['sat'] for fd in frames_data])
    avg_val = np.mean([fd['val'] for fd in frames_data])
    avg_r = np.mean([fd['r'] for fd in frames_data])
    avg_g = np.mean([fd['g'] for fd in frames_data])
    avg_b = np.mean([fd['b'] for fd in frames_data])

    # 风格分类
    style_flags = []
    # 高亮背景判断（高亮度+低饱和度=接近白色/纯色）
    is_bright_bg = avg_val > 0.65 and avg_sat < 0.35
    if is_bright_bg:
        style_flags.append('亮色/白底')

    # 高饱和度=鲜艳画面
    is_colorful = avg_sat > 0.45
    if is_colorful:
        style_flags.append('鲜艳/彩色')

    # 高运动=动态剪辑
    is_dynamic = avg_motion > 15
    if is_dynamic:
        style_flags.append('高动态/快剪')

    # 有转场=多场景
    has_cuts = len(transitions) >= 2
    if has_cuts:
        style_flags.append('多场景切换')

    if not has_cuts and not is_dynamic:
        style_flags.append('单机位固定镜头')

    result = {
        'material_id': mat_id,
        'duration_s': round(dur, 1),
        'fps': round(fps, 1),
        'resolution': f'{w}x{h}',
        'total_frames_sampled': len(frames_data),

        # 转场
        'transitions': transitions,
        'transition_count': len(transitions),
        'is_single_shot': len(transitions) <= 1,

        # 节奏
        'avg_motion': avg_motion,
        'peak_motion': peak_motion,
        'motion_stability': round(motion_std / (avg_motion + 0.01), 2),  # 低=稳定, 高=波动大
        'rhythm_curve': rhythm_curve,

        # 色彩
        'avg_brightness': round(avg_val, 3),
        'avg_saturation': round(avg_sat, 3),
        'dominant_rgb': [round(avg_r), round(avg_g), round(avg_b)],

        # 风格
        'style_tags': style_flags,
        'style_summary': ', '.join(style_flags),

        # 已知文案映射
        **COPY_MAP.get(mat_id, {}),
    }

    return result


def main():
    # 找所有有 video.mp4 的视频
    mat_ids = []
    for d in sorted(os.listdir(VID_DIR)):
        vp = os.path.join(VID_DIR, d, 'video.mp4')
        if os.path.isfile(vp):
            mat_ids.append(d)

    print(f'开始动态分析 {len(mat_ids)} 个视频...\n')

    results = []
    for i, mid in enumerate(mat_ids):
        print(f'[{i+1}/{len(mat_ids)}] 分析 {mid} ...', end=' ')
        try:
            r = analyze_video(mid)
            if r:
                results.append(r)
                print(f'{r["duration_s"]}s | {r["style_summary"]} | 转场{r["transition_count"]} | 运动{r["avg_motion"]:.1f}')
            else:
                print('SKIP')
        except Exception as e:
            print(f'ERR: {e}')

    # 保存 JSON
    with open(OUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f'\n已保存: {OUT_JSON} ({len(results)} 条)')

    # 保存 CSV
    fields = ['material_id', 'duration_s', 'fps', 'resolution', 'cert_type',
              'cost', 'ctr', 'cvr', 'clicks', 'conv',
              'transition_count', 'is_single_shot',
              'avg_motion', 'peak_motion', 'motion_stability',
              'avg_brightness', 'avg_saturation',
              'style_tags', 'style_summary', 'transitions',
              'copy']
    with open(OUT_CSV, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        w.writeheader()
        w.writerows(results)
    print(f'已保存: {OUT_CSV}')

    # 打印汇总统计
    print('\n===== 动态分析汇总 =====')
    styles = Counter()
    shot_types = {'单机位固定镜头': 0, '多场景': 0}
    for r in results:
        for s in r['style_tags']:
            styles[s] += 1
        if r['is_single_shot']:
            shot_types['单机位固定镜头'] += 1
        else:
            shot_types['多场景'] += 1

    print(f'\n风格分布:')
    for s, c in styles.most_common():
        print(f'  {s}: {c}条')
    print(f'\n拍摄方式:')
    for s, c in shot_types.items():
        print(f'  {s}: {c}条')

    # 按消耗排序 TOP10
    by_cost = sorted([r for r in results if r.get('cost', 0) > 0],
                      key=lambda x: x['cost'], reverse=True)[:10]
    print(f'\nTOP10 消耗素材动态特征:')
    print(f'{"ID":<12} {"时长":>5} {"花费":>9} {"CTR":>6} {"CVR":>6} {"转场":>3} {"运动":>6} {"风格"}')
    print('-' * 80)
    for r in by_cost:
        print(f'{r["material_id"]:<12} {r["duration_s"]:>4.1f}s ¥{r["cost"]:>7,.0f} '
              f'{r["ctr"]:>5.2f}% {r["cvr"]:>5.2f}% {r["transition_count"]:>3} '
              f'{r["avg_motion"]:>5.1f} {r["style_summary"][:25]}')


if __name__ == '__main__':
    main()
