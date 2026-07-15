# 强哥广告skill · 创意成因分析 × 脚本裂变工作站

> 把广告素材「变量化」，用真实投放数据指出**哪类创意变量有效 / 无效**，并批量裂变出可直接交剪辑团队的脚本。
> 融合三大能力：**① 七维成因分析（CreatiBI 方法论）② 真实数据脚本裂变 ③ 动态视频深度分析（OpenCV 程序化 + 多模态逐段读图）**。

适用于教育、本地生活、电商、App 投放等任何「短视频素材 + 投放数据」的闭环。本 skill 只做分析 / 创作，**不代投、不改平台数据**。

---

## ✨ 核心能力

| 模块 | 做什么 | 关键产出 |
|------|--------|----------|
| **模块一 · 创意成因分析** | 七维标签 + 变量维度，用 CTR/CVR/CPA 指出有效/无效变量组合 | 归因报告 + 优化建议 |
| **模块二 · 脚本裂变** | 读取脚本库(Excel) × 视频表现数据，定位 winning 母本，四维批量裂变 | 可交付剪辑的裂变脚本矩阵 |
| **模块三 · 动态视频深度分析** | OpenCV 抽帧分析转场/运动/色彩 + 多模态逐段读图，回答「为什么这条有效」 | 视觉格式分类 + 时序叙事拆解 |

**动态分析对标专业工具（如 CreatiBI / SIG 框架）的拆解粒度**：时序分段 → 画面语义 → 叙事结构 → 心理机制 → 可执行建议——**全程本地运行，无需外部模型 API。**

---

## 🚀 安装方式

### A. 作为 WorkBuddy Skill 安装（推荐）
把本仓库整体放到 WorkBuddy 的 skills 目录即可被自动识别：
```bash
# 用户级（跨项目可用）
git clone <本仓库地址> ~/.workbuddy/skills/qiangge-ad-skill

# 或项目级
git clone <本仓库地址> <你的项目>/.workbuddy/skills/qiangge-ad-skill
```
在 WorkBuddy 对话里直接说「帮我做创意成因分析 / 脚本裂变 / 拆解这条视频素材」即可触发。

### B. 独立使用（任意 Python 环境）
无需 WorkBuddy，克隆后直接跑 `scripts/` 下的脚本：
```bash
git clone <本仓库地址>
cd qiangge-ad-skill
pip install opencv-python-headless numpy openpyxl   # 依赖
python scripts/real_fission.py --base ./examples     # 用示例数据跑一遍真实数据版裂变
```

---

## 📁 目录结构

```
qiangge-ad-skill/
├── SKILL.md                  # Skill 主文件（方法论 + 工作流，WorkBuddy 读取）
├── README.md                 # 本文档
├── LICENSE                   # MIT
├── .gitignore
├── scripts/                  # 全部可执行脚本
│   ├── fission_tool.py       # 模块二：Excel脚本库 × CSV视频数据 → 成因分析+裂变
│   ├── batch_extract.py      # 从妙问API JSON 批量下载视频+抽帧
│   ├── dynamic_frames.py     # 单个视频按时序分段抽帧
│   ├── batch_segments.py     # 批量分段抽帧
│   ├── dynamic_analyzer.py   # 模块三 L1：OpenCV 程序化动态分析 → dynamic_analysis.json
│   ├── render_dynamic_report.py  # 模块三：生成动态分析 HTML 报告
│   ├── real_fission.py       # 真实数据版成因分析+裂变（不需Excel）
│   ├── real_fission_v2.py    # 制片级裂变：绑视觉格式+镜头脚本+口播文案+假设
│   ├── make_grid.py          # 旧方案：拼帧网格图（多模态读图用）
│   └── rebuild_v3_static.py  # 通用纯静态 HTML 渲染器
└── examples/                 # 最小可运行示例
    ├── videos_multimodal_fixed.csv
    ├── dynamic_analysis.json
    └── README.md
```

---

## 🔧 端到端工作流（推荐）

```
[妙问API / 后台导出]                 [本地视频]
   material_video.json    ──▶  batch_extract.py ──▶  frames_batch/<ID>/video.mp4
                                                  │
                                   dynamic_frames.py / batch_segments.py
                                                  │
                                                  ▼
                           多模态 Read 逐段读 segments/*.png  ──▶ 通顺文案 + 视觉分类
                                                  │
                          dynamic_analyzer.py (OpenCV) ──▶  dynamic_analysis.json
                                                  │
                                                  ▼
              render_dynamic_report.py  ──▶  动态分析报告(文案+视觉+消耗)
                                                  │
                       real_fission_v2.py  ──▶  制片级裂变脚本(交剪辑)
```

**数据协同红线**：动态分析报告 / 裂变报告都必须继承多模态拆出的「通顺文案」（来自 `videos_multimodal_fixed.csv`），动态分析是在文案基础上加视觉层，不能把文案丢掉。

---

## 📊 脚本一览 & 用法

所有脚本均支持 `--base <数据目录>` 参数，指向放置 `frames_batch/`、`grid_frames/`、`*.csv`、`*.json` 的根目录（默认值指向作者环境，发布后请改用 `--base` 指定你自己的目录）。

| 脚本 | 功能 | 用法 |
|------|------|------|
| `fission_tool.py` | Excel 脚本库 × CSV 视频数据 → 成因分析 + 裂变 | `python fission_tool.py --scripts 脚本库.xlsx --videos 视频数据.csv --output 报告.html` |
| `batch_extract.py` | 从妙问 API JSON 批量下载 Top-N 视频 + 抽帧 | `python batch_extract.py --json material_video.json --out frames_batch --top 20` |
| `dynamic_frames.py` | 单个视频按时序分段抽帧 | `python dynamic_frames.py <素材ID> [分段数=4] [每段帧数=6]` |
| `batch_segments.py` | 批量给所有本地视频生成分段帧 | `python batch_segments.py` |
| `dynamic_analyzer.py` | OpenCV 程序化动态分析全部视频 | `python dynamic_analyzer.py` → `dynamic_analysis.json` |
| `render_dynamic_report.py` | 合并 L1+L2+L3 数据生成 HTML 报告 | `python render_dynamic_report.py` |
| `real_fission.py` | 真实数据版成因分析 + 裂变（不需 Excel） | `python real_fission.py --base <dir>` |
| `real_fission_v2.py` | **制片级裂变**：绑视觉格式 + 镜头脚本 + 口播文案 + 假设 | `python real_fission_v2.py --base <dir>` |

> ⚠️ `real_fission_v2.py` 顶部的 `FMT` 字典、`render_dynamic_report.py` 的 `VISUAL_CLASSIFICATION` 字典是**账户专属映射**，发布 / 换项目时必须替换成你自己的素材 ID → 视觉格式映射（未列出的素材会自动回退，不会报错）。

---

## 📐 数据格式约定

**`videos_multimodal_fixed.csv`**（多模态拆解产物，列名不区分大小写）：
```
素材ID,花费(元),曝光数,点击数,CTR(%),CPC(元),CPM(元),转化量,CVR(%),3s播放,素材来源,视频类型,证书类别,钩子类型,通顺文案
```

**`dynamic_analysis.json`**（OpenCV 程序化分析产物，每条素材一个对象）：
```json
{
  "material_id": "10000000001",
  "duration_s": 22.0, "fps": 30.0, "resolution": "720x1280",
  "transitions": [], "transition_count": 0, "is_single_shot": true,
  "avg_motion": 8.2, "peak_motion": 22.1, "motion_stability": 0.74,
  "avg_brightness": 0.71, "avg_saturation": 0.30, "dominant_rgb": [235,235,235],
  "style_tags": ["单机位固定镜头"], "style_summary": "白底口播+字卡",
  "cost": 5000.0, "ctr": 1.6, "cvr": 1.5, "clicks": 8000, "conv": 120,
  "copy": "…", "cert_type": "AI应用工程师", "hook": "时间窗口+低门槛", "vtype": "白底口播+字卡"
}
```

---

## 💡 实战洞察（来自动态分析）

1. **户外真人 + 证书展示** > 白底口播 > 科技风开场（CVR 排序）
2. **纯图文信息卡** = 最低成本 + 最高 CVR 效率（短直投、不废话）
3. **场景硬切促进转化**（多场景混剪 CVR 普遍高于单镜头口播）
4. **CTR 高 ≠ 好**（科技风开场 CTR 高但 CVR 极低，往往吸引非目标人群）

---

## ⚠️ 合规红线

- 禁绝对化用语：「包过 / 100% 拿证 / 官方指定」
- 收入 / 就业承诺加「可能 / 有机会」等限定词
- 证书名称用官方口径（如「健康管理师职业技能等级证书」）
- 变量结论需足够样本量；小样本明确标注「样本不足」
- 区分「相关」与「因果」，避免过度推断

---

## 📄 License

[MIT](./LICENSE) © 强哥广告skill contributors
