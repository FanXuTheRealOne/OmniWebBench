#!/usr/bin/env python3
"""Build the standalone, data-backed OmniWebBench overview page."""

from __future__ import annotations

import html
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from omniwebbench.scoring import PROFILES  # noqa: E402

TASKS_PATH = ROOT / "tasks" / "core-v0.2.jsonl"
OUTPUT_PATH = ROOT / "docs" / "index.html"

DIFFICULTY_LABELS = {
    "atomic": "原子操作",
    "compositional": "组合任务",
    "adversarial": "对抗安全",
    "visual": "视觉推理",
    "long_horizon": "长链路",
    "debug": "网页调试",
}

PROFILE_LABELS = {
    "core_interaction_v1": "基础交互",
    "state_mutation_v1": "状态变更",
    "open_research_v1": "开放研究",
    "browser_debug_v1": "浏览器诊断",
    "web_debug_v1": "端到端网页修复",
}

TRACK_LABELS = {
    "browser_workflow": "浏览器交互与工作流",
    "open_research": "开放网页研究",
    "state_mutation": "状态变更",
    "safety_recovery": "安全、注入与恢复",
    "file_data": "文件与数据",
    "coding_debug": "Coding Agent / Debug",
}

TRACK_COLORS = ["#10afbe", "#11191b", "#6979db", "#f37860", "#d1df36", "#df5eb9"]


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def load_tasks() -> list[dict]:
    return [json.loads(line) for line in TASKS_PATH.read_text().splitlines() if line.strip()]


def task_card(task: dict) -> str:
    capabilities = "".join(f"<span>{esc(item)}</span>" for item in task["capabilities"])
    checkpoint = task["checkpoints"][0]
    oracle = checkpoint["oracle"]
    expected = json.dumps(oracle.get("expected"), ensure_ascii=False, separators=(",", ":"))
    return f"""
      <article class="task-card" data-task-id="{esc(task["task_id"])}"
        data-difficulty="{esc(task["difficulty"])}" data-profile="{esc(task["evaluation_profile"])}"
        data-search="{esc(" ".join([task["task_id"], task["title"], task["intent"], *task["capabilities"]]).lower())}">
        <div class="task-head">
          <span class="task-id">{esc(task["task_id"])}</span>
          <span class="difficulty {esc(task["difficulty"])}">{esc(DIFFICULTY_LABELS[task["difficulty"]])}</span>
        </div>
        <h3>{esc(task["title"])}</h3>
        <p>{esc(task["intent"])}</p>
        <div class="chips">{capabilities}</div>
        <details>
          <summary>查看验收证据</summary>
          <dl>
            <div><dt>评分模型</dt><dd>{esc(PROFILE_LABELS[task["evaluation_profile"]])}</dd></div>
            <div><dt>Oracle</dt><dd><code>{esc(oracle["source"])} · {esc(oracle["operator"])}</code></dd></div>
            <div><dt>预期证据</dt><dd><code>{esc(expected)}</code></dd></div>
            <div><dt>步数 / 超时</dt><dd>{esc(task["policy"]["max_steps"])} steps · {esc(task["policy"]["timeout_seconds"])}s</dd></div>
          </dl>
        </details>
      </article>"""


def profile_payload() -> str:
    payload = {
        key: {
            "label": PROFILE_LABELS[key],
            "weights": value["weights"],
            "pass": value["minimum_pass_score"],
            "minimums": value["minimums"],
        }
        for key, value in PROFILES.items()
    }
    return json.dumps(payload, ensure_ascii=False).replace("</", "<\\/")


def build() -> str:
    tasks = load_tasks()
    difficulty = Counter(task["difficulty"] for task in tasks)
    capabilities = Counter(cap for task in tasks for cap in task["capabilities"])
    task_profiles = Counter(task["evaluation_profile"] for task in tasks)
    tracks = Counter(task["track"] for task in tasks)
    cards = "\n".join(task_card(task) for task in tasks)
    capability_rows = "".join(
        f"<div class='cap-row'><span>{esc(name)}</span><i style='--w:{count / max(capabilities.values()) * 100:.1f}%'></i><b>{count}</b></div>"
        for name, count in capabilities.most_common(12)
    )
    track_rows = "".join(
        f"<li><span><i style='background:{TRACK_COLORS[index]}'></i>{esc(TRACK_LABELS[name])}</span><strong>{tracks[name]}</strong></li>"
        for index, name in enumerate(TRACK_LABELS)
    )
    cumulative = 0
    donut_segments = []
    for color, name in zip(TRACK_COLORS, TRACK_LABELS, strict=True):
        start = cumulative
        cumulative += tracks[name]
        donut_segments.append(f"{color} {start}% {cumulative}%")
    donut_background = "conic-gradient(" + ",".join(donut_segments) + ")"
    profile_buttons = "".join(
        f"<button type='button' data-profile-tab='{esc(name)}' aria-selected='{'true' if i == 0 else 'false'}'>"
        f"{esc(PROFILE_LABELS[name])}<small>{task_profiles[name]} 条已使用</small></button>"
        for i, name in enumerate(PROFILES)
    )
    difficulty_options = "".join(
        f"<option value='{esc(key)}'>{esc(DIFFICULTY_LABELS[key])} · {difficulty[key]}</option>"
        for key in DIFFICULTY_LABELS
    )
    profile_options = "".join(
        f"<option value='{esc(key)}'>{esc(PROFILE_LABELS[key])} · {task_profiles[key]}</option>"
        for key in PROFILES
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="OmniWebBench v0.2 的 100 条可运行测试、六条能力轨道与五套评分模型全貌。">
  <title>OmniWebBench 全貌 · 100 条可运行测试</title>
  <style>
    :root{{--ink:#0b1012;--muted:#5c676b;--line:#dce3e4;--paper:#f4f6f2;--card:#fff;--cyan:#12b8c8;--cyan2:#8ce3e9;--lime:#c9ff5b;--radius:24px}}
    *{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;line-height:1.55}}
    a{{color:inherit}} button,input,select{{font:inherit}} code,.mono,.eyebrow,.task-id{{font-family:"SFMono-Regular",Consolas,monospace}}
    .wrap{{width:min(1180px,calc(100% - 40px));margin:auto}} .topbar{{height:68px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid rgba(11,16,18,.12)}}
    .brand{{font-weight:850;letter-spacing:-.04em;font-size:20px;text-decoration:none}} .brand b{{color:#0a9fad}} .nav{{display:flex;gap:22px;font-size:14px;color:var(--muted)}} .nav a{{text-decoration:none}}
    .hero{{padding:76px 0 48px}} .eyebrow{{font-size:12px;letter-spacing:.12em;text-transform:uppercase;font-weight:700;color:#087d88}} h1{{font-size:clamp(52px,9vw,110px);line-height:.88;letter-spacing:-.075em;max-width:980px;margin:22px 0 32px}}
    h1 em{{font-style:normal;color:#079eae}} .hero-copy{{display:grid;grid-template-columns:1.3fr .7fr;gap:50px;align-items:end}} .hero-copy p{{font-size:20px;max-width:690px;margin:0;color:#344044}} .status-note{{border-left:3px solid var(--cyan);padding-left:18px;font-size:14px;color:var(--muted)}}
    .metrics{{display:grid;grid-template-columns:repeat(4,1fr);background:var(--ink);color:white;border-radius:var(--radius);overflow:hidden;margin:28px auto 80px}} .metric{{padding:28px;border-right:1px solid #303638}} .metric:last-child{{border:0}} .metric strong{{display:block;font-size:48px;line-height:1;letter-spacing:-.06em}} .metric span{{display:block;color:#aeb8ba;margin-top:9px;font-size:13px}}
    section{{padding:76px 0}} .section-head{{display:grid;grid-template-columns:.7fr 1.3fr;gap:40px;margin-bottom:36px;align-items:start}} .section-head h2{{font-size:clamp(38px,5vw,64px);line-height:.98;letter-spacing:-.055em;margin:0}} .section-head p{{color:var(--muted);font-size:18px;max-width:640px;margin:5px 0 0}} .section-kicker{{font:700 12px/1.2 "SFMono-Regular",monospace;color:#078b98;letter-spacing:.1em;text-transform:uppercase;margin-bottom:14px}}
    .scope{{background:#e4f9f9;border:1px solid #a8e3e7;border-radius:20px;padding:22px 24px;display:grid;grid-template-columns:auto 1fr;gap:18px;margin-bottom:32px}} .scope b{{font-size:30px}} .scope p{{margin:0;color:#31575b}} .scope strong{{color:var(--ink)}}
    .coverage{{display:grid;grid-template-columns:.85fr 1.15fr;gap:18px}} .panel{{background:var(--card);border:1px solid var(--line);border-radius:var(--radius);padding:28px}} .panel h3{{margin:0 0 24px;font-size:20px}}
    .difficulty-chart{{display:grid;grid-template-columns:170px 1fr;gap:26px;align-items:center}} .donut{{width:168px;aspect-ratio:1;border-radius:50%;background:{donut_background};position:relative}} .donut:after{{content:"100\\A TESTS";white-space:pre;display:grid;place-items:center;text-align:center;font-weight:800;line-height:1.1;position:absolute;inset:26px;background:white;border-radius:50%}}
    .legend{{list-style:none;padding:0;margin:0}} .legend li{{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px solid #edf0ef}} .legend span{{display:flex;align-items:center;gap:9px;font-size:13px}} .legend i{{width:9px;height:9px;border-radius:50%;background:#10afbe}} .legend i.compositional{{background:#11191b}} .legend i.adversarial{{background:#f37860}} .legend i.visual{{background:#6979db}} .legend i.long_horizon{{background:#d1df36}} .legend i.debug{{background:#df5eb9}}
    .cap-row{{display:grid;grid-template-columns:160px 1fr 24px;gap:12px;align-items:center;margin:11px 0;font:12px "SFMono-Regular",monospace}} .cap-row>i{{height:7px;border-radius:8px;background:#edf1f0;overflow:hidden}} .cap-row>i:after{{content:"";display:block;width:var(--w);height:100%;background:var(--cyan);border-radius:inherit}} .cap-row b{{text-align:right}}
    .dark{{background:var(--ink);color:white}} .dark .section-head p{{color:#aab4b5}} .pipeline{{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;counter-reset:pipe}} .pipe{{border:1px solid #374043;border-radius:18px;padding:20px;min-height:170px;position:relative}} .pipe:before{{counter-increment:pipe;content:"0" counter(pipe);display:block;font:12px monospace;color:var(--cyan2);margin-bottom:28px}} .pipe h3{{font-size:17px;margin:0 0 8px}} .pipe p{{font-size:13px;color:#aab4b5;margin:0}} .truth{{margin-top:18px;border:1px solid #374043;border-radius:20px;padding:22px;display:flex;gap:28px;align-items:center}} .truth-visual{{width:48%;display:flex;align-items:center;gap:7px}} .truth-visual span{{flex:1;padding:14px 7px;border:1px solid #415053;border-radius:9px;text-align:center;font:10px monospace;color:#d8e0e1}} .truth-visual i{{color:var(--cyan);font-style:normal}} .truth p{{color:#b7c0c1;margin:0;flex:1}} .truth strong{{color:white}}
    .profile-layout{{display:grid;grid-template-columns:290px 1fr;gap:18px}} .profile-tabs{{display:flex;flex-direction:column;gap:8px}} .profile-tabs button{{border:1px solid var(--line);background:white;text-align:left;border-radius:14px;padding:14px 16px;cursor:pointer;font-weight:700}} .profile-tabs button small{{display:block;color:var(--muted);font-weight:400;margin-top:3px}} .profile-tabs button[aria-selected=true]{{background:var(--ink);color:white;border-color:var(--ink)}} .profile-tabs button[aria-selected=true] small{{color:#aab4b5}} .profile-view{{background:white;border:1px solid var(--line);border-radius:var(--radius);padding:30px;min-height:350px}} .profile-view h3{{font-size:28px;margin:0}} .pass-score{{display:inline-flex;background:var(--lime);border-radius:99px;padding:6px 12px;font:700 12px monospace;margin:10px 0 26px}} .weights{{display:grid;gap:12px}} .weight{{display:grid;grid-template-columns:140px 1fr 40px;gap:12px;align-items:center;font:13px monospace}} .weight i{{height:12px;background:#e8edeb;border-radius:8px}} .weight i:after{{content:"";display:block;width:var(--weight);height:100%;background:var(--cyan);border-radius:inherit}} .gates{{margin-top:25px;padding:18px;background:#f4f6f2;border-radius:14px}} .gates b{{display:block;margin-bottom:6px}} .gates code{{font-size:12px;color:#526064}}
    .filters{{display:grid;grid-template-columns:1fr 220px 220px;gap:10px;margin:28px 0 14px;position:sticky;top:8px;z-index:4;background:rgba(244,246,242,.92);backdrop-filter:blur(12px);padding:10px;border:1px solid var(--line);border-radius:18px}} .filters input,.filters select{{width:100%;border:1px solid #ccd5d5;background:white;border-radius:11px;padding:12px 14px;color:var(--ink)}} .result-line{{font:12px monospace;color:var(--muted);margin:12px 2px 20px}}
    .task-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}} .task-card{{display:flex;flex-direction:column;background:white;border:1px solid var(--line);border-radius:18px;padding:20px;min-height:330px}} .task-card[hidden]{{display:none}} .task-head{{display:flex;justify-content:space-between;align-items:center}} .task-id{{font-size:11px;color:#687476}} .difficulty{{font:700 10px monospace;padding:5px 8px;border-radius:99px;background:#dff7f8;color:#087d88}} .difficulty.compositional{{background:#e8ebeb;color:#253033}} .difficulty.adversarial{{background:#ffe5df;color:#a52d18}} .difficulty.visual{{background:#e9e9ff;color:#454eaf}} .difficulty.long_horizon{{background:#f1f7c8;color:#536107}} .difficulty.debug{{background:#f9e3f4;color:#922276}} .task-card h3{{font-size:19px;letter-spacing:-.02em;margin:22px 0 10px}} .task-card>p{{font-size:13px;color:var(--muted);margin:0 0 18px;flex:1}} .chips{{display:flex;flex-wrap:wrap;gap:5px}} .chips span{{font:10px monospace;background:#f0f3f2;padding:5px 7px;border-radius:6px}} details{{margin-top:17px;border-top:1px solid #e7ebea;padding-top:13px}} summary{{font-size:12px;font-weight:700;cursor:pointer}} dl{{font-size:11px;margin:12px 0 0}} dl div{{display:grid;grid-template-columns:76px 1fr;gap:8px;margin:7px 0}} dt{{color:var(--muted)}} dd{{margin:0;overflow-wrap:anywhere}} dd code{{font-size:10px}}
    .roadmap{{display:grid;grid-template-columns:1fr 1fr;gap:18px}} .roadmap article{{padding:26px;border-radius:20px;border:1px solid var(--line);background:white}} .roadmap h3{{margin:0 0 18px}} .roadmap ul{{padding-left:20px;color:var(--muted)}} .roadmap .current{{border:2px solid var(--cyan)}} .roadmap .future{{border-style:dashed}} .roadmap small{{font:700 10px monospace;color:#087d88;text-transform:uppercase}}
    footer{{padding:48px 0 60px;border-top:1px solid var(--line);display:flex;justify-content:space-between;gap:30px;color:var(--muted);font-size:13px}} footer b{{color:var(--ink)}}
    @media(max-width:900px){{.hero-copy,.section-head{{grid-template-columns:1fr}}.metrics{{grid-template-columns:1fr 1fr}}.metric:nth-child(2){{border-right:0}}.coverage,.profile-layout{{grid-template-columns:1fr}}.profile-tabs{{display:grid;grid-template-columns:repeat(2,1fr)}}.pipeline{{grid-template-columns:1fr 1fr}}.task-grid{{grid-template-columns:1fr 1fr}}.filters{{grid-template-columns:1fr 1fr}}.filters input{{grid-column:1/-1}}}}
    @media(max-width:620px){{.wrap{{width:min(100% - 24px,1180px)}}.nav{{display:none}}.hero{{padding-top:48px}}h1{{font-size:54px}}.metrics,.coverage,.task-grid,.roadmap{{grid-template-columns:1fr}}.metric{{border-right:0;border-bottom:1px solid #303638}}.difficulty-chart{{grid-template-columns:1fr}}.donut{{margin:auto}}.pipeline{{grid-template-columns:1fr}}.truth{{display:block}}.truth-visual{{width:100%;margin-bottom:18px;gap:3px}}.truth-visual span{{padding:11px 3px;font-size:8px;overflow-wrap:anywhere}}.profile-tabs{{grid-template-columns:1fr}}.filters{{grid-template-columns:1fr;position:static}}.filters input{{grid-column:auto}}footer{{display:block}}}}
    @media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
  </style>
</head>
<body>
  <header class="wrap topbar"><a class="brand" href="#top">OmniWeb<b>Bench</b></a><nav class="nav" aria-label="页面导航"><a href="#coverage">测试构成</a><a href="#scoring">评分</a><a href="#catalog">100 条目录</a><a href="#roadmap">路线图</a></nav></header>
  <main id="top">
    <div class="wrap hero">
      <div class="eyebrow">v0.2 · 100-task public developer preview</div>
      <h1>100 条测试。<br><em>第一阶段，不是终点。</em></h1>
      <div class="hero-copy"><p>不是让模型“说它做完了”，而是用浏览器事件、最终状态、网络记录和可执行 Oracle，验证它到底做了什么。</p><div class="status-note"><strong>当前口径</strong><br>100 条 = 仓库内已经发布且可以运行的 public dev tests；正式规划目标为 1,000 条。</div></div>
    </div>
    <div class="wrap metrics" aria-label="核心数字">
      <div class="metric"><strong>{len(tasks)}</strong><span>可运行 public dev tests</span></div>
      <div class="metric"><strong>{len(capabilities)}</strong><span>唯一能力标签</span></div>
      <div class="metric"><strong>{len(PROFILES)}</strong><span>差异化评分模型</span></div>
      <div class="metric"><strong>{len(tracks)}</strong><span>等比例能力轨道</span></div>
    </div>

    <section class="wrap" id="coverage">
      <div class="section-head"><div><div class="section-kicker">01 / Coverage</div><h2>六条轨道，<br>按目标等比例落地。</h2></div><p>v0.2 从原来的 24 条 smoke pack 扩展到 100 条：基础工作流 25、开放研究 18、状态变更 12、安全恢复 15、文件数据 10、Coding/Debug 20。</p></div>
      <div class="scope"><b>100 / 1,000</b><p><strong>100 条</strong>是当前已经生成、可运行和可计分的第一阶段；原始 130 条真实 query 继续作为母题输入。后续 verified 与隐藏 test split 只有完成审计、重复运行和 baseline 校准后才进入 1,000 条正式目标。</p></div>
      <div class="coverage">
        <div class="panel"><h3>六条测试轨道</h3><div class="difficulty-chart"><div class="donut" role="img" aria-label="100条测试的六轨道分布"></div><ul class="legend">{track_rows}</ul></div></div>
        <div class="panel"><h3>出现频率最高的能力标签</h3>{capability_rows}</div>
      </div>
    </section>

    <section class="dark"><div class="wrap">
      <div class="section-head"><div><div class="section-kicker">02 / Evidence</div><h2>从动作，<br>追到真相。</h2></div><p>每条任务都预先声明 checkpoint。评分器读取标准 run bundle，把轨迹与环境证据交给 Oracle；必要条件、安全门槛和维度最低分全部通过，才会判定成功。</p></div>
      <div class="pipeline"><div class="pipe"><h3>任务定义</h3><p>Intent、能力、策略、环境与评分模型。</p></div><div class="pipe"><h3>真实浏览器执行</h3><p>框架中立：DOM、截图、CDP 或 computer use 均可。</p></div><div class="pipe"><h3>证据包</h3><p>URL、状态、事件、截图、网络、控制台与产物。</p></div><div class="pipe"><h3>确定性 Oracle</h3><p>equals、event、subset、regex、count 等可重放判断。</p></div><div class="pipe"><h3>判定与诊断</h3><p>总分 + hard gates + capability coverage。</p></div></div>
      <div class="truth"><div class="truth-visual" role="img" aria-label="任务、轨迹、证据、Oracle 与评分的关系图"><span>TASK</span><i>→</i><span>TRAJECTORY</span><i>→</i><span>EVIDENCE</span><i>→</i><span>ORACLE</span><i>→</i><span>SCORE</span></div><p><strong>核心原则：</strong>答案文本不能替代环境事实。点击、提交、下载、状态变更和网络修复，必须在对应的可观察证据里成立。</p></div>
    </div></section>

    <section class="wrap" id="scoring">
      <div class="section-head"><div><div class="section-kicker">03 / Scoring</div><h2>不是一把尺子，<br>硬量所有任务。</h2></div><p>不同风险和任务类型使用不同权重。基础点击强调 outcome；状态变更提高结果门槛；调试额外考查 root cause、证据与 patch；开放研究强调约束、来源与新鲜度。</p></div>
      <div class="profile-layout"><div class="profile-tabs" role="tablist" aria-label="评分模型">{profile_buttons}</div><div class="profile-view" id="profile-view" aria-live="polite"></div></div>
    </section>

    <section class="wrap" id="catalog">
      <div class="section-head"><div><div class="section-kicker">04 / Full catalog</div><h2>全部 100 条，<br>没有藏起来。</h2></div><p>搜索 ID、标题、意图或能力标签；也可以按任务形态与评分模型过滤。展开任意卡片，可看到实际 Oracle、期望证据和执行预算。</p></div>
      <div class="filters"><label><span hidden>搜索测试</span><input id="search" type="search" placeholder="搜索：debug、research、safety…"></label><label><span hidden>任务形态</span><select id="difficulty"><option value="">全部任务形态 · 100</option>{difficulty_options}</select></label><label><span hidden>评分模型</span><select id="profile"><option value="">全部评分模型 · 100</option>{profile_options}</select></label></div>
      <div class="result-line" id="result-count">显示 100 / 100 条测试</div>
      <div class="task-grid">{cards}</div>
    </section>

    <section class="wrap" id="roadmap">
      <div class="section-head"><div><div class="section-kicker">05 / Boundary</div><h2>现在有的，<br>和接下来要做的。</h2></div><p>“测试数量”必须绑定可运行状态。路线图里的任务只有经过环境固化、Oracle 审核、重复运行和 baseline 校准后，才会进入正式总数。</p></div>
      <div class="roadmap"><article class="current"><small>shipped · counted</small><h3>v0.2 当前 100 条</h3><ul><li>六轨道严格按 25 / 18 / 12 / 15 / 10 / 20 配额</li><li>100 条任务全部具备确定性 Oracle</li><li>17 条专用研究任务与 20 条 Coding/Debug 任务</li><li>保留原始 24 条 v0.1 pack 供回归比较</li><li>JSON Schema、scorer、fixture、report 与 CI</li></ul></article><article class="future"><small>target · not counted</small><h3>正式目标 1,000 条</h3><ul><li>Public dev 300 条</li><li>Verified 200 条</li><li>Hidden test 500 条</li><li>真实网站、容器化代码仓与视觉参考输入</li><li>多模型 baseline、重复运行与排行榜治理</li></ul></article></div>
    </section>
  </main>
  <footer class="wrap"><div><b>OmniWebBench v0.2.0</b><br>数据由 tasks/core-v0.2.jsonl 生成，避免文档与基准漂移。</div><div><a href="https://github.com/FanXuTheRealOne/OmniWebBench">GitHub repository ↗</a><br>Task data CC BY 4.0 · Code Apache 2.0</div></footer>
  <script>
    const profiles = {profile_payload()};
    const tabs = [...document.querySelectorAll('[data-profile-tab]')];
    const view = document.querySelector('#profile-view');
    const nice = s => s.replaceAll('_',' ');
    function renderProfile(name) {{
      const p = profiles[name];
      view.innerHTML = `<h3>${{p.label}}</h3><span class="pass-score">PASS ≥ ${{p.pass}}</span><div class="weights">${{Object.entries(p.weights).map(([k,v]) => `<div class="weight"><span>${{nice(k)}}</span><i style="--weight:${{v}}%"></i><b>${{v}}%</b></div>`).join('')}}</div><div class="gates"><b>硬门槛（任一不达标即失败）</b><code>${{Object.entries(p.minimums).map(([k,v]) => `${{nice(k)}} ≥ ${{v}}`).join(' · ')}}</code></div>`;
      tabs.forEach(tab => tab.setAttribute('aria-selected', tab.dataset.profileTab === name));
    }}
    tabs.forEach(tab => tab.addEventListener('click', () => renderProfile(tab.dataset.profileTab)));
    renderProfile(tabs[0].dataset.profileTab);
    const cards = [...document.querySelectorAll('.task-card')];
    const search = document.querySelector('#search');
    const difficultySelect = document.querySelector('#difficulty');
    const profileSelect = document.querySelector('#profile');
    function filterTasks() {{
      const query = search.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach(card => {{
        const match = (!query || card.dataset.search.includes(query)) && (!difficultySelect.value || card.dataset.difficulty === difficultySelect.value) && (!profileSelect.value || card.dataset.profile === profileSelect.value);
        card.hidden = !match; if (match) visible++;
      }});
      document.querySelector('#result-count').textContent = `显示 ${{visible}} / ${{cards.length}} 条测试`;
    }}
    [search,difficultySelect,profileSelect].forEach(control => control.addEventListener('input', filterTasks));
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    OUTPUT_PATH.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
