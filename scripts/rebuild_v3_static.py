import csv, os, base64

import argparse as _ap

def _resolve_base():
    """数据根目录：放置 frames_batch/ grid_frames/ 各 csv/json。可用 --base 覆盖。"""
    _p = _ap.ArgumentParser(add_help=False)
    _p.add_argument('--base', default=r'C:\Users\Administrator\WorkBuddy\2026-07-14-11-51-15',
                    help='数据根目录(含 frames_batch/ grid_frames/ 各csv/json)')
    _a, _ = _p.parse_known_args()
    return _a.base

base = _resolve_base()
csv_path = os.path.join(base, 'videos_multimodal.csv')
grid_dir = os.path.join(base, 'grid_frames')
html_path = os.path.join(base, 'demo_multimodal_copy_report.html')

rows = []
with open(csv_path, 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

# Compute stats
tc = sum(float(r['花费(元)']) or 0 for r in rows)
ac = sum(1 for r in rows if r['证书类别'] == 'AI应用工程师')
hc = len(rows) - ac
dc = sum(1 for r in rows if '同素材' in r.get('通顺文案', ''))

# Build cards HTML
cards_html = []
for i, r in enumerate(rows):
    img_id = r['素材ID']
    img_path = os.path.join(grid_dir, f'{img_id}.png')
    
    # Read and encode image
    b64 = ''
    if os.path.exists(img_path):
        with open(img_path, 'rb') as f:
            b64 = base64.b64encode(f.read()).decode('ascii')
    
    D = '同素材' in r.get('通顺文案', '')
    A = r['证书类别'] == 'AI应用工程师'
    c = float(r['CTR(%)']) or 0
    v = float(r['CVR(%)']) or 0
    cost = float(r['花费(元)']) or 0
    clicks = int(r['点击数'] or 0)
    conv = int(r['转化量'] or 0)
    
    copy_text = r.get('通顺文案', '').replace('\n', '<br>')
    # Escape for HTML safety
    import html as htmlescape
    copy_text = htmlescape.escape(copy_text)
    hook = htmlescape.escape(r.get('钩子类型', ''))
    vtype = htmlescape.escape(r.get('视频类型', ''))
    
    badge_var = '<span class="b bd">变体</span> ' if D else ''
    badge_cat = f'<span class="b {"bai" if A else "bh"}">{htmlescape.escape(r["证书类别"])}</span>'
    ct_cls = '' if A else ' hb'
    color_ctr = ' class="gn"' if c >= 1 else ''
    color_cvr = ' class="gn"' if v >= 3 else ''
    
    card = f'''<div class="card">
<div class="ch"><span class="id">#{i+1}&middot;{img_id}</span>{badge_var}{badge_cat}</div>
<div class="ci"><img src="data:image/png;base64,{b64}" alt="{img_id}"></div>
<div class="cb">
<div class="ct{ct_cls}">{copy_text}</div>
<div style="display:flex;justify-content:space-between"><span class="ht">&#x1F3AF; {hook}</span><span style="font-size:11px;color:#64748b">{vtype}</span></div>
<div class="ms" style="margin-top:10px">
<div class="m"><div class="v">&yen;{int(cost):,}</div><div class="k">花费</div></div>
<div class="m"><div class="v"{color_ctr}>{c:.2f}%</div><div class="k">CTR</div></div>
<div class="m"><div class="v"{color_cvr}>{v:.2f}%</div><div class="k">CVR</div></div>
<div class="m"><div class="v">{clicks:,}</div><div class="k">点击</div></div>
<div class="m"><div class="v">{conv}</div><div class="k">转化</div></div>
</div></div></div>'''
    cards_html.append(card)

from datetime import datetime
now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

full_html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>某教育行业客户 &middot; 视频素材多模态文案拆解报告</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f8f9fc;color:#1e293b;padding:20px}}
.header{{max-width:1400px;margin:0 auto 24px}}.header h1{{font-size:22px;font-weight:700}}
.header p{{color:#64748b;margin-top:4px;font-size:14px}}
.stats{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px}}
.sc{{background:#fff;border:1px solid #e2e6f0;border-radius:10px;padding:16px 20px;min-width:140px}}
.sc .n{{font-size:28px;font-weight:700}}.sc .l{{font-size:12px;color:#64748b;margin-top:2px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(680px,1fr));gap:18px;max-width:1400px;margin:0 auto}}
.card{{background:#fff;border:1px solid #e2e6f0;border-radius:12px;overflow:hidden}}
.ch{{padding:14px 16px;border-bottom:1px solid #e2e6f0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:4px}}
.ch .id{{font-size:13px;font-weight:600;color:#64748b}}
.b{{font-size:11px;padding:3px 10px;border-radius:20px;font-weight:500}}
.bai{{background:#ede9fe;color:#4f46e5}}.bh{{background:#ecfdf5;color:#059669}}.bd{{background:#fef3c7;color:#d97706}}
.ci img{{width:100%;height:auto;display:block;max-height:400px;object-fit:contain;background:#000}}
.cb{{padding:14px 16px}}
.ct{{font-size:14.5px;line-height:1.75;color:#1e293b;margin-bottom:10px;padding:10px 14px;background:#fafafa;border-radius:8px;border-left:3px solid #4f46e5}}
.ct.hb{{border-left-color:#059669}}
.ms{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px}}
.m{{text-align:center;padding:8px 4px;background:#f8fafc;border-radius:6px}}
.m .v{{font-size:15px;font-weight:700}}.m .k{{font-size:11px;color:#64748b}}
.ht{{display:inline-block;font-size:11px;padding:2px 8px;background:#eff6ff;color:#1d4ed8;border-radius:4px;margin-top:6px}}
.ft{{max-width:1400px;margin:24px auto;text-align:center;color:#64748b;font-size:12px}}
.gn{{color:#16a34a}}.rd{{color:#dc2626}}
</style></head>
<body>
<div class="header"><h1>&#x1F3AC; 某教育行业客户 &middot; 视频素材多模态文案拆解报告</h1>
<p>Top{len(rows)} 视频 &middot; 多模态逐帧阅读通顺口播稿 &middot; 腾讯广告妙问API拉取真实消耗数据</p></div>
<div class="stats">
<div class="sc"><div class="n">{len(rows)}</div><div class="l">拆解素材数</div></div>
<div class="sc"><div class="n" style="color:#d97706">&yen;{int(tc):,}</div><div class="l">合计花费</div></div>
<div class="sc"><div class="n" style="color:#4f46e5">{ac}</div><div class="l">AI应用工程师</div></div>
<div class="sc"><div class="n" style="color:#059669">{hc}</div><div class="l">健康管理师</div></div>
<div class="sc"><div class="n">{dc}</div><div class="l">同素材变体</div></div>
</div>
<div class="grid">
{''.join(cards_html)}
</div>
<div class="ft">生成时间：{now} | 妙问API&rarr;视频下载&rarr;opencv抽帧&rarr;多模态读图&rarr;通顺文案映射</div>
</body></html>'''

with open(html_path, 'w', encoding='utf-8') as f:
    f.write(full_html)

print(f'Done! {os.path.getsize(html_path)/1024/1024:.0f} MB, {len(rows)} cards, ZERO JS')
