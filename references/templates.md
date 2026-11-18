# 模板

复制后填空。结构比样式重要；HTML 只为本项目阅读方便，换成 Markdown 也可以，但任务单/审查记录的文件扩展名要与台账里写的一致。

---

## 1. `.dual-session/config.json`（可选）

不建就用下面的默认值。建了只覆盖路径，**不写角色**——角色是每个会话自己的事。

```json
{
  "reviewer_root": "审查与规划",
  "task_dir": "审查与规划/任务单",
  "ledger_dir": "审查与规划/台账",
  "review_dir": "审查与规划/审查记录",
  "delivery_dir": "交付",
  "executor_dirs": ["code", "paper", "data", "交付"]
}
```

---

## 2. 三本台账的表头

`审查与规划/台账/任务台账.csv`：

```csv
编号,标题,对应问题,执行方,下达日期,前置条件,状态,任务单,交付物,验收日期,验收结论
```

`审查与规划/台账/问题台账.csv`：

```csv
编号,发现日期,严重程度,标题,证据,影响,修法,验收标准,负责方,关联,状态,关闭日期,关闭证据
```

`审查与规划/台账/决策台账.csv`：

```csv
编号,决定事项,审查方建议,理由,影响到,提出日期,状态,用户决定,决定日期
```

行示例：

```csv
T018,摘要与正文口径统一,M4,美赛工作Agent,2026-11-19,T012 通过,待执行,审查与规划/任务单/T018_摘要口径.html,交付/T018_delivery.json 与 data/runs/T018/,,
```

```csv
M9,摘要写“任何分辨率都不缺车”，但 T004 有 5.84% 未满足,summary.tex:23-27；交付/T004_delivery.json,结论与证据相反,按 T004 口径改写摘要与 §9,摘要/§9 两处数字一致且不再出现“任何分辨率”,执行方,T018,打开,,
```

```csv
B8,p 主值用 0.128 还是 0.185,用 0.185 并全部重算,0.128 只覆盖部分日期且偏差方向已知；0.185 是全部样本的中心估计,所有绝对量、T018、摘要,2026-11-19,待定,,
```

---

## 3. 任务单 HTML 模板

```html
<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>T018 摘要与正文口径统一</title>
<style>
:root{--bg:#fbfaf7;--fg:#1d1d1f;--muted:#5f6368;--line:#dcdcd6;--card:#fff;--accent:#1f4e79;--hi:#b3261e;--warn:#8a5a00;--code:#f1f0ea}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#16171a;--fg:#e6e6e3;--muted:#a3a7ad;--line:#36383d;--card:#1d1f23;--accent:#8db7e5;--hi:#ff8a80;--warn:#e0b45c;--code:#26282d}}
:root[data-theme="dark"]{--bg:#16171a;--fg:#e6e6e3;--muted:#a3a7ad;--line:#36383d;--card:#1d1f23;--accent:#8db7e5;--hi:#ff8a80;--warn:#e0b45c;--code:#26282d}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font:15px/1.75 -apple-system,"PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:1000px;margin:0 auto;padding:24px 16px 72px}
h1{font-size:23px;margin:6px 0 4px;color:var(--accent)}
h2{font-size:18px;margin:30px 0 8px;padding-bottom:6px;border-bottom:1px solid var(--line);color:var(--accent)}
p{margin:8px 0}.meta{color:var(--muted);font-size:13px}
.box{background:var(--card);border:1px solid var(--line);border-left:4px solid var(--accent);border-radius:8px;padding:12px 16px;margin:12px 0}
.box.warn{border-left-color:var(--warn)}.box.hi{border-left-color:var(--hi)}
table{border-collapse:collapse;width:100%;font-size:13.5px}
th,td{border:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{background:var(--code);font-weight:600}
code{background:var(--code);border-radius:4px;font-size:12.5px;font-family:Consolas,Menlo,monospace;padding:1px 4px;word-break:break-all}
ul,ol{padding-left:22px;margin:6px 0}li{margin:3px 0}
</style>
</head>
<body><main>

<h1>T018 · 摘要与正文口径统一</h1>
<p class="meta">状态：<strong>已下达 2026-11-19</strong>　·　前置：T012 通过　·　对应问题：M4　·　执行方：美赛工作Agent</p>

<div class="box hi">
<p><strong>为什么做。</strong>摘要仍写“任何分辨率都不缺车”，但 T004 在 R=450 下有 5.84%/3.51% 未满足；§9 又写 13.4%。同一结论三处口径不一致，评委可直接抓出。本任务只统一口径，不新做模型。</p>
</div>

<h2>1. 范围</h2>
<div class="box">
<p><strong>可写：</strong><code>paper/summary.tex</code>、<code>paper/sec9_sensitivity.tex</code>、<code>paper/sec10_evaluation.tex</code>。</p>
<p><strong>不写：</strong><code>code/</code>、<code>data/</code>、<code>审查与规划/</code>；不重跑模型；不改任何结果文件。</p>
<p><strong>不做什么：</strong>不新增敏感性实验；不改变 R=450 的口径；不把 13.4% 删掉了事，要写明它来自哪个模型。</p>
</div>

<h2>2. 输入</h2>
<ul>
<li><code>交付/T004_delivery.json</code>：R=450 的 5.84%/3.51%，R=600 的 2.35%/1.28%，细网格 2.07%。</li>
<li><code>交付/T012_delivery.json</code> 的 <code>affected</code>：已改过的口径。</li>
<li>题面原文：Q2/Q4 要求使用 Q1 的行为模型。</li>
</ul>

<h2>3. 修改条目</h2>
<table>
<thead><tr><th style="width:8%">编号</th><th style="width:22%">位置</th><th style="width:35%">现文</th><th style="width:35%">改为</th></tr></thead>
<tbody>
<tr><td>T018-1</td><td><code>paper/summary.tex:23-27</code></td><td>“At every resolution … no zone ever runs out”</td><td>按 T004 写：R=450 下 5.84%（封闭车队）/3.51%（细网格），并说明“不缺车”只在 R=300 的旧口径成立</td></tr>
<tr><td>T018-2</td><td><code>paper/sec9_sensitivity.tex:106-108</code></td><td>“13.4% unmet”</td><td>改为 R=450 的 5.84%/3.51%，并注明 13.4% 是 R=300 且无邻格的口径</td></tr>
</tbody>
</table>

<h2>4. 验收</h2>
<ol>
<li><code>grep -rn "any resolution\|no zone ever runs out\|13.4" paper/*.tex</code>：旧表述命中 0，或命中处已带新口径说明。</li>
<li>摘要、§9、§10 三处同一量的数值一致；抽查 3 处，0 处冲突。</li>
<li>每个改动的数都能在 <code>交付/T004_delivery.json</code> 找到对应字段；交付 <code>affected</code> 列 old/new/basis。</li>
<li>xelatex 两遍：undefined 0、overfull 0、正文 ≤25 页。</li>
<li>重交 <code>交付/T018_delivery.json</code>：<code>checks</code> 覆盖 1–4；<code>notes</code> 写明未处理项。</li>
</ol>

<div class="box warn">
<p><strong>边界：</strong>如果发现 T004 的数字本身不可复现，停止，交 <code>blocked</code>，不要用旧数凑。不要为了页数删掉“13.4% 的来源说明”。</p>
</div>

</main></body></html>
```

---

## 4. 交付 JSON 模板

```json
{
  "task": "T018",
  "title": "摘要与正文口径统一",
  "date": "2026-11-19",
  "status": "delivered",
  "revision": "R0",
  "summary": "把摘要、§9、§10 的未满足率统一到 T004 的 R=450 口径；旧 13.4% 保留为 R=300 的对照并注明来源。所有数字来自 T004 交付，未重跑模型。",
  "checks": {
    "1_old_phrases_zero": "pass; rg -n 'any resolution|no zone ever runs out|13\\.4' paper/*.tex -> 0 hits after edit",
    "2_three_places_consistent": "pass; summary=5.84/3.51, sec9=5.84/3.51, sec10=5.84/3.51",
    "3_numbers_traceable": "pass; T004_delivery.json checks.6_* and q4_* fields",
    "4_compile": "pass; xelatex 2 passes, undefined=0, overfull=0, body=24 pages"
  },
  "affected": [
    {"location": "paper/summary.tex:23-27", "old": "At every resolution ... no zone ever runs out", "new": "At R=450, 5.84% (closed fleet) / 3.51% (fine grid) ...", "basis": "交付/T004_delivery.json"},
    {"location": "paper/sec9_sensitivity.tex:106-108", "old": "13.4% unmet", "new": "5.84%/3.51% at R=450; 13.4% is the R=300 no-neighbour figure", "basis": "交付/T004_delivery.json"}
  ],
  "outputs": ["paper/main.pdf"],
  "notes": [
    "13.4% is retained only as the old R=300 baseline; not deleted.",
    "No model rerun; all numbers are from the frozen T004 delivery."
  ],
  "integrity": {
    "readonly_respected": true,
    "no_files_written_in_review_or_planning": true
  }
}
```

---

## 5. 验收记录 HTML 模板

```html
<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><title>T018 验收</title>
<style>body{font:15px/1.7 -apple-system,"Microsoft YaHei",sans-serif;max-width:960px;margin:0 auto;padding:24px}
h1{font-size:22px;color:#1f4e79}h2{font-size:17px;border-bottom:1px solid #ddd;padding-bottom:4px}
code{background:#f1f0ea;padding:1px 4px;border-radius:4px}
table{border-collapse:collapse;width:100%}th,td{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top}
.ok{color:#1e6b3a}.bad{color:#b3261e}</style></head><body>
<h1>T018 验收记录</h1>
<p>验收日期：2026-11-19　·　验收人：指导方　·　结论：<strong class="ok">通过</strong></p>
<h2>1. 读了什么</h2>
<ul><li>交付/T018_delivery.json</li><li>paper/summary.tex、sec9_sensitivity.tex、sec10_evaluation.tex</li><li>交付/T004_delivery.json</li></ul>
<h2>2. 复算了什么</h2>
<table><tr><th>项</th><th>命令/方法</th><th>结果</th></tr>
<tr><td>R=450 未满足率</td><td>读 T004_delivery.json 的 q4_* 字段</td><td>5.84% / 3.51%，与正文一致</td></tr>
<tr><td>旧表述残留</td><td><code>rg -n "any resolution|13\.4" paper/*.tex</code></td><td>0 处旧表述</td></tr></table>
<h2>3. 差异与未解决项</h2>
<p>无。13.4% 仅作为 R=300 对照保留，并已注明口径。</p>
<h2>4. 后续</h2>
<p>关闭 M4；无后续任务。</p>
</body></html>
```

---

## 6. 返工任务单的增量写法

不重写整张任务单，在原文件末尾加：

```html
<h2>R1 返工（2026-11-20）</h2>
<ol>
<li><strong>[高]</strong> 摘要只改了第一句，第二句仍写“no zone ever runs out”。证据：<code>summary.tex:27</code>。修法：按 T018-1 改全。复验：grep 命中 0。</li>
<li><strong>[中]</strong> 交付 <code>checks.3</code> 只写“traceable”，没有给字段名。修法：补 <code>T004_delivery.json</code> 的具体键。复验：指导方能按路径打开。</li>
</ol>
```

同时把任务台账状态改为 `退回 R1`，交付 JSON 的 `revision` 改为 `R1`。

---

## 7. 新项目初始化命令

```bash
mkdir -p 审查与规划/任务单 审查与规划/审查记录 审查与规划/台账 交付
printf '\xEF\xBB\xBF编号,标题,对应问题,执行方,下达日期,前置条件,状态,任务单,交付物,验收日期,验收结论\n' > 审查与规划/台账/任务台账.csv
printf '\xEF\xBB\xBF编号,发现日期,严重程度,标题,证据,影响,修法,验收标准,负责方,关联,状态,关闭日期,关闭证据\n' > 审查与规划/台账/问题台账.csv
printf '\xEF\xBB\xBF编号,决定事项,审查方建议,理由,影响到,提出日期,状态,用户决定,决定日期\n' > 审查与规划/台账/决策台账.csv
```

Windows PowerShell 也可以直接用编辑器建 UTF-8 CSV；关键是表头逐字一致，脚本才能读。
