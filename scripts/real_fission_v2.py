#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
爆款素材拆解裂变器 · 真实数据版裂变 v2（制片级）
整合：通顺文案(videos_multimodal_fixed.csv) + 真实消耗(dynamic_analysis.json) + 动态视觉格式洞察
每个裂变变体 = 已验证高效视觉格式 + 镜头脚本 + 口播文案 + 钩子 + 测试假设 + 母本来源
纯静态HTML，零JS
注：本脚本内置的 V 裂变变体表与 FMT 格式映射为「脱敏示例」，素材ID已匿名(EDU-V0x)，
不含任何具体客户名称与具体投放数值，仅用于演示「格式→镜头→文案→假设」的裂变方法论。
"""
import json, csv, os, html as htmlescape
from collections import defaultdict
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
OUT = os.path.join(BASE, 'demo_real_fission_v2_report.html')

# ---------- 1. 真实数据：格式级聚合 ----------
with open(os.path.join(BASE, 'dynamic_analysis.json'), encoding='utf-8') as f:
    prog = json.load(f)
with open(os.path.join(BASE, 'videos_multimodal_fixed.csv'), encoding='utf-8-sig') as f:
    copy_map = {r['素材ID']: r for r in csv.DictReader(f)}

# ⚠️ 按账户替换：把你的素材ID映射到「视觉格式」分类（来自动态分析模块的输出）。
#    未列出的素材会回退到 dynamic_analysis.json 里的 style_summary 字段，不会报错。
#    这是账户专属配置，发布/换项目时必须改成你自己的映射。
FMT = {
    'EDU-V01':'户外真人+证书展示','EDU-V02':'户外真人+证书展示',
    'EDU-V03':'纯图文信息卡','EDU-V04':'纯图文信息卡',
    'EDU-V05':'白底口播+动态大字报','EDU-V06':'科技风开场→白底口播',
    'EDU-V07':'白底口播+字卡','EDU-V08':'白底口播+字卡',
    'EDU-V09':'白底口播+字卡','EDU-V10':'白底口播+字卡',
    'EDU-V11':'白底口播','EDU-V12':'快剪/高动态','EDU-V13':'白底+多场景',
    'EDU-V14':'白底口播','EDU-V15':'白底口播','EDU-V16':'高动态快剪',
    'EDU-V17':'多场景混剪','EDU-V18':'场景对比混剪','EDU-V19':'居家/办公场景口播',
}
agg = defaultdict(lambda: {'cost':0.0,'conv':0,'ctr':[],'cvr':[],'n':0,'certs':defaultdict(int)})
for r in prog:
    f_ = FMT.get(r['material_id'], r['style_summary'])
    a = agg[f_]; a['cost'] += r['cost']; a['conv'] += r['conv']
    a['ctr'].append(r['ctr']); a['cvr'].append(r['cvr']); a['n'] += 1
    cert = copy_map.get(r['material_id'], {}).get('证书类别','')
    if cert: a['certs'][cert] += 1

fmt_stats = []
for f_, a in agg.items():
    # 单转化成本 CPA = 花费/转化（越低越高效，真正的ROI口径）
    cpa = (a['cost'] / a['conv']) if a['conv'] else 0
    fmt_stats.append({
        'fmt': f_, 'n': a['n'], 'cost': a['cost'], 'conv': a['conv'],
        'avg_cvr': sum(a['cvr'])/len(a['cvr']), 'avg_ctr': sum(a['ctr'])/len(a['ctr']),
        'cpa': cpa, 'certs': dict(a['certs'])
    })
fmt_stats.sort(key=lambda x: x['cpa'])  # CPA升序（低成本优先）

# ---------- 2. 裂变变体库（制片级，绑格式+镜头+文案+假设） ----------
V = [
 # ===== Family A 纯图文信息卡（CVR王格式，优先扩量） =====
 dict(id='A1', pri='P0', cert='健康管理师', fmt='纯图文信息卡', mother='EDU-V03（高CVR母本）',
      hook='时间窗口+低门槛',
      shots=['绿底主卡：健康管理师证书+「未来5年吃香」','报考条件卡：不限专业·不限经验·选择题',
             '福利卡：五险一金+工作稳定','CTA卡：直播间入口按钮'],
      copy='健康管理师证书——未来5年可能越来越吃香，但要在26年考下。题目难度小、就业机会大；不限专业、不限经验；题目都是选择题，满分100分60分合格。想了解更多详情来我直播间。',
      hyp='复用高CVR格式+利益清单结构，验证「绿底vs米黄底」配色是否影响转化'),
 dict(id='A2', pri='P0', cert='AI应用工程师', fmt='纯图文信息卡', mother='EDU-V04 (米黄版)',
      hook='时间窗口+低门槛',
      shots=['米黄底主卡：AI应用工程师证书+「26年窗口」','报考条件卡：零基础·18岁以上·不编程',
             '福利卡：远远甩开同龄人','CTA卡：直播间入口按钮'],
      copy='AI应用工程师证书——现在知道的人很少，但未来很吃香。要在26年考下，零基础、18岁以上就能报，不用会编程。满分100分60分就及格。想了解更多来我直播间。',
      hyp='把已验证的「纯图文信息卡」格式迁移到AI工程师品类，验证品类×格式交叉是否同样高效'),
 dict(id='A3', pri='P1', cert='健康管理师', fmt='纯图文信息卡', mother='EDU-V03',
      hook='稀缺+社会认同',
      shots=['双证对比卡：健康管理师 vs 公共营养师（并排）','差异卡：哪个更吃香/更好就业',
             '报考卡：同条件·选择题·60分','CTA卡：直播间'],
      copy='同样是含金量证书，健康管理师和公共营养师哪个更吃香？现在考健康管理师，不限专业、不限经验，选择题满分100分60分合格，就业机会更大。来我直播间对比看看。',
      hyp='双证对比制造决策张力，测试是否比单证信息卡提升点击与转化'),

 # ===== Family B 户外真人+证书展示（信任王，扩量） =====
 dict(id='B1', pri='P0', cert='健康管理师', fmt='户外真人+证书展示', mother='EDU-V01（高花费/高转化母本）',
      hook='权威背书+含金量',
      shots=['户外自然光，女讲师手持红色证书入镜','手势强调：「今年含金量比较高」',
             '降门槛：「不限制专业，越早越好」','利益：「选择题60分及格，待遇好」','CTA：后台联系'],
      copy='健康管理师——今年含金量比较高。每天有时间玩手机？不如考个健康管理师。每天学习一下，选择题，60分及格拿证。待遇好。',
      hyp='1:1复刻高转化母本结构，测试不同讲师/户外场景是否影响信任度'),
 dict(id='B2', pri='P0', cert='AI应用工程师', fmt='户外真人+证书展示', mother='EDU-V01(结构迁移)',
      hook='趋势驱动+消除门槛',
      shots=['户外女讲师手持AI应用工程师红证书','强调：「不用会编程、零基础」',
             '利益：「26年拿下远远甩开别人」','CTA：直播间'],
      copy='AI应用工程师证书——现在知道的人很少，但未来很吃香。它不需要你会编程，零基础就能上手，18岁以上就能报。26年拿下，远远甩开别人。还是想考？',
      hyp='把健康管理的「户外持证信任结构」迁移到AI工程师，验证信任结构是否跨品类有效'),
 dict(id='B3', pri='P1', cert='健康管理师', fmt='户外真人+证书展示', mother='EDU-V01',
      hook='痛点切入+简单直接',
      shots=['户外持证：「每天有时间玩手机？」','切证书特写：「题目简单」',
             '利益字幕：「工作稳定·五险一金」','CTA：来考一个'],
      copy='健康管理师——每天有时间玩手机？题目简单，满分100分，工作稳定，感兴趣的来考一个。',
      hyp='缩短时长至10s内、砍掉铺垫，测试极简版是否提升完播与转化'),

 # ===== Family C 多场景混剪（动态，测试扩量） =====
 dict(id='C1', pri='P1', cert='健康管理师', fmt='多场景混剪', mother='EDU-V17',
      hook='行为中断+利益清单',
      shots=['室内白顶讲师：「健康管理师今年有含金量」','硬切户外白毛衣女+红证书：「9零后首选正薪就业」',
             '硬切手机屏幕特写：「每天刷刷玩手机」','CTA：手机特写+直播间'],
      copy='健康管理师——今年有含金量的职业。每天有时间玩手机？每天手机学一下。题目简单，满分100分，工作状态安稳，享受五险一金。',
      hyp='验证「室内→户外→手机」三段硬切是否比单机位提升完播与转化'),
 dict(id='C2', pri='P1', cert='AI应用工程师', fmt='场景对比混剪', mother='EDU-V18（高CVR母本）',
      hook='消除门槛+硬利益',
      shots=['女士持AI证书讲解','证书特写','硬切电脑桌面：「不能考证？」','桌面：「零基础也能考」',
             '福利字幕：「周末双休·五险一金」','CTA：直播间'],
      copy='AI应用工程师证书——不限专业，零基础也能学。今年的题目简单，满分100分。周末双休、五险一金！来直播间看看吧。',
      hyp='复用场景切换「疑虑回应」手法，验证对AI工程师品类同样有效'),

 # ===== Family D 白底口播+动态大字报（走量，CTR王家族） =====
 dict(id='D1', pri='P1', cert='AI应用工程师', fmt='白底口播+动态大字报', mother='EDU-V05（高CTR母本）',
      hook='稀缺性+FOMO',
      shots=['白底单机位女讲师','大字报红：「AI应用工程师证书」','黄字：「限定名额很少·但还来得及」',
             '白字：「28岁以下/零基础/60分过」','绿勾：「2025最后机会✓」','CTA：直播间入口'],
      copy='AI应用工程师证书——现在知道的人很少，但未来很吃香。只要你在26年拿下，就能远远甩开别人。满分100分，60分就可以及格拿证。还是想考？',
      hyp='保留高CTR钩子结构，测试「直播间CTA前置」是否补CVR短板'),
 dict(id='D2', pri='P1', cert='健康管理师', fmt='白底口播+字卡', mother='EDU-V17(结构)',
      hook='行为中断+利益清单',
      shots=['白底讲师：「每天有时间玩手机？」','字卡：「不如考健康管理师」',
             '字卡：「选择题·60分及格·待遇好」','CTA：后台'],
      copy='健康管理师——每天有时间玩手机？不如考个健康管理师。每天学习一下，选择题，60分及格拿证。待遇好。',
      hyp='白底低成本版替代户外拍摄，测试成本下降后ROI是否更优'),
 dict(id='D3', pri='P2', cert='AI应用工程师', fmt='白底口播+字卡', mother='EDU-V05(变体)',
      hook='稀缺+社会认同',
      shots=['白底讲师','字卡：「现在知道的人少·未来吃香」','字卡：「26年拿下远超身边人」',
             '字卡：「满分100·60分拿证」','CTA：直播间'],
      copy='有空就去考这个证——现在知道的人少，但是未来很吃香。只要你在26年拿下，就远超身边人。专业和经验都不限，满分100分，60分就可以拿证。',
      hyp='用男声/不同讲师做A/B，测试主播性别对AI品类CVR的影响'),

 # ===== Family E 科技风开场（仅认知层，标注CVR弱） =====
 dict(id='E1', pri='P2', cert='AI应用工程师', fmt='科技风开场→白底口播', mother='EDU-V06（高CTR母本）',
      hook='趋势驱动+消除门槛',
      shots=['暗场电路板2s：「AI时代」','硬切白底讲师持证书','大字报：「不编程·零基础·18岁可报」',
             'CTA：直播间'],
      copy='AI时代——一定要考的证来了！AI应用工程师认证证书：它不需要你会编程，也不需要技术背景，零基础就能上手，关键18岁以上就能报名。报名成功之后即可参加考试，满分100分，60分及格拿证。来我直播间了解详情。',
      hyp='【仅用于曝光/认知层】高CTR但CVR偏低，不作为转化素材，测试暗场开场对低频人群的吸引力'),
]

# ---------- 3. 渲染 ----------
def esc(s): return htmlescape.escape(str(s)).replace('\n','<br>')
def pri_cls(p): return {'P0':'p0','P1':'p1','P2':'p2'}.get(p,'p2')
def fmt_cls(f):
    if '户外' in f: return 'fmt-outdoor'
    if '图文' in f: return 'fmt-textcard'
    if '白底' in f: return 'fmt-white'
    if '多场景' in f or '混剪' in f: return 'fmt-multi'
    return 'fmt-tech'

def fmt_rows():
    rows = ''
    for s in fmt_stats:
        top = ' class="gn"' if s['avg_cvr'] >= 3 else ''
        rows += f'<tr><td>{esc(s["fmt"])}</td><td>{s["n"]}</td><td>¥{int(s["cost"]):,}</td><td>{s["conv"]}</td><td{top}>{s["avg_cvr"]:.2f}%</td><td>¥{s["cpa"]:.0f}</td></tr>'
    return rows

cards = ''
for v in V:
    shots = ''.join(f'<li>{esc(x)}</li>' for x in v['shots'])
    cards += f'''
<div class="card">
  <div class="ch">
    <span class="vid">{esc(v['id'])}</span>
    <span class="pri {pri_cls(v['pri'])}">{esc(v['pri'])}</span>
    <span class="cert {('bai' if v['cert']=='AI应用工程师' else 'bh')}">{esc(v['cert'])}</span>
    <span class="fmt {fmt_cls(v['fmt'])}">{esc(v['fmt'])}</span>
  </div>
  <div class="body">
    <div class="row"><span class="k">母本来源</span><span class="val">{esc(v['mother'])}</span></div>
    <div class="row"><span class="k">钩子类型</span><span class="val">{esc(v['hook'])}</span></div>
    <div class="copy"><span class="lbl">📝 口播/字幕文案</span><div class="txt">{esc(v['copy'])}</div></div>
    <div class="shots"><b>🎬 镜头脚本（制片指令）</b><ul>{shots}</ul></div>
    <div class="hyp"><b>🧪 测试假设</b>{esc(v['hyp'])}</div>
  </div>
</div>'''

now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
p0 = sum(1 for v in V if v['pri']=='P0'); p1 = sum(1 for v in V if v['pri']=='P1'); p2 = sum(1 for v in V if v['pri']=='P2')

html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head><meta charset="UTF-8"><title>某教育行业客户 · 真实数据版裂变 v2（制片级）</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#f8f9fc;color:#1e293b;padding:20px;max-width:1500px;margin:auto}}
.header{{margin-bottom:20px}}.header h1{{font-size:22px;font-weight:700}}.header p{{color:#64748b;font-size:13.5px;margin-top:4px}}
.stats{{display:flex;gap:14px;flex-wrap:wrap;margin-bottom:20px}}
.sc{{background:#fff;border:1px solid #e2e6f0;border-radius:10px;padding:14px 18px;min-width:120px}}.sc .n{{font-size:24px;font-weight:700}}.sc .l{{font-size:12px;color:#64748b;margin-top:2px}}
.panel{{background:#fff;border:1px solid #e2e6f0;border-radius:10px;padding:16px;margin-bottom:20px}}
.panel h3{{font-size:15px;margin-bottom:10px}}
table{{width:100%;border-collapse:collapse;font-size:13px}}th,td{{padding:7px 10px;text-align:left;border-bottom:1px solid #f1f5f9}}th{{background:#f8fafc;font-weight:600}}
.gn{{color:#16a34a;font-weight:700}}
.legend{{font-size:12px;color:#64748b;margin-top:8px;line-height:1.6}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(680px,1fr));gap:16px;align-items:start}}
.card{{background:#fff;border:1px solid #e2e6f0;border-radius:12px;overflow:hidden}}
.ch{{padding:10px 14px;border-bottom:1px solid #e2e6f0;display:flex;align-items:center;flex-wrap:wrap;gap:6px}}
.vid{{font-size:15px;font-weight:700;color:#1e293b}}
.pri{{font-size:11px;padding:2px 9px;border-radius:20px;font-weight:700;color:#fff}}
.p0{{background:#dc2626}}.p1{{background:#ea580c}}.p2{{background:#64748b}}
.cert{{font-size:11px;padding:3px 9px;border-radius:20px;font-weight:500}}.bai{{background:#ede9fe;color:#4f46e5}}.bh{{background:#ecfdf5;color:#059669}}
.fmt{{font-size:11px;padding:3px 9px;border-radius:20px;font-weight:600}}
.fmt-outdoor{{background:#fef3c7;color:#b45309}}.fmt-textcard{{background:#d1fae5;color:#065f46}}.fmt-white{{background:#ede9fe;color:#5b21b6}}.fmt-multi{{background:#fce7f3;color:#be185d}}.fmt-tech{{background:#dbeafe;color:#1e40af}}
.body{{padding:12px 14px}}
.row{{display:flex;gap:10px;font-size:13px;margin:4px 0}}.row .k{{color:#64748b;min-width:64px;flex-shrink:0}}.row .val{{color:#334155;font-weight:500}}
.copy{{margin:10px 0;padding:10px 14px;background:#fafbff;border:1px solid #e0e7ff;border-left:4px solid #4f46e5;border-radius:8px}}
.copy .lbl{{display:block;font-size:11px;color:#4f46e5;font-weight:600;margin-bottom:4px}}
.copy .txt{{font-size:14px;line-height:1.75;color:#1e293b}}
.shots{{margin:10px 0;padding:10px 14px;background:#f0fdf4;border-left:4px solid #16a34a;border-radius:8px;font-size:13px}}
.shots ul{{margin-top:6px;padding-left:18px}}.shots li{{margin:3px 0;line-height:1.5}}
.hyp{{margin-top:8px;padding:8px 12px;background:#fffbeb;border-left:4px solid #eab308;border-radius:8px;font-size:12.5px;color:#92400e;line-height:1.6}}
.ft{{text-align:center;color:#64748b;font-size:12px;margin:28px auto;line-height:1.7}}
</style></head>
<body>
<div class="header"><h1>🧬 某教育行业客户 · 真实数据版裂变 v2（制片级）</h1>
<p>整合：通顺文案(多模态) + 真实消耗(妙问API) + 动态视觉格式洞察(OpenCV) ｜ {len(V)} 个裂变变体 · 每个绑定已验证高效格式 + 镜头脚本 + 测试假设</p></div>

<div class="stats">
<div class="sc"><div class="n">{len(V)}</div><div class="l">裂变变体</div></div>
<div class="sc"><div class="n" style="color:#dc2626">{p0}</div><div class="l">P0 紧急</div></div>
<div class="sc"><div class="n" style="color:#ea580c">{p1}</div><div class="l">P1 测试</div></div>
<div class="sc"><div class="n" style="color:#64748b">{p2}</div><div class="l">P2 探索</div></div>
<div class="sc"><div class="n" style="color:#059669">{len(fmt_stats)}</div><div class="l">视觉格式</div></div>
</div>

<div class="panel"><h3>📊 视觉格式效率排名（真实消耗驱动，裂变分配依据）</h3>
<table><tr><th>视觉格式</th><th>素材数</th><th>总花费</th><th>总转化</th><th>均CVR</th><th>单转化成本CPA</th></tr>
{fmt_rows()}
</table>
<div class="legend">💡 <b>双口径结论</b>：① <b>CPA（单转化成本，越低越好）</b>最低的是 <b>白底系列</b> 与 <b>多场景混剪</b>——制作便宜+流量划算，是走量主力；
② <b>CVR（转化率，越高越好）</b>最高的是 <b>纯图文信息卡</b> 与 <b>户外真人+证书展示</b>——信任/offer更强。<br>
<b>分配逻辑</b>：P0 押在「高CVR且当前素材量少、可降依赖」的 <b>纯图文信息卡</b> 与 <b>户外真人</b>（账户目前7成以上是白底口播，需多元化）；白底系列按CPA优势作P1走量；<b>科技风开场</b>(高CTR但低CVR) 仅作认知层(E1)。</div>
</div>

<div class="grid">{cards}</div>

<div class="ft">生成时间：{now}<br>
数据链路：妙问API拉素材 → 本地下载mp4 → OpenCV动态分析 → 多模态文案拆解 → 真实消耗归因 → 格式效率排名 → 制片级裂变<br>
技术栈：Python + OpenCV 5.0 ｜ 纯静态报告 · 零JavaScript</div>
</body></html>'''

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(html)
print(f'Done! {OUT}')
print(f'Size: {os.path.getsize(OUT)/1024/1024:.1f}MB | Variants: {len(V)} (P0:{p0} P1:{p1} P2:{p2})')
print(f'Formats ranked by CPA: ' + ' > '.join(f'{s["fmt"]}(¥{s["cpa"]:.0f})' for s in fmt_stats[:5]))
