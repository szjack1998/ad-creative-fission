#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""批量给所有本地视频生成时序分段帧"""
import os, subprocess, sys

import argparse as _ap

def _resolve_base():
    """数据根目录：放置 frames_batch/ grid_frames/ 各 csv/json。可用 --base 覆盖。"""
    _p = _ap.ArgumentParser(add_help=False)
    _p.add_argument('--base', default=r'C:\Users\Administrator\WorkBuddy\2026-07-14-11-51-15',
                    help='数据根目录(含 frames_batch/ grid_frames/ 各csv/json)')
    _a, _ = _p.parse_known_args()
    return _a.base

BASE = _resolve_base()
PY = r'C:\Users\Administrator\.workbuddy\binaries\python\versions\3.13.12\python.exe'

# 找所有有 video.mp4 的目录
vids = []
for d in sorted(os.listdir(os.path.join(BASE, 'frames_batch'))):
    vp = os.path.join(BASE, 'frames_batch', d, 'video.mp4')
    if os.path.isfile(vp):
        vids.append(d)

print(f'发现 {len(vids)} 个本地视频')
ok = 0
for v in vids:
    seg_dir = os.path.join(BASE, 'frames_batch', v, 'segments')
    # 已有则跳过
    if os.path.isdir(seg_dir) and any(f.endswith('.png') for f in os.listdir(seg_dir)):
        print(f'  [skip] {v} 已有分段')
        ok += 1
        continue
    r = subprocess.run([PY, os.path.join(BASE, 'dynamic_frames.py'), v, '4', '6'],
                       capture_output=True, text=True)
    if r.returncode == 0:
        ok += 1
        print(f'  [done] {v}')
    else:
        print(f'  [ERR] {v}: {r.stderr[:200]}')

print(f'\n完成：{ok}/{len(vids)} 视频已生成分段帧')
