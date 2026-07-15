#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态视频分析报告生成器 v4 — 纯静态HTML，零JS
合并四层数据：
  L1 程序化动态特征(opencv) + L2 视觉分类(多模态读图) + L3 真实消耗(妙问API) + L4 通顺文案(多模态拆解)
修复：补回通顺文案字段 / 修复破损<span>标签 / 重构数据排版
"""
import json, csv, os, base64, html as htmlescape
from datetime import datetime

import argparse as _ap

def _resolve_base():
    """数据根目录：放置 frames_batch/ grid_frames/ 各 csv/json。可用 --base 覆盖。"""
    _p = _ap.ArgumentParser(add_help=False)
    _p.add_argument('--base', default=r'C:\Users\Administrator\WorkBuddy\2026-07-14-11-51-15',
                    help='数据根目录(含 frames_batch/ grid_frames/ 各csv/json)')
    _a, _ = _p.parse_known_args()
    return _a.base

BASE = _resolve_base()
GRID_DIR = os.path.join(BASE, 'grid_frames')
OUT_HTML = os.path.join(BASE, 'xincheng_dynamic_analysis_report.html')

# ---- 加载程序化分析结果 ----
with open(os.path.join(BASE, 'dynamic_analysis.json'), 'r', encoding='utf-8') as f:
    prog_data = json.load(f)
prog_map = {r['material_id']: r for r in prog_data}

# ---- 加载通顺文案(规范版，来自修正后的CSV) ----
copy_map, hook_map, vtype_map, cert_map = {}, {}, {}, {}
with open(os.path.join(BASE, 'videos_multimodal_fixed.csv'), 'r', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        mid = row['素材ID']
        copy_map[mid] = row.get('通顺文案', '')
        hook_map[mid] = row.get('钩子类型', '')
        vtype_map[mid] = row.get('视频类型', '')
        cert_map[mid] = row.get('证书类别', '')

# ---- 视觉分类(来自多模态逐段验证) ----
# ⚠️ 按账户替换：这是用 Read 工具逐段读 segments/ 图后人工填写的 L2 标注。
#    换项目时把素材ID换成你自己的，并填写对应的视觉格式/叙事拆解。
#    未列出的素材会回退为空(报告仍可生成，只是缺视觉分类)。
VISUAL_CLASSIFICATION = {
    '40632415704': {'format':'户外真人+证书展示','desc':'白毛衣女讲师户外手持红色证书，全程手势丰富自然光','scenes':['开场：证书展示+含金量铺垫','降门槛：不限制专业/越早越好','利益点：选择题满分100分/60分及格','CTA：五险一金+后台联系'],'color_tone':'暖色调/自然光','presenter_style':'活泼亲切/手势频繁','key_visual':'红证书是核心视觉锚点'},
    '41754594941': {'format':'户外真人+证书展示（同款变体）','desc':'与40632415704同一拍摄风格，户外真人持证','scenes':['开场钩子','利益推进','CTA收尾'],'color_tone':'暖色调/自然光','presenter_style':'亲切自然','key_visual':'证书展示建立信任'},
    '41379732140': {'format':'纯图文信息卡','desc':'绿色草地蒲公英背景+全屏文字信息卡片，无真人出镜','scenes':['信息密度极高的文字卡片轮播','证书名称+报考条件+福利待遇一次性呈现'],'color_tone':'绿色清新/信息密集','presenter_style':'无真人/纯图文','key_visual':'结构化信息排版是核心','special_note':'仅7.1秒超短！CVR王5.24%——信息直投效率最高'},
    '42117789987': {'format':'纯图文信息卡（米黄版）','desc':'米黄底色+结构化文字卡片，与41379732140同类但配色不同','scenes':['健康管理师证书核心信息展示'],'color_tone':'米黄温暖/低饱和度','presenter_style':'无真人/纯图文','key_visual':'极简信息卡，运动幅度接近0（几乎静态）'},
    '39158668835': {'format':'白底口播+动态大字报','desc':'白底单机位女讲师+全屏动态字幕/大字报切换','scenes':['0-5s：FOMO钩子(AI证书+限定名额)','5-11s：降门槛(28岁以下/零基础/60分过)','11-17s：信任状(2025最后机会✓)','17-22s：CTA(直播间入口)'],'color_tone':'干净白底+彩色大字(红黄绿)','presenter_style':'稳定口播+前段手势强调','key_visual':'大字报颜色策略：红=权威/黄=FOMO/绿=确认','special_note':'CTR王候选(3.25%)——钩子吸引力强但CVR偏低(1.74%)'},
    '39150194052': {'format':'科技风开场→白底口播','desc':'深蓝电路板背景"AI时代"开场(~2秒)→切到白底女讲师持证书','scenes':['0-2s：科技风暗场钩子(电路板+AI时代)','2s+: 切到白底口播模式'],'color_tone':'暗场科技蓝→亮场白底双色系','presenter_style':'开场震撼→转温和讲解','key_visual':'暗场开场制造差异化注意力捕获','special_note':'绝对CTR王(6%)但CVR仅0.43%——钩子太吸引非目标人群'},
    '38962770012': {'format':'白底口播+字卡（AI工程师标准款）','desc':'经典白底口播+动态字卡，与39158668835同模板','scenes':['FOMO钩子→降门槛→CTA'],'color_tone':'白底+彩色字卡','presenter_style':'稳定口播','key_visual':'标准白底字卡模板'},
    '38986614588': {'format':'白底口播+字卡','desc':'白底口播+字卡格式','scenes':['口播推进+字卡辅助'],'color_tone':'白底','presenter_style':'口播为主'},
    '39158727095': {'format':'白底口播+字卡','desc':'白底口播格式','color_tone':'白底'},
    '39158778319': {'format':'白底口播+字卡','desc':'白底口播长视频(25s)','color_tone':'白底'},
    '39158811093': {'format':'白底口播','desc':'白底口播格式','color_tone':'白底'},
    '39290259529': {'format':'快剪/高动态','desc':'高运动幅度，快速节奏','color_tone':'多变'},
    '39290378461': {'format':'白底+多场景','desc':'白底基础上有多处切镜','color_tone':'白底为主'},
    '40458376438': {'format':'白底口播','desc':'白底口播格式','color_tone':'白底'},
    '39773921823': {'format':'白底口播','desc':'白底口播格式','color_tone':'白底'},
    '39774043280': {'format':'高动态快剪','desc':'快节奏剪辑风格','color_tone':'动态'},
    '40457882068': {'format':'多场景混剪','desc':'室内讲师→户外证书持有者→手机特写CTA，至少3个独立场景硬切','scenes':['seg1: 室内白顶讲师"健康管理师"','seg2: 室内讲师手势强调','seg3: 切！户外白毛衣女"9零后首选正薪就业"+红证书','seg4: 户外继续+证书展示','seg5: 切！手机屏幕特写"每天刷刷玩手机"','seg6: 手机特写CTA'],'color_tone':'室内冷调→户外暖光→手机近景 三段式','presenter_style':'多角色切换+场景跳切','key_visual':'场景硬切制造视觉新鲜感+手机特写做CTA','special_note':'运动幅度17.6——场景切换带来高动态'},
    '39314358212': {'format':'场景对比混剪','desc':'证书展示场景→电脑桌面场景（"不能考证/零基础也能考"），用场景切换回应疑虑','scenes':['seg1-2: 女士持AI证书讲解','seg3-4: 证书特写','seg5: 硬切！电脑桌面"不能考证"','seg6: 桌面"零基础也能考"'],'color_tone':'明亮→办公桌面冷调','key_visual':'场景切换=疑虑回应的叙事手法','special_note':'运动幅度最高(24.2)+CVR高达4.71%——场景切换有效促进转化'},
    '37818264151': {'format':'居家/办公场景口播','desc':'现代家居/办公室环境（落地窗）+女讲师，比纯白底更生活化','scenes':['开场：健康管理师','推进：含金量+手机习惯钩子'],'color_tone':'自然光/生活化暖调','presenter_style':'轻松自然/不像演播室','key_visual':'真实生活场景降低距离感'},
}

# ---- 排序 + 统计 ----
prog_sorted = sorted(prog_data, key=lambda x: x.get('cost', 0), reverse=True)
fmt_counts = {}
for r in prog_sorted:
    vc = VISUAL_CLASSIFICATION.get(r['material_id'], {})
    fmt = vc.get('format', r['style_summary'] or '未分类')
    fmt_counts[fmt] = fmt_counts.get(fmt, 0) + 1
tc = sum(r.get('cost', 0) for r in prog_sorted)
ac = sum(1 for r in prog_sorted if cert_map.get(r['material_id']) == 'AI应用工程师' or r.get('cert_type') == 'AI应用工程师')
hc = len(prog_sorted) - ac

def esc(s):
    return htmlescape.escape(str(s)).replace('\n', '<br>')

def b64img(path):
    if os.path.exists(path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read()).decode()
    return ''

def fmt_tag_cls(fmt):
    if '户外' in fmt: return 'fmt-outdoor'
    if '图文' in fmt: return 'fmt-textcard'
    if '白底' in fmt: return 'fmt-white'
    if '多场景' in fmt or '混剪' in fmt: return 'fmt-multi'
    return 'fmt-tech'

cards_html = ''
for i, r in enumerate(prog_sorted):
    mid = r['material_id']
    vc = VISUAL_CLASSIFICATION.get(mid, {})
    fmt = vc.get('format', r['style_summary'] or '未分类')

    grid_b64 = b64img(os.path.join(GRID_DIR, f'{mid}.png'))

    cost = r.get('cost', 0)
    ctr = r.get('ctr', 0)
    cvr = r.get('cvr', 0)
    clicks = r.get('clicks', 0)
    conv = r.get('conv', 0)
    dur = r.get('duration_s', 0)
    motion = r.get('avg_motion', 0)
    tcount = r.get('transition_count', 0)
    single_shot = r.get('is_single_shot', True)
    tags = r.get('style_tags', [])
    brightness = r.get('avg_brightness', 0)

    cert = cert_map.get(mid) or r.get('cert_type', '')
    copy = copy_map.get(mid) or r.get('copy', '')
    hook = hook_map.get(mid) or r.get('hook', '')
    vtype = vtype_map.get(mid) or r.get('vtype', '')

    # 动态特征芯片
    shot_txt = '单镜头' if single_shot else '多场景'
    if motion < 5: motion_txt = '静'
    elif motion < 18: motion_txt = '中'
    else: motion_txt = '动'

    # 视觉分类
    vis_desc = vc.get('desc', '')
    scenes = vc.get('scenes', [])
    color_tone = vc.get('color_tone', '')
    key_vis = vc.get('key_visual', '')
    special = vc.get('special_note', '')

    fmt_cls = fmt_tag_cls(fmt)
    cert_cls = 'bai' if cert == 'AI应用工程师' else 'bh'

    # CTR/CVR 高亮
    ctr_cls = ' class="gn"' if ctr >= 1 else ''
    cvr_cls = ' class="gn"' if cvr >= 1 else ''

    # 文案块（之前遗漏的字段，现在补回）
    copy_html = ''
    if copy:
        copy_html = f'<div class="copy"><span class="copy-lbl">📝 通顺文案（多模态拆解）</span><div class="copy-txt">{esc(copy)}</div></div>'

    # 时序拆解
    scenes_html = ''
    if scenes:
        li = ''.join(f'<li>{esc(s)}</li>' for s in scenes)
        scenes_html = f'<div class="vs"><b>时序拆解：</b><ul>{li}</ul></div>'

    special_html = f'<div class="sp">{esc(special)}</div>' if special else ''
    tags_html = ''.join(f'<span class="tg">{esc(t)}</span>' for t in tags)

    meta_line = ''
    if hook or vtype:
        meta_line = f'<div class="meta">钩子：{esc(hook or "—")} ｜ 视频类型：{esc(vtype or "—")}</div>'

    cards_html += f'''
<div class="card">
  <div class="ch">
    <span class="id">#{i+1}·{mid}</span>
    <span class="{fmt_cls}">{esc(fmt)}</span>
    <span class="b {cert_cls}">{esc(cert)}</span>
  </div>
  <div class="ci"><img src="data:image/png;base64,{grid_b64}" alt="{mid}"></div>
  <div class="cb">
    <div class="ms">
      <div class="m"><div class="v">¥{int(cost):,}</div><div class="k">花费</div></div>
      <div class="m"><div class="v"{ctr_cls}>{ctr:.2f}%</div><div class="k">CTR</div></div>
      <div class="m"><div class="v"{cvr_cls}>{cvr:.2f}%</div><div class="k">CVR</div></div>
      <div class="m"><div class="v">{clicks:,}</div><div class="k">点击</div></div>
      <div class="m"><div class="v">{conv}</div><div class="k">转化</div></div>
    </div>
    {copy_html}
    <div class="dyn">
      <span>⏱ {dur}s</span>
      <span>🎬 转场 {tcount}（{shot_txt}）</span>
      <span>🏃 运动 {motion:.1f}（{motion_txt}）</span>
      <span>💡 亮度 {brightness:.0%}</span>
    </div>
    {meta_line}
    {f'<div class="vd"><b>视觉描述：</b>{esc(vis_desc)}</div>' if vis_desc else ''}
    {f'<div class="vt"><b>色彩基调：</b>{esc(color_tone)}</div>' if color_tone else ''}
    {f'<div class="vt"><b>核心视觉：</b>{esc(key_vis)}</div>' if key_vis else ''}
    {scenes_html}
    {special_html}
    <div class="tags">{tags_html}</div>
  </div>
</div>'''

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
fmt_rows = '\n'.join(
    f'<tr><td>{esc(k)}</td><td>{v}</td></tr>' for k, v in sorted(fmt_counts.items(), key=lambda x: -x[1])
)

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>新程教育 · 动态视频深度分析报告</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f8f9fc;color:#1e293b;padding:20px;max-width:1600px;margin:auto}}
.header{{margin-bottom:24px}}.header h1{{font-size:22px;font-weight:700}}.header p{{color:#64748b;font-size:14px;margin-top:4px}}
.stats{{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:24px}}
.sc{{background:#fff;border:1px solid #e2e6f0;border-radius:10px;padding:16px 20px;min-width:140px}}.sc .n{{font-size:28px;font-weight:700}}.sc .l{{font-size:12px;color:#64748b;margin-top:2px}}
.fmt-table{{background:#fff;border:1px solid #e2e6f0;border-radius:10px;padding:16px;margin-bottom:24px}}.fmt-table h3{{font-size:15px;margin-bottom:8px}}
.fmt-table table{{width:100%;border-collapse:collapse;font-size:13px}}.fmt-table th,.fmt-table td{{padding:6px 12px;text-align:left;border-bottom:1px solid #f1f5f9}}.fmt-table th{{background:#f8fafc;font-weight:600}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(720px,1fr));gap:18px;align-items:start}}
.card{{background:#fff;border:1px solid #e2e6f0;border-radius:12px;overflow:hidden}}
.ch{{padding:12px 16px;border-bottom:1px solid #e2e6f0;display:flex;align-items:center;flex-wrap:wrap;gap:6px}}.ch .id{{font-size:13px;font-weight:600;color:#64748b}}
.b{{font-size:11px;padding:3px 10px;border-radius:20px;font-weight:500}}
.bai{{background:#ede9fe;color:#4f46e5}}.bh{{background:#ecfdf5;color:#059669}}
.tag{{font-size:11px;padding:3px 10px;border-radius:20px;font-weight:600}}
.fmt-outdoor{{background:#fef3c7;color:#b45309}}.fmt-textcard{{background:#d1fae5;color:#065f46}}.fmt-white{{background:#ede9fe;color:#5b21b6}}.fmt-multi{{background:#fce7f3;color:#be185d}}.fmt-tech{{background:#dbeafe;color:#1e40af}}
.ci img{{width:100%;height:auto;display:block;max-height:320px;object-fit:contain;background:#000}}
.cb{{padding:14px 16px}}
.ms{{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;margin-bottom:10px}}
.m{{text-align:center;padding:8px 4px;background:#f8fafc;border-radius:6px}}.m .v{{font-size:15px;font-weight:700}}.m .k{{font-size:11px;color:#64748b;margin-top:2px}}
.copy{{margin:10px 0;padding:10px 14px;background:#fafbff;border:1px solid #e0e7ff;border-left:4px solid #4f46e5;border-radius:8px}}
.copy-lbl{{display:block;font-size:11px;color:#4f46e5;font-weight:600;margin-bottom:4px}}
.copy-txt{{font-size:14px;line-height:1.75;color:#1e293b}}
.dyn{{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0;padding:8px 12px;background:#f8fafc;border-radius:6px;font-size:12px;color:#475569}}
.dyn span{{padding:3px 8px;background:#fff;border:1px solid #e2e6f0;border-radius:4px;white-space:nowrap}}
.meta{{font-size:12px;color:#64748b;margin:6px 0}}
.vd{{font-size:13.5px;line-height:1.7;color:#334155;margin:8px 0;padding:8px 12px;background:#eff6ff;border-left:3px solid #2563eb;border-radius:4px}}
.vt{{font-size:12.5px;color:#64748b;margin:4px 0}}
.vs{{font-size:13px;margin:8px 0;padding:8px 12px;background:#fefce8;border-left:3px solid #eab308;border-radius:4px}}.vs ul{{margin-top:4px;padding-left:18px}}.vs li{{margin:3px 0;font-size:12.5px;line-height:1.5}}
.sp{{font-size:12.5px;color:#dc2626;margin:6px 0;padding:6px 10px;background:#fef2f2;border-radius:4px;font-weight:500}}
.tags{{display:flex;flex-wrap:wrap;gap:4px;margin-top:8px}}.tg{{font-size:11px;padding:2px 8px;background:#f1f5f9;color:#475569;border-radius:4px}}
.gn{{color:#16a34a}}
.ft{{text-align:center;color:#64748b;font-size:12px;margin:32px auto;line-height:1.7}}
.note{{background:#fff;border:1px solid #e2e6f0;border-radius:10px;padding:14px 16px;margin-bottom:24px;font-size:13px;color:#475569;line-height:1.7}}
.note b{{color:#1e293b}}
</style></head>
<body>
<div class="header"><h1>🎬 新程教育 · 动态视频深度分析报告</h1>
<p>Top{len(prog_sorted)} 视频 · 时序分段动态分析 · opencv转场/运动/色彩 · 多模态视觉验证 · 妙问API真实消耗 · 多模态通顺文案</p></div>

<div class="stats">
<div class="sc"><div class="n">{len(prog_sorted)}</div><div class="l">分析素材数</div></div>
<div class="sc"><div class="n" style="color:#d97706">¥{int(tc):,}</div><div class="l">合计花费</div></div>
<div class="sc"><div class="n" style="color:#4f46e5">{ac}</div><div class="l">AI应用工程师</div></div>
<div class="sc"><div class="n" style="color:#059669">{hc}</div><div class="l">健康管理师</div></div>
<div class="sc"><div class="n">{len(fmt_counts)}</div><div class="l">视觉格式类型</div></div>
</div>

<div class="note">📌 <b>数据协同说明：</b>本报告整合了四层数据 —— ① <b>程序化动态特征</b>（OpenCV 对 mp4 做转场检测/运动幅度/色彩分析）；② <b>视觉分类</b>（多模态逐段读图验证）；③ <b>真实消耗</b>（妙问API 拉取的CTR/CVR/花费）；④ <b>通顺文案</b>（多模态拆解口播稿，<b>与「多模态文案拆解报告」同源</b>，此处一并呈现，避免两步脱节）。</div>

<div class="fmt-table"><h3>📊 视觉格式分布</h3><table><tr><th>格式</th><th>数量</th></tr>{fmt_rows}</table></div>

<div class="grid">{cards_html}</div>

<div class="ft">生成时间：{now}<br>
分析链路：妙问API拉取素材 → 本地下载mp4 → opencv抽帧(每秒1帧) → 帧间直方图差分检测转场 → 运动幅度 → 色彩风格 → 多模态逐段视觉验证 + 文案拆解<br>
技术栈：Python + OpenCV 5.0 + numpy ｜ 纯静态报告 · 零JavaScript</div>
</body></html>'''

with open(OUT_HTML, 'w', encoding='utf-8') as f:
    f.write(html)

sz_mb = os.path.getsize(OUT_HTML) / 1024 / 1024
print(f'Done! {OUT_HTML}')
print(f'Size: {sz_mb:.1f}MB | Cards: {len(prog_sorted)}')
print(f'Total cost: ¥{int(tc):,} | AI:{ac} Health:{hc}')
print(f'Formats: {json.dumps(fmt_counts, ensure_ascii=False)}')
print(f'Copy included: {sum(1 for r in prog_sorted if copy_map.get(r["material_id"]))}/{len(prog_sorted)}')
