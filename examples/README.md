# 示例数据（examples/）

本目录提供**最小可运行示例**，让你克隆仓库后能立即跑通真实数据版裂变，无需准备真实投放数据。

## 文件说明

| 文件 | 对应真实管线产物 | 用途 |
|------|------------------|------|
| `videos_multimodal_fixed.csv` | 多模态拆解出的通顺文案 + 真实消耗 | `real_fission.py` / `real_fission_v2.py` 的输入 |
| `dynamic_analysis.json` | OpenCV 程序化动态分析输出 | `real_fission_v2.py` / `render_dynamic_report.py` 的输入 |

## 直接跑

```bash
# 在仓库根目录
python scripts/real_fission.py --base ./examples
python scripts/real_fission_v2.py --base ./examples
```

即可在 `examples/` 下生成 `xincheng_real_fission_report.html` / `xincheng_real_fission_v2_report.html`。

> 注意：`real_fission_v2.py` 顶部的 `FMT` 字典是按原账户写的素材 ID → 视觉格式映射。
> 示例 ID（`10000000001` 等）不在其中，会**自动回退**到 `dynamic_analysis.json` 的 `style_summary` 字段，
> 报告/裂变仍可正常生成（只是不显示作者专属的格式命名）。换你自己的数据时，把 `FMT` 改成你的映射即可。
