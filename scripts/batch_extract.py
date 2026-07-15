import json, os, subprocess, sys, argparse
import cv2

WORK = os.path.dirname(os.path.abspath(__file__))

def get_top(json_path, n):
    with open(json_path, encoding='utf-8') as f:
        obj = json.load(f)
    lst = obj['data']['list']
    have = [r for r in lst if r.get('视频链接')]
    have.sort(key=lambda x: float(x.get('花费(元)') or 0), reverse=True)
    return have[:n]

def download(url, out):
    subprocess.run(['curl', '-L', '-A', 'Mozilla/5.0', '--max-time', '180', '-o', out, url],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def extract_frames(video, out_dir, max_frames=10):
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        return []
    total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    dur = total / fps if fps else 0
    os.makedirs(out_dir, exist_ok=True)
    times = []
    for t in [0, 1, 2, 3]:
        if t < dur:
            times.append(float(t))
    t = 4.0
    while t < dur:
        times.append(t)
        t += 2.0
    times = sorted(set(times))[:max_frames]
    paths = []
    for i, t in enumerate(times):
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            continue
        p = os.path.join(out_dir, f'frame_{i:02d}_{int(t)}s.png')
        cv2.imwrite(p, frame, [cv2.IMWRITE_PNG_COMPRESSION, 3])
        paths.append(p)
    cap.release()
    return paths

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--json', default='material_video.json')
    ap.add_argument('--out', default='frames_batch')
    ap.add_argument('--top', type=int, default=20)
    args = ap.parse_args()
    top = get_top(args.json, args.top)
    manifest = {}
    for idx, r in enumerate(top, 1):
        mid = r['视频素材ID']
        url = r['视频链接']
        cost = r.get('花费(元)')
        vdir = os.path.join(args.out, str(mid))
        os.makedirs(vdir, exist_ok=True)
        vpath = os.path.join(vdir, 'video.mp4')
        print(f'[{idx}/{len(top)}] {mid} cost={cost}', flush=True)
        try:
            if not os.path.exists(vpath) or os.path.getsize(vpath) < 1000:
                download(url, vpath)
            frames = extract_frames(vpath, vdir)
            manifest[mid] = {'cost': cost, 'video': vpath, 'frames': frames}
            print(f'  frames={len(frames)}', flush=True)
        except Exception as e:
            print(f'  ERR {e}', flush=True)
            manifest[mid] = {'cost': cost, 'error': str(e)}
    with open(os.path.join(args.out, 'manifest.json'), 'w', encoding='utf-8') as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)
    print('DONE', len(manifest))

if __name__ == '__main__':
    main()
