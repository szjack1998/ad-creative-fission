#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态视频分析 - 时序分段抽帧 + 拼图
把一段视频按时间轴切成 N 段，每段密集抽帧拼成一张横向 grid，
命名带时间段，便于多模态逐段分析动态变化/转场/节奏。
"""
import cv2, os, sys, math

import argparse as _ap

def _resolve_base():
    """数据根目录：放置 frames_batch/ grid_frames/ 各 csv/json。可用 --base 覆盖。"""
    _p = _ap.ArgumentParser(add_help=False)
    _p.add_argument('--base', default=r'C:\Users\Administrator\WorkBuddy\2026-07-14-11-51-15',
                    help='数据根目录(含 frames_batch/ grid_frames/ 各csv/json)')
    _a, _ = _p.parse_known_args()
    return _a.base

BASE = _resolve_base()

def extract_segments(mat_id, n_seg=4, per_seg=6, out_dir=None):
    vid_dir = os.path.join(BASE, 'frames_batch', mat_id)
    vid_path = os.path.join(vid_dir, 'video.mp4')
    if not os.path.exists(vid_path):
        print(f'[ERR] 视频不存在: {vid_path}')
        return []
    cap = cv2.VideoCapture(vid_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    dur = total / fps if fps else 0
    cap.release()

    seg_dir = out_dir or os.path.join(vid_dir, 'segments')
    os.makedirs(seg_dir, exist_ok=True)
    # 清旧
    for f in os.listdir(seg_dir):
        if f.endswith('.png'):
            os.remove(os.path.join(seg_dir, f))

    seg_len = dur / n_seg
    results = []
    for s in range(n_seg):
        t0 = s * seg_len
        t1 = (s + 1) * seg_len
        # 在该段内均匀取 per_seg 帧
        ts = [t0 + (i + 0.5) * (t1 - t0) / per_seg for i in range(per_seg)]
        frames = []
        for tt in ts:
            cap = cv2.VideoCapture(vid_path)
            cap.set(cv2.CAP_PROP_POS_FRAMES, int(tt * fps))
            ok, fr = cap.read()
            cap.release()
            if ok:
                # resize 到高度统一，便于拼横向 grid
                h, w = fr.shape[:2]
                nh = 240
                nw = int(w * nh / h)
                fr = cv2.resize(fr, (nw, nh))
                frames.append(fr)
        if not frames:
            continue
        # 横向拼 (1 行 per_seg 列) 或 2 行
        cols = per_seg
        rows = 1
        # 拼成一行
        grid = cv2.hconcat(frames)
        # 底部加时间段标注条
        label_h = 36
        canvas = cv2.copyMakeBorder(grid, 0, label_h, 0, 0, cv2.BORDER_CONSTANT, value=(20, 20, 20))
        # 用 putText 写时间段
        txt = f'seg{s+1}  {t0:.1f}s - {t1:.1f}s'
        cv2.putText(canvas, txt, (10, canvas.shape[0] - 12),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        out = os.path.join(seg_dir, f'seg{s+1}_{t0:.0f}-{t1:.0f}s.png')
        cv2.imwrite(out, canvas)
        results.append((s + 1, t0, t1, out))
        print(f'  seg{s+1}: {t0:.1f}s~{t1:.1f}s -> {out}')

    print(f'\n视频 {mat_id}: 时长 {dur:.1f}s, 切成 {len(results)} 段, 每段 {per_seg} 帧')
    return results

if __name__ == '__main__':
    mat_id = sys.argv[1] if len(sys.argv) > 1 else '10000000001'
    n_seg = int(sys.argv[2]) if len(sys.argv) > 2 else 4
    per_seg = int(sys.argv[3]) if len(sys.argv) > 3 else 6
    extract_segments(mat_id, n_seg, per_seg)
