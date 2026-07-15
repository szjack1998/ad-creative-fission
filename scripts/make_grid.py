import json, cv2, os, numpy as np

import argparse as _ap

def _resolve_base():
    """数据根目录：放置 frames_batch/ 抽帧。可用 --base 覆盖。"""
    _p = _ap.ArgumentParser(add_help=False)
    _p.add_argument("--base", default=r"C:\Users\Administrator\WorkBuddy\2026-07-14-11-51-15",
                    help="数据根目录(含 frames_batch/)")
    _a, _ = _p.parse_known_args()
    return _a.base

BASE = _resolve_base()
manifest = json.load(open(f"{BASE}/frames_batch/manifest.json", encoding="utf-8"))
out = f"{BASE}/grid_frames"
os.makedirs(out, exist_ok=True)

COLS = 3
TW = 520  # 单帧拼接宽度

def make_grid(vid, frames):
    imgs = []
    for fp in frames:
        im = cv2.imread(fp)
        if im is None:
            continue
        h, w = im.shape[:2]
        nh = int(TW * h / w)
        im = cv2.resize(im, (TW, nh))
        imgs.append(im)
    if not imgs:
        return None
    rows = (len(imgs) + COLS - 1) // COLS
    while len(imgs) < rows * COLS:
        imgs.append(np.zeros_like(imgs[0]))
    cell_h = imgs[0].shape[0]
    grid_rows = []
    for r in range(rows):
        grid_rows.append(np.hstack(imgs[r * COLS:(r + 1) * COLS]))
    final = np.vstack(grid_rows)
    # 加时间标注
    path = f"{out}/{vid}.png"
    cv2.imwrite(path, final)
    return path

n = 0
for vid, info in manifest.items():
    frames = info.get("frames", [])
    if not frames:
        continue
    p = make_grid(vid, frames)
    if p:
        n += 1
        print(vid, "->", p)
print(f"grid 生成完成: {n} 个视频")
