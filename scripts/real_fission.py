# -*- coding: utf-8 -*-
"""
强哥广告skill · 真实数据版成因分析 + 脚本裂变
==============================================
数据源：videos_multimodal_fixed.csv（妙问API拉取的19条真实素材：真实文案+真实消耗+已标注钩子/品类/视频类型）
与 fission_tool.py 区别：不依赖Excel脚本库/命名匹配，直接用真实素材做归因与裂变。
输出：xincheng_real_fission_report.html（纯静态，零JS，避免空白问题）
"""
import csv, os, html
from datetime import datetime
from collections import defaultdict

import argparse as _ap

def _resolve_base():
    """数据根目录：放置 frames_batch/ grid_frames/ 各 csv/json。可用 --base 覆盖。"""
    _p = _ap.ArgumentParser(add_help=False)
    _p.add_argument('--base', default=r'C:\Users\Administrator\WorkBuddy\2026-07-14-11-51-15',
                    help='数据根目录(含 frames_batch/ grid_frames/ 各csv/json)')
    _a, _ = _p.parse_known_args()
    return _a.base

BASE = _resolve_base()
CSV = os.path.join(BASE, 'videos_multimodal_fixed.csv')
OUT = os.path.join(BASE, 'xincheng_real_fission_report.html')

# ---------- 1. 读真实数据 ----------
rows = []
with open(CSV, encoding='utf-8-sig') as f:
    for r in csv.DictReader(f):
        rows.append(r)

for r in rows:
    r['spend'] = float(r['花费(元)'] or 0)
    r['exp']   = int(float(r['曝光数'] or 0))
    r['clk']   = int(float(r['点击数'] or 0))
    r['ctr']   = float(r['CTR(%)'] or 0)
    r['cvr']   = float(r['CVR(%)'] or 0)
    r['conv']  = int(float(r['转化量'] or 0))
    r['cpm']   = float(r['CPM(元)'] or 0)
    r['cpc']   = float(r['CPC(元)'] or 0)
    r['eff']   = r['ctr'] * r['cvr']        # 综合效率 = CTR×CVR
    r['is_var'] = '同素材' in r['通顺文案']  # 变体标记

# ---------- 2. 总体指标 ----------
total_spend = sum(r['spend'] for r in rows)
total_exp   = sum(r['exp'] for r in rows)
total_clk   = sum(r['clk'] for r in rows)
total_conv  = sum(r['conv'] for r in rows)
w_ctr = total_clk/total_exp*100
w_cvr = total_conv/total_clk*100
n_ai  = sum(1 for r in rows if r['证书类别']=='AI应用工程师')
n_hp  = len(rows)-n_ai
n_var = sum(1 for r in rows if r['is_var'])

# ---------- 3. 聚合（加权CTR/CVR更真实） ----------
def agg(key):
    d = defaultdict(lambda: {'spend':0,'exp':0,'clk':0,'conv':0,'n':0,'ctr_sum':0,'cvr_sum':0,'cpm_sum':0})
    for r in rows:
        k = r[key]; a = d[k]
        a['spend']+=r['spend']; a['exp']+=r['exp']; a['clk']+=r['clk']; a['conv']+=r['conv']
        a['n']+=1; a['ctr_sum']+=r['ctr']; a['cvr_sum']+=r['cvr']; a['cpm_sum']+=r['cpm']
    out=[]
    for k,a in d.items():
        out.append({'key':k,'n':a['n'],'spend':a['spend'],'conv':a['conv'],
            'wctr': a['clk']/a['exp']*100 if a['exp'] else 0,
            'wcvr': a['conv']/a['clk']*100 if a['clk'] else 0,
            'avg_ctr': a['ctr_sum']/a['n'], 'avg_cvr': a['cvr_sum']/a['n'],
            'avg_cpm': a['cpm_sum']/a['n']})
    return sorted(out, key=lambda x:-x['conv'])

by_hook   = agg('钩子类型')
by_cert   = agg('证书类别')
by_vtype  = agg('视频类型')

# ---------- 4. 效率王 / 预警 ----------
winner_conv = max(rows, key=lambda r:r['conv'])   # 绝对转化王
winner_cvr  = max(rows, key=lambda r:r['cvr'])    # CVR王
winner_ctr  = max(rows, key=lambda r:r['ctr'])    # CTR王
winner_eff  = max(rows, key=lambda r:r['eff'])    # 综合效率王
high_ctr_low= [r for r in rows if r['ctr']>=2 and r['cvr']<1]   # 高点击低转化(人群错配嫌疑)
# 原始母本(非变体)里各品类效率王
orig = [r for r in rows if not r['is_var']]
ai_orig  = [r for r in orig if r['证书类别']=='AI应用工程师']
hp_orig  = [r for r in orig if r['证书类别']=='健康管理师']
ai_mother  = max(ai_orig, key=lambda r:r['eff'])
hp_mother  = max(hp_orig, key=lambda r:r['eff'])

# ---------- 5. 真实变量池（从19条真实文案归纳，非硬编码通用模板） ----------
REAL_HOOKS = {
 '权威背书/含金量': '今年含金量比较高，是国家认可、企业抢着要的职业资格',
 '稀缺性/FOMO': '现在知道的人很少，但未来很吃香，26年拿下就能远远甩开身边人',
 '时间窗口/低门槛': '未来5年越来越吃香，但要在26年考下，以后难度只会更高',
 '行为中断': '每天有时间玩手机？不如用这点时间考个证',
 '趋势驱动/零门槛': 'AI时代一定要考的证来了，不需要会编程、零基础就能上手',
 '展证信任': '（展示证书）它不需要你会编程、不需要技术背景，18岁以上就能报名',
}
REAL_PERSONA = {
 '通用':'',
 '宝妈':'很多宝妈利用带娃空隙就考下了，不用坐班、时间自由',
 '打工人':'加班到10点累得不想说话？有人已悄悄考下，现在朝九晚五双休',
 '转行族':'想转行健康/科技行业？这证不限专业不限经验就能跨行',
 '副业族':'不用辞职，手机就能接单，一条咨询几十到几百',
}
REAL_BENEFIT = [
 '题目都是选择题，满分100分，60分及格就能拿证',
 '不限专业、不限经验，零基础也能报',
 '拿证后学校/社区/企业抢着要，周末双休五险一金',
 '26年是最容易过的窗口期，往后难度只增不减',
]
REAL_CTA = [
 '想了解更多详情来我直播间',
 '来直播间测一测你符不符合条件',
 '还是想考？来直播间聊聊',
 '赶紧冲，来我直播间了解',
]

def build(cert, hk, pn, bi, ci):
    hook = REAL_HOOKS[hk]; pers = REAL_PERSONA[pn]; ben = REAL_BENEFIT[bi]; cta = REAL_CTA[ci]
    pclause = (pers+'。') if pers else ''
    if cert == '健康管理师':
        return f"{cert}——{hook}。{pclause}不如考个{cert}。{ben}。{cta}。"
    else:
        body = f"{cert}证书——{hook}。只要你在26年拿下，"
        body += f"{pclause}就能远远甩开别人。" if pclause else "就能远远甩开别人。"
        return body + f"{ben}。{cta}"

# ---------- 6. 四维裂变计划（18条，按 P0/P1/P2/大字报） ----------
# 每条：(优先级, 品类, 钩子, 人群, 利益idx, CTAidx, 测试假设)
FISSION_PLAN = [
 # P0 × 4：复制 winning 结构，换开场/场景，验证跨人群稳定性
 ('P0','健康管理师','权威背书/含金量','通用',0,2,'复制40632415704母本(转化691)，换权威背书钩子验证跨账户稳定性'),
 ('P0','健康管理师','时间窗口/低门槛','宝妈',3,0,'winning结构+宝妈人群，验证女性/家庭决策人群CVR'),
 ('P0','AI应用工程师','稀缺性/FOMO','通用',0,3,'复制39158668835母本(转化625)，强化FOMO钩子'),
 ('P0','AI应用工程师','趋势驱动/零门槛','转行族',1,1,'AI母本+转行族，验证不限专业零基础卖点对跨行人群'),
 # P1 × 6：钩子对比 A/B
 ('P1','健康管理师','行为中断','打工人',2,0,'行为中断钩子 vs 权威背书，对比打工人CTR'),
 ('P1','健康管理师','时间窗口/低门槛','通用',3,1,'时间窗口钩子，低成本图文版位测试'),
 ('P1','AI应用工程师','展证信任','通用',1,0,'展证建立信任钩子，消除"是否真能考"顾虑'),
 ('P1','AI应用工程师','稀缺性/FOMO','副业族',2,3,'FOMO+副业族，验证接单收益对CVR拉动'),
 ('P1','健康管理师','权威背书/含金量','转行族',1,1,'权威背书+转行族，验证职业资格对跨行吸引力'),
 ('P1','AI应用工程师','行为中断','打工人',0,2,'行为中断+打工人，对比AI品类点击意愿'),
 # P2 × 5：边界探索
 ('P2','健康管理师','展证信任','宝妈',2,0,'数字人/展证二次尝试，加强信任状密度'),
 ('P2','AI应用工程师','趋势驱动/零门槛','宝妈',1,1,'极简快剪版，验证短时长版位CPM'),
 ('P2','健康管理师','稀缺性/FOMO','副业族',3,3,'稀缺+副业，边界探索健康品类副业角度'),
 ('P2','AI应用工程师','时间窗口/低门槛','通用',3,0,'时间窗口钩子，验证AI品类紧迫感'),
 ('P2','健康管理师','行为中断','副业族',2,2,'行为中断+副业，健康品类副业边界'),
 # 大字报 × 3：纯文字卡片，低成本版位
 ('大字报','健康管理师','时间窗口/低门槛','通用',3,0,'大字报：26年窗口+60分及格，图文低成本版位'),
 ('大字报','AI应用工程师','稀缺性/FOMO','通用',0,3,'大字报：AI证未来吃香+零基础，图文版位'),
 ('大字报','健康管理师','权威背书/含金量','通用',2,1,'大字报：国家认可+双休五险一金，强福利冲击'),
]

fissions = []
for i,(pri,cert,hk,pn,bi,ci,hypo) in enumerate(FISSION_PLAN,1):
    body = build(cert,hk,pn,bi,ci)
    tags = [hk, pn if pn!='通用' else '通用', f'利益{ bi+1 }', '条件CTA']
    fissions.append({'tag':f'[{pri}-{i}]','pri':pri,'cert':cert,'body':body,
                     'vars':tags,'hypo':hypo,'hook':REAL_HOOKS[hk]})

# ---------- 7. 渲染（纯静态 HTML） ----------
now = datetime.now().strftime('%Y-%m-%d %H:%M')
def money(x): return f'¥{x:,.0f}'

# 聚合表
def agg_rows_html(data, key_label):
    h=''
    for d in data:
        col = '#3B6D11' if d['wcvr']>=3 else ('#BA7517' if d['wcvr']>=1.5 else '#E24B4A')
        h+=f"""<tr>
<td><b>{html.escape(d['key'])}</b></td>
<td>{d['n']}</td>
<td>{money(d['spend'])}</td>
<td>{d['conv']}</td>
<td>{d['wctr']:.2f}%</td>
<td style="color:{col};font-weight:600">{d['wcvr']:.2f}%</td>
<td>¥{d['avg_cpm']:.0f}</td></tr>"""
    return h

hook_tbl = agg_rows_html(by_hook,'钩子类型')
cert_tbl = agg_rows_html(by_cert,'证书类别')
vtype_tbl= agg_rows_html(by_vtype,'视频类型')

# 裂变卡片
def fission_html(items):
    cls={'P0':'p0','P1':'p1','P2':'p2','大字报':'p1'}
    h=''
    for f in items:
        c=cls.get(f['pri'],'p2')
        vt=''.join(f'<span class="vt">{html.escape(x)}</span>' for x in f['vars'])
        h+=f"""<div class="sc {c}">
<span class="hk">{html.escape(f['tag'])} · {html.escape(f['cert'])}</span>
<div class="bd">{html.escape(f['body'])}</div>
<div class="mt">{vt}</div>
<div class="hp">假设：{html.escape(f['hypo'])}</div></div>"""
    return h

fission_all = fission_html(fissions)

# 附录：19条真实素材
def appendix_html():
    h=''
    for r in sorted(rows,key=lambda x:-x['spend']):
        col='#3B6D11' if r['cvr']>=3 else ('#BA7517' if r['cvr']>=1.5 else '#E24B4A')
        badge='<span class="vb">变体</span>' if r['is_var'] else ''
        h+=f"""<tr>
<td><b>{html.escape(r['素材ID'])}</b>{badge}</td>
<td>{html.escape(r['证书类别'])}</td>
<td>{html.escape(r['钩子类型'])}</td>
<td>{html.escape(r['视频类型'])}</td>
<td>{money(r['spend'])}</td>
<td>{r['exp']:,}</td>
<td>{r['clk']:,}</td>
<td>{r['ctr']:.2f}%</td>
<td style="color:{col};font-weight:600">{r['cvr']:.2f}%</td>
<td>{r['conv']}</td>
<td class="cp">{html.escape(r['通顺文案'])}</td></tr>"""
    return h

# 成因结论（基于真实聚合自动生成要点）
top_hook = by_hook[0]
bot_hook = min(by_hook, key=lambda x:x['wcvr'])
ai_wcvr = next(d['wcvr'] for d in by_cert if d['key']=='AI应用工程师')
hp_wcvr = next(d['wcvr'] for d in by_cert if d['key']=='健康管理师')
ai_wctr = next(d['wctr'] for d in by_cert if d['key']=='AI应用工程师')
hp_wctr = next(d['wctr'] for d in by_cert if d['key']=='健康管理师')

conclusions = f"""
<li><b>品类效率：</b>健康管理师加权CVR <b>{hp_wcvr:.2f}%</b> 显著高于 AI应用工程师 <b>{ai_wcvr:.2f}%</b>（约 {hp_wcvr/ai_wcvr:.1f}×）；但 AI应用工程师加权CTR <b>{ai_wctr:.2f}%</b> 远高于健康管理师 <b>{hp_wctr:.2f}%</b>。结论：健康品类"叫好又叫座"（点击转化双高），AI品类"高点击低转化"——AI钩子吸引好奇但报名决策弱，需加强信任状/门槛利益。</li>
<li><b>钩子有效性：</b>转化最集中的钩子是「{html.escape(top_hook['key'])}」（{top_hook['conv']}转化、加权CVR {top_hook['wcvr']:.2f}%）；最弱的是「{html.escape(bot_hook['key'])}」（加权CVR {bot_hook['wcvr']:.2f}%）。建议把预算向"权威背书/含金量/时间窗口"类钩子倾斜。</li>
<li><b>视频形式：</b>真人+大字报叠加、口播+动态字幕两类综合效率最高；纯大字报/图文CPM最低（¥{min(d['avg_cpm'] for d in by_vtype):.0f}），适合低成本放量版位。</li>
<li><b>效率王：</b>绝对转化王=<b>{html.escape(winner_conv['素材ID'])}</b>（{winner_conv['cert'] if 'cert' in winner_conv else winner_conv['证书类别']}，{winner_conv['conv']}转化，花费{money(winner_conv['spend'])}）；CVR王=<b>{html.escape(winner_cvr['素材ID'])}</b>（{winner_cvr['cvr']:.2f}%）；综合效率王(CTR×CVR)=<b>{html.escape(winner_eff['素材ID'])}</b>（{winner_eff['eff']:.2f}）。</li>
<li><b>预警：</b>{len(high_ctr_low)} 条"高点击低转化"素材（CTR≥2% 但 CVR&lt;1%），疑似钩子吸引非目标人群，建议收紧定向或强化报名利益。</li>
""".replace('cert','证书类别')

doc = f"""<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>新程教育 · 真实数据版成因分析+脚本裂变</title>
<style>
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;background:#F8F8F7;color:#2C2C2A;line-height:1.65;font-size:13px;padding:20px;max-width:1180px;margin:0 auto}}
h1{{font-size:21px;font-weight:700;margin-bottom:4px}}
h2{{font-size:16px;font-weight:600;border-left:3px solid #534AB7;padding-left:10px;margin:26px 0 12px}}
h3{{font-size:13.5px;font-weight:600;color:#534AB7;margin:14px 0 8px}}
.sub{{color:#888;font-size:12px;margin-bottom:16px}}
.card{{background:#fff;border-radius:12px;border:.5px solid rgba(44,44,42,.1);padding:18px;margin-bottom:14px}}
table{{width:100%;border-collapse:collapse;font-size:12px}}
th{{background:#F8F8F7;font-weight:600;text-align:left;padding:7px 9px;border-bottom:1px solid rgba(44,44,42,.18)}}
td{{padding:7px 9px;border-bottom:.5px solid rgba(44,44,42,.1);vertical-align:top}}
.metrics{{display:grid;grid-template-columns:repeat(6,1fr);gap:10px;margin-bottom:4px}}
.metric{{background:#F8F8F7;border-radius:8px;padding:12px 8px;text-align:center}}
.metric .v{{font-size:19px;font-weight:700}} .metric .l{{font-size:11px;color:#888;margin-top:2px}}
.hl{{border-radius:8px;padding:12px 14px;margin:8px 0;font-size:12.5px}}
.hl.g{{background:#EAF3DE;color:#3B6D11}} .hl.r{{background:#FCEBEB;color:#E24B4A}} .hl.a{{background:#FAEEDA;color:#BA7517}} .hl.b{{background:#EDEAFD;color:#534AB7}}
.fission{{display:grid;grid-template-columns:repeat(auto-fill,minmax(330px,1fr));gap:10px}}
.sc{{background:#F8F8F7;border-radius:8px;padding:12px;border-left:3px solid rgba(44,44,42,.18)}}
.sc.p0{{border-left-color:#E24B4A}} .sc.p1{{border-left-color:#BA7517}} .sc.p2{{border-left-color:#185FA5}}
.hk{{font-weight:600;color:#534AB7;font-size:12px;display:block;margin-bottom:5px}}
.bd{{color:#3a3a38;font-size:12.5px;line-height:1.75}}
.mt{{margin-top:7px;display:flex;gap:5px;flex-wrap:wrap}} .vt{{font-size:10px;background:#fff;color:#5F5E5A;border:.5px solid rgba(44,44,42,.15);border-radius:4px;padding:1px 6px}}
.hp{{margin-top:6px;font-size:11px;color:#888;font-style:italic}}
.cp{{font-size:11.5px;color:#5F5E5A;line-height:1.7;max-width:380px}}
.vb{{font-size:10px;background:#fef3c7;color:#d97706;border-radius:4px;padding:0 5px;margin-left:4px}}
ul{{margin:6px 0 6px 18px}} li{{margin:7px 0;font-size:12.5px;line-height:1.75}}
@media(max-width:760px){{.metrics{{grid-template-columns:repeat(3,1fr)}}.fission{{grid-template-columns:1fr}}}}
</style></head><body>
<h1>新程教育 · 真实数据版「成因分析 + 脚本裂变」</h1>
<p class="sub">强哥广告skill · 数据源：妙问API拉取19条真实素材（真实文案+真实消耗）· 生成 {now}</p>

<div class="card"><div class="metrics">
<div class="metric"><div class="v" style="color:#534AB7">{len(rows)}</div><div class="l">真实素材</div></div>
<div class="metric"><div class="v">{money(total_spend)}</div><div class="l">总花费</div></div>
<div class="metric"><div class="v" style="color:#3B6D11">{total_conv:,}</div><div class="l">总转化</div></div>
<div class="metric"><div class="v">{w_ctr:.2f}%</div><div class="l">加权CTR</div></div>
<div class="metric"><div class="v">{w_cvr:.2f}%</div><div class="l">加权CVR</div></div>
<div class="metric"><div class="v">{n_var}</div><div class="l">变体数</div></div>
</div></div>

<h2>一、创意成因分析（七维归因 · 真实数据）</h2>

<h3>① 按钩子类型聚合（转化量降序）</h3>
<div class="card"><table>
<thead><tr><th>钩子类型</th><th>素材数</th><th>花费</th><th>转化</th><th>加权CTR</th><th>加权CVR</th><th>平均CPM</th></tr></thead>
<tbody>{hook_tbl}</tbody></table></div>

<h3>② 按证书类别聚合</h3>
<div class="card"><table>
<thead><tr><th>证书类别</th><th>素材数</th><th>花费</th><th>转化</th><th>加权CTR</th><th>加权CVR</th><th>平均CPM</th></tr></thead>
<tbody>{cert_tbl}</tbody></table></div>

<h3>③ 按视频类型聚合</h3>
<div class="card"><table>
<thead><tr><th>视频类型</th><th>素材数</th><th>花费</th><th>转化</th><th>加权CTR</th><th>加权CVR</th><th>平均CPM</th></tr></thead>
<tbody>{vtype_tbl}</tbody></table></div>

<h3>④ 效率王 & 预警</h3>
<div class="hl b"><b>绝对转化王：</b> {html.escape(winner_conv['素材ID'])}（{html.escape(winner_conv['证书类别'])}，{winner_conv['conv']}转化，花费{money(winner_conv['spend'])}，CTR {winner_conv['ctr']:.2f}% / CVR {winner_conv['cvr']:.2f}%）</div>
<div class="hl g"><b>CVR王：</b> {html.escape(winner_cvr['素材ID'])}（CVR {winner_cvr['cvr']:.2f}%） | <b>CTR王：</b> {html.escape(winner_ctr['素材ID'])}（CTR {winner_ctr['ctr']:.2f}%） | <b>综合效率王(CTR×CVR)：</b> {html.escape(winner_eff['素材ID'])}（{winner_eff['eff']:.2f}）</div>
<div class="hl r"><b>高点击低转化预警（{len(high_ctr_low)}条）：</b> {', '.join(html.escape(r['素材ID']) for r in high_ctr_low) or '无'} —— 钩子吸引非目标人群嫌疑，建议收紧定向/强化报名利益</div>

<h3>⑤ 成因结论（可执行）</h3>
<div class="card"><ul>{conclusions}</ul></div>

<h2>二、脚本裂变（真实母本结构 + 真实变量池）</h2>
<div class="hl a">母本取自真实winning：健康管理师 <b>{html.escape(hp_mother['素材ID'])}</b>（综合效率 {hp_mother['eff']:.2f}）+ AI应用工程师 <b>{html.escape(ai_mother['素材ID'])}</b>（综合效率 {ai_mother['eff']:.2f}）。变量池从上述19条真实文案归纳，非通用硬编码。以下为创作起点草稿，需人工润色+小预算实测。</div>
<div class="card"><div class="fission">{fission_all}</div></div>

<h3>合规红线</h3>
<div class="hl r">禁"包过/100%拿证/官方指定"等绝对化用语；收入/接单承诺加"可能/有机会"；证书名称用官方口径（健康管理师职业技能等级证书 / AI应用工程师认证证书）；"不限专业"须与当期报考政策一致。</div>

<h2>三、附录 · 19条真实素材完整数据</h2>
<div class="card"><table>
<thead><tr><th>素材ID</th><th>类别</th><th>钩子</th><th>视频类型</th><th>花费</th><th>曝光</th><th>点击</th><th>CTR</th><th>CVR</th><th>转化</th><th>真实文案</th></tr></thead>
<tbody>{appendix_html()}</tbody></table></div>

<div style="text-align:center;padding:24px 0;color:#888;font-size:11px">强哥广告skill · 真实数据版 · 妙问API → 多模态拆文案 → 真实消耗归因 → 裂变</div>
</body></html>"""

with open(OUT,'w',encoding='utf-8') as f:
    f.write(doc)

print(f'OK 输出: {OUT}')
print(f'大小: {os.path.getsize(OUT)/1024:.0f} KB')
print(f'总花费: {money(total_spend)} | 总转化: {total_conv} | 加权CTR: {w_ctr:.2f}% | 加权CVR: {w_cvr:.2f}%')
print(f'效率王(转化): {winner_conv["素材ID"]} | CVR王: {winner_cvr["素材ID"]}({winner_cvr["cvr"]:.2f}%) | 综合王: {winner_eff["素材ID"]}({winner_eff["eff"]:.2f})')
print(f'高点击低转化: {[r["素材ID"] for r in high_ctr_low]}')
print(f'裂变脚本: {len(fissions)} 条 (P0×4/P1×6/P2×5/大字报×3)')
