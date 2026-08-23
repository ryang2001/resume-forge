# resume-forge

把岗位 JD 锻造成**一页 A4 定制简历(HTML + PDF)**的 Claude Code Skill:档案匹配 + 诚实基线 + STAR chip 排版 + 无头 Chrome 自动导出与**内容级验证** + 多版本矩阵管理。

来自真实求职季的实战沉淀——19 个定向简历版本、三段经历的 STAR 重写、多次诚实口径修正,以及一次"19 个 PDF 全是 Chrome 错误页"的导出事故复盘。

## 功能

| 功能 | 说明 |
|---|---|
| JD 定制 | 解析岗位 JD → 关键词命中表 → 档案匹配(缺 gap 不编造)→ 定向产出 |
| 诚实基线 | 候选人档案内置"铁律区":数字口径、未收敛项目、公司资产 vs 个人产出、禁写清单,每次产出前逐条核对 |
| STAR chip 排版 | 每条经历 = 加粗标题 + `背景`/`方法`/`结果` 主题色小标签 + 量化高亮;附写作禁忌(如"教科书结构展开=AI 味") |
| 一页 A4 自动保障 | 导出工具自动检测溢出,注入 zoom 从 0.97 逐级压回恰好一页 |
| 内容级验证 | 页数 + 体积 + 嵌入图片三重校验,专治"错误页也是一页"的假 PDF |
| 多版本矩阵 | 求职意向/主色/经历侧重差异化,含"经历评审清单"批量改写工作流 |

## 安装

```bash
# 用户级(所有项目可用)
git clone https://github.com/ryang2001/resume-forge.git
cp -r resume-forge ~/.claude/skills/resume-forge

# 或项目级
cp -r resume-forge <你的项目>/.claude/skills/resume-forge
```

然后把你的资料按 `profile/profile.example.md` 的格式填成 `profile/profile.md`。

## 使用

对 Claude 说:

```
按这个 JD 改简历:<粘贴岗位描述>
```

Claude 会走完整流程:JD 解析 → 档案匹配(诚实检查)→ 定位(意向/主打经历/主色)→ STAR 写作 → 生成 HTML → 自动导出 PDF → 内容级验证 → 汇报(命中表 + 诚实边界 + 面试 defense)。

工具也可以单独用:

```bash
# 导出并自动压页(URL 自动编码,防"错误页 PDF")
python scripts/export_autofit.py 我的简历_某版本.html

# 内容级验证(页数/体积/嵌入图片)
python scripts/verify_pdf.py 我的简历_某版本.pdf
```

## 目录结构

```
resume-forge/
├── SKILL.md                     # Skill 本体:完整流程、写作规范、模板规则
├── scripts/
│   ├── export_autofit.py        # HTML → 一页 PDF(无头 Chrome + zoom 自动压页)
│   └── verify_pdf.py            # PDF 内容级验证(无第三方依赖)
├── template/
│   └── resume_template.html     # A4 模板(chip 标签/主色/tech-tag/highlight)
└── profile/
    └── profile.example.md       # 候选人档案模板(含诚实基线铁律区)
```

## 踩坑记录(都写进了 SKILL.md)

1. **中文路径 URL 必须百分号编码**——否则 Chrome 把 `ERR_FILE_NOT_FOUND` 错误页打印成 PDF(≈39KB),且错误页"恰好一页",只查页数发现不了
2. **验证必须内容级**——体积 + 嵌入图片 + 页数三重判别
3. **`--virtual-time-budget=15000`**——不加的话无头打印在网络字体加载完成前截图,PDF 悄悄回落本地字体
4. **独立 `--user-data-dir`** 且用 Windows 风格路径,否则吸附已运行的 Chrome 报 0x5;`--print-to-pdf` 路径必须绝对
4. **教科书结构不展开写**——"条件 UNet(通道拼接+编码器-解码器+跳连)"这类复述定义一眼假,专业度靠具体参数与真实工作量
5. **诚实基线**——未收敛不报精度、定性验证≠定量验证、公司平台不写"自研"、对比数字带前提;简历经不起追问会被刷

## License

MIT
