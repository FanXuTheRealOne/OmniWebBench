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
    checkpoint_rows = "".join(
        f"<div><dt>{esc(checkpoint['dimension'])}</dt><dd><code>{esc(checkpoint['oracle']['source'])} · {esc(checkpoint['oracle']['operator'])} · {esc(json.dumps(checkpoint['oracle'].get('expected'), ensure_ascii=False, separators=(',', ':')))}</code></dd></div>"
        for checkpoint in task["checkpoints"]
    )
    return f"""
      <article class="task-card" data-task-id="{esc(task["task_id"])}"
        data-difficulty="{esc(task["difficulty"])}" data-profile="{esc(task["evaluation_profile"])}" data-track="{esc(task["track"])}"
        data-search="{esc(" ".join([task["task_id"], task["title"], task["intent"], task["track"], *task["capabilities"]]).lower())}">
        <div class="task-head">
          <span class="task-id">{esc(task["task_id"])}</span>
          <span class="difficulty {esc(task["difficulty"])}">{esc(DIFFICULTY_LABELS[task["difficulty"]])}</span>
        </div>
        <h3>{esc(task["title"])}</h3>
        <p>{esc(task["intent"])}</p>
        <div class="track-label">{esc(TRACK_LABELS[task["track"]])}</div>
        <div class="chips">{capabilities}</div>
        <details>
          <summary>查看 {len(task["checkpoints"])} 个验收点</summary>
          <dl>
            <div><dt>评分模型</dt><dd>{esc(PROFILE_LABELS[task["evaluation_profile"]])}</dd></div>
            {checkpoint_rows}
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
    track_options = "".join(
        f"<option value='{esc(key)}'>{esc(TRACK_LABELS[key])} · {tracks[key]}</option>"
        for key in TRACK_LABELS
    )
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="OmniWebBench v0.2 的 100 条可运行测试、六条能力轨道与五套评分模型全貌。">
  <title>OmniWebBench 全貌 · 100 条可运行测试</title>
  <style>
    :root{{--ink:#151515;--muted:#5e5a54;--line:#cfc5b5;--paper:#f4efe3;--card:#fffaf0;--blue:#263fbd;--cyan:#159ed1;--red:#d9253f;--orange:#ff5a1f;--green:#149447;--lime:#d5e636;--radius:22px}}
    *{{box-sizing:border-box}} html{{scroll-behavior:smooth}} body{{margin:0;background:var(--paper);color:var(--ink);font-family:Arial,"PingFang SC","Microsoft YaHei",sans-serif;line-height:1.6}}
    a{{color:inherit}} button,input,select{{font:inherit}} code,.mono,.eyebrow,.task-id{{font-family:"SFMono-Regular",Consolas,monospace}} mark{{background:var(--lime);color:var(--ink);padding:.08em .28em;box-decoration-break:clone;-webkit-box-decoration-break:clone}}
    .wrap{{width:min(1220px,calc(100% - 40px));margin:auto}} .topbar{{height:76px;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:20;background:rgba(244,239,227,.94);backdrop-filter:blur(14px);border-bottom:2px solid var(--ink)}}
    .brand{{font-weight:950;letter-spacing:-.06em;font-size:23px;text-decoration:none}} .brand b{{color:var(--blue)}} .nav{{display:flex;gap:20px;font-size:13px;font-weight:800}} .nav a{{text-decoration:none;border-bottom:3px solid transparent}} .nav a:hover,.nav a:focus-visible{{border-color:var(--orange)}}
    .hero{{min-height:700px;margin-top:28px;padding:58px 52px 46px;background:var(--card) url('assets/matisse-botanical.jpg') center/cover no-repeat;border:2px solid var(--ink);border-radius:34px;box-shadow:10px 10px 0 var(--blue);display:flex;flex-direction:column;justify-content:space-between}} .eyebrow{{font-size:12px;letter-spacing:.14em;text-transform:uppercase;font-weight:800;color:var(--blue)}} h1{{font-family:Georgia,"Songti SC",serif;font-size:clamp(58px,8.5vw,116px);line-height:.86;letter-spacing:-.075em;max-width:760px;margin:22px 0 32px}}
    h1 em{{font-style:italic;color:var(--red)}} .hero-copy{{display:grid;grid-template-columns:minmax(0,610px) 300px;gap:28px;align-items:end}} .hero-copy p{{font-size:21px;margin:0;padding:16px 18px;background:rgba(255,250,240,.94);border:2px solid var(--ink)}} .status-note{{background:var(--orange);color:var(--ink);padding:17px 18px;border:2px solid var(--ink);box-shadow:5px 5px 0 var(--ink);font-size:14px}} .hero-actions{{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px}} .hero-actions a{{text-decoration:none;padding:11px 15px;border:2px solid var(--ink);background:var(--card);font-size:13px;font-weight:900;box-shadow:4px 4px 0 var(--ink)}} .hero-actions a:first-child{{background:var(--lime)}}
    .metrics{{display:grid;grid-template-columns:repeat(4,1fr);background:var(--blue);color:white;border:2px solid var(--ink);border-radius:var(--radius);overflow:hidden;margin:34px auto 90px;box-shadow:8px 8px 0 var(--orange)}} .metric{{padding:28px;border-right:2px solid var(--ink)}} .metric:last-child{{border:0}} .metric strong{{display:block;font-family:Georgia,serif;font-style:italic;font-size:54px;line-height:1;letter-spacing:-.06em}} .metric span{{display:block;color:#f5f0e4;margin-top:9px;font-size:13px}}
    section{{padding:82px 0}} .section-head{{display:grid;grid-template-columns:.8fr 1.2fr;gap:50px;margin-bottom:38px;align-items:start}} .section-head h2{{font-family:Georgia,"Songti SC",serif;font-size:clamp(42px,5vw,68px);line-height:.98;letter-spacing:-.055em;margin:0}} .section-head p{{color:var(--muted);font-size:18px;max-width:650px;margin:5px 0 0}} .section-kicker{{font:800 12px/1.2 "SFMono-Regular",monospace;color:var(--red);letter-spacing:.12em;text-transform:uppercase;margin-bottom:14px}}
    .leaf-divider{{height:170px;background:url('assets/matisse-botanical.jpg') center 76%/cover no-repeat;border-top:2px solid var(--ink);border-bottom:2px solid var(--ink)}}
    .scope{{background:var(--lime);border:2px solid var(--ink);border-radius:18px;padding:24px 26px;display:grid;grid-template-columns:auto 1fr;gap:20px;margin-bottom:34px;box-shadow:6px 6px 0 var(--ink)}} .scope b{{font-family:Georgia,serif;font-style:italic;font-size:32px}} .scope p{{margin:0;color:#28271f}} .scope strong{{color:var(--blue)}}
    .coverage{{display:grid;grid-template-columns:.9fr 1.1fr;gap:20px}} .panel{{background:var(--card);border:2px solid var(--ink);border-radius:var(--radius);padding:30px;box-shadow:6px 6px 0 var(--cyan)}} .panel:nth-child(2){{box-shadow:6px 6px 0 var(--green)}} .panel h3{{margin:0 0 24px;font-size:21px}}
    .difficulty-chart{{display:grid;grid-template-columns:170px 1fr;gap:26px;align-items:center}} .donut{{width:168px;aspect-ratio:1;border-radius:50%;background:{donut_background};position:relative;border:2px solid var(--ink)}} .donut:after{{content:"100\\A TESTS";white-space:pre;display:grid;place-items:center;text-align:center;font-weight:900;line-height:1.1;position:absolute;inset:27px;background:var(--card);border:2px solid var(--ink);border-radius:50%}}
    .legend{{list-style:none;padding:0;margin:0}} .legend li{{display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--line)}} .legend span{{display:flex;align-items:center;gap:9px;font-size:13px}} .legend i{{width:11px;height:11px;border-radius:50%}}
    .cap-row{{display:grid;grid-template-columns:170px 1fr 26px;gap:12px;align-items:center;margin:11px 0;font:12px "SFMono-Regular",monospace}} .cap-row>i{{height:10px;border:1px solid var(--ink);background:#e4dccd;overflow:hidden}} .cap-row>i:after{{content:"";display:block;width:var(--w);height:100%;background:var(--red);border-right:1px solid var(--ink)}} .cap-row b{{text-align:right}}
    .dark{{background:var(--blue);color:white;border-top:2px solid var(--ink);border-bottom:2px solid var(--ink)}} .dark .section-head p{{color:#eee8dc}} .dark .section-kicker{{color:var(--lime)}} .pipeline{{display:grid;grid-template-columns:repeat(5,1fr);gap:12px;counter-reset:pipe}} .pipe{{background:#fffaf0;color:var(--ink);border:2px solid var(--ink);border-radius:18px;padding:20px;min-height:180px;box-shadow:5px 5px 0 var(--orange)}} .pipe:before{{counter-increment:pipe;content:"0" counter(pipe);display:block;font:800 12px monospace;color:var(--red);margin-bottom:28px}} .pipe h3{{font-size:17px;margin:0 0 8px}} .pipe p{{font-size:13px;color:var(--muted);margin:0}} .truth{{margin-top:24px;border:2px solid var(--ink);background:#151515;border-radius:20px;padding:24px;display:flex;gap:28px;align-items:center}} .truth-visual{{width:48%;display:flex;align-items:center;gap:7px}} .truth-visual span{{flex:1;padding:14px 7px;border:1px solid #fff;border-radius:9px;text-align:center;font:10px monospace;color:#fff}} .truth-visual i{{color:var(--lime);font-style:normal}} .truth p{{color:#eee8dc;margin:0;flex:1}} .truth strong{{color:white}}
    .guide{{background:#ffe9dd;border-top:2px solid var(--ink);border-bottom:2px solid var(--ink)}} .guide-grid{{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:20px}} .step-card,.important-card,.faq details{{background:var(--card);border:2px solid var(--ink);border-radius:18px;padding:24px}} .step-card{{min-width:0;box-shadow:6px 6px 0 var(--orange)}} .step-card h3,.important-card h3{{font-family:Georgia,serif;font-size:25px;margin:0 0 10px}} .step-card p,.important-card p{{color:var(--muted)}} .step-no{{display:inline-grid;place-items:center;width:35px;height:35px;border-radius:50%;background:var(--blue);color:white;border:2px solid var(--ink);font-weight:900;margin-bottom:18px}} .important-grid{{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px;margin:30px 0}} .important-card:nth-child(1){{box-shadow:6px 6px 0 var(--red)}} .important-card:nth-child(2){{box-shadow:6px 6px 0 var(--green)}} .important-card:nth-child(3){{box-shadow:6px 6px 0 var(--cyan)}}
    .code-block{{position:relative;background:#151515;color:#f8f3e7;border:2px solid var(--ink);border-radius:14px;padding:20px 54px 20px 20px;margin:16px 0;overflow:auto;box-shadow:4px 4px 0 var(--blue)}} .code-block pre{{margin:0;font:12px/1.7 "SFMono-Regular",Consolas,monospace;white-space:pre-wrap}} .copy-btn{{position:absolute;right:9px;top:9px;border:1px solid #fff;background:var(--orange);color:var(--ink);border-radius:8px;padding:6px 9px;font-size:10px;font-weight:800;cursor:pointer}} .copy-btn.copied{{background:var(--green)}} .command-note{{font-size:12px;color:var(--muted)}}
    .profile-layout{{display:grid;grid-template-columns:300px 1fr;gap:20px}} .profile-tabs{{display:flex;flex-direction:column;gap:9px}} .profile-tabs button{{border:2px solid var(--ink);background:var(--card);text-align:left;border-radius:12px;padding:15px 17px;cursor:pointer;font-weight:800}} .profile-tabs button small{{display:block;color:var(--muted);font-weight:400;margin-top:3px}} .profile-tabs button[aria-selected=true]{{background:var(--red);color:white;box-shadow:5px 5px 0 var(--ink)}} .profile-tabs button[aria-selected=true] small{{color:#fff1ec}} .profile-view{{background:var(--card);border:2px solid var(--ink);border-radius:var(--radius);padding:32px;min-height:365px;box-shadow:7px 7px 0 var(--blue)}} .profile-view h3{{font-family:Georgia,serif;font-size:32px;margin:0}} .pass-score{{display:inline-flex;background:var(--lime);border:2px solid var(--ink);border-radius:99px;padding:6px 12px;font:800 12px monospace;margin:10px 0 26px}} .weights{{display:grid;gap:12px}} .weight{{display:grid;grid-template-columns:150px 1fr 42px;gap:12px;align-items:center;font:13px monospace}} .weight i{{height:12px;background:#e5ddce;border:1px solid var(--ink)}} .weight i:after{{content:"";display:block;width:var(--weight);height:100%;background:var(--cyan);border-right:1px solid var(--ink)}} .gates{{margin-top:25px;padding:18px;background:#fff0c4;border:2px solid var(--ink);border-radius:12px}} .gates b{{display:block;margin-bottom:6px}} .gates code{{font-size:12px;color:#4d463b}}
    .filters{{display:grid;grid-template-columns:1.2fr repeat(3,minmax(170px,.55fr));gap:9px;margin:28px 0 14px;position:sticky;top:84px;z-index:10;background:rgba(244,239,227,.95);backdrop-filter:blur(14px);padding:10px;border:2px solid var(--ink);border-radius:16px;box-shadow:5px 5px 0 var(--orange)}} .filters input,.filters select{{width:100%;border:2px solid var(--ink);background:var(--card);border-radius:9px;padding:12px 14px;color:var(--ink)}} .result-line{{font:12px monospace;color:var(--muted);margin:14px 2px 20px}}
    .task-grid{{display:grid;grid-template-columns:repeat(3,1fr);gap:16px}} .task-card{{display:flex;flex-direction:column;background:var(--card);border:2px solid var(--ink);border-radius:16px;padding:20px;min-height:355px;box-shadow:4px 4px 0 #d7cdbd;transition:transform .15s,box-shadow .15s}} .task-card:hover{{transform:translate(-2px,-2px);box-shadow:7px 7px 0 var(--blue)}} .task-card[hidden]{{display:none}} .task-head{{display:flex;justify-content:space-between;align-items:center}} .task-id{{font-size:11px;color:#686058}} .difficulty{{font:800 10px monospace;padding:5px 8px;border:1px solid var(--ink);border-radius:99px;background:#dff7f8;color:#075d72}} .difficulty.compositional{{background:#eee5d5;color:#253033}} .difficulty.adversarial{{background:#ffcec3;color:#8b2416}} .difficulty.visual{{background:#dfe4ff;color:#3546a7}} .difficulty.long_horizon{{background:#eef2a3;color:#505b06}} .difficulty.debug{{background:#f6c9ea;color:#791d63}} .task-card h3{{font-family:Georgia,serif;font-size:21px;line-height:1.15;margin:22px 0 10px}} .task-card>p{{font-size:13px;color:var(--muted);margin:0 0 14px;flex:1}} .track-label{{display:inline-flex;align-self:flex-start;background:var(--blue);color:white;padding:5px 8px;border:1px solid var(--ink);border-radius:6px;font-size:10px;font-weight:800;margin-bottom:10px}} .chips{{display:flex;flex-wrap:wrap;gap:5px}} .chips span{{font:10px monospace;background:#eee5d5;padding:5px 7px;border:1px solid #c8bdad;border-radius:6px}} details{{margin-top:17px;border-top:2px solid var(--ink);padding-top:13px}} summary{{font-size:12px;font-weight:800;cursor:pointer}} dl{{font-size:11px;margin:12px 0 0}} dl div{{display:grid;grid-template-columns:86px 1fr;gap:8px;margin:8px 0}} dt{{color:var(--red);font-weight:800}} dd{{margin:0;overflow-wrap:anywhere}} dd code{{font-size:10px}}
    .roadmap{{display:grid;grid-template-columns:1fr 1fr;gap:20px}} .roadmap article{{padding:28px;border-radius:20px;border:2px solid var(--ink);background:var(--card)}} .roadmap h3{{font-family:Georgia,serif;font-size:28px;margin:0 0 18px}} .roadmap ul{{padding-left:20px;color:var(--muted)}} .roadmap .current{{box-shadow:7px 7px 0 var(--green)}} .roadmap .future{{box-shadow:7px 7px 0 var(--red)}} .roadmap small{{font:800 10px monospace;color:var(--blue);text-transform:uppercase}} .faq{{display:grid;gap:12px}} .faq details{{padding:18px 22px}} .faq summary{{font-size:16px}} .faq p{{color:var(--muted);margin-bottom:0}}
    footer{{padding:50px 0 65px;border-top:2px solid var(--ink);display:flex;justify-content:space-between;gap:30px;color:var(--muted);font-size:13px}} footer b{{color:var(--ink)}}
    @media(max-width:960px){{.hero-copy,.section-head{{grid-template-columns:1fr}}.hero{{background-position:58% center}}.metrics{{grid-template-columns:1fr 1fr}}.metric:nth-child(2){{border-right:0}}.coverage,.profile-layout{{grid-template-columns:1fr}}.profile-tabs{{display:grid;grid-template-columns:repeat(2,1fr)}}.pipeline{{grid-template-columns:1fr 1fr}}.guide-grid,.important-grid{{grid-template-columns:repeat(2,minmax(0,1fr))}}.task-grid{{grid-template-columns:1fr 1fr}}.filters{{grid-template-columns:1fr 1fr}}.filters label:first-child{{grid-column:1/-1}}}}
    @media(max-width:650px){{.wrap{{width:min(100% - 24px,1220px)}}.topbar{{height:64px}}.nav{{display:none}}.hero{{min-height:760px;padding:34px 22px 28px;background-position:64% center;border-radius:24px;box-shadow:6px 6px 0 var(--blue)}}h1{{font-size:55px;max-width:340px}}.hero-copy{{gap:12px}}.hero-copy p{{font-size:17px}}.metrics,.coverage,.task-grid,.roadmap,.guide-grid,.important-grid{{grid-template-columns:minmax(0,1fr)}}.metric{{border-right:0;border-bottom:2px solid var(--ink)}}.difficulty-chart{{grid-template-columns:1fr}}.donut{{margin:auto}}.pipeline{{grid-template-columns:1fr}}.truth{{display:block}}.truth-visual{{width:100%;margin-bottom:18px;gap:3px}}.truth-visual span{{padding:11px 3px;font-size:8px;overflow-wrap:anywhere}}.profile-tabs{{grid-template-columns:1fr}}.filters{{grid-template-columns:1fr;position:static}}.filters label:first-child{{grid-column:auto}}.leaf-divider{{height:120px}}footer{{display:block}}}}
    @media(prefers-reduced-motion:reduce){{html{{scroll-behavior:auto}}}}
  </style>
</head>
<body>
  <header class="wrap topbar"><a class="brand" href="#top">OmniWeb<b>Bench</b></a><nav class="nav" aria-label="页面导航"><a href="#quickstart">快速开始</a><a href="#integration">接入 Agent</a><a href="#scoring">评分</a><a href="#debug-track">Debug</a><a href="#catalog">100 条目录</a></nav></header>
  <main id="top">
    <div class="wrap hero">
      <div class="eyebrow">v0.2 · 100-task public developer preview</div>
      <h1>100 条测试。<br><em>第一阶段，<br>不是终点。</em></h1>
      <div><div class="hero-copy"><p>不是让模型“说它做完了”，而是用浏览器事件、最终状态、网络记录和可执行 Oracle，验证它到底做了什么。</p><div class="status-note"><strong>当前口径</strong><br>100 条 = 仓库内已经发布且可以运行的 public dev tests；正式规划目标为 1,000 条。</div></div><div class="hero-actions"><a href="#quickstart">五分钟跑起来</a><a href="#catalog">浏览全部任务</a><a href="https://github.com/FanXuTheRealOne/OmniWebBench">查看 GitHub</a></div></div>
    </div>
    <div class="wrap metrics" aria-label="核心数字">
      <div class="metric"><strong>{len(tasks)}</strong><span>可运行 public dev tests</span></div>
      <div class="metric"><strong>{len(capabilities)}</strong><span>唯一能力标签</span></div>
      <div class="metric"><strong>{len(PROFILES)}</strong><span>差异化评分模型</span></div>
      <div class="metric"><strong>{len(tracks)}</strong><span>等比例能力轨道</span></div>
    </div>

    <div class="leaf-divider" role="img" aria-label="彩色剪纸植物装饰"></div>

    <section class="guide" id="quickstart"><div class="wrap">
      <div class="section-head"><div><div class="section-kicker">00 / Start here</div><h2>从零开始，<br>五分钟拿到第一条分数。</h2></div><p>OmniWebBench 不绑定 Playwright、Selenium、Computer Use 或任何特定 Agent 框架。你的 Agent 只需要打开任务 URL、完成网页操作，然后写出标准 run bundle。</p></div>
      <div class="important-grid">
        <article class="important-card"><h3>用对任务包</h3><p>当前主版本是 <mark>tasks/core-v0.2.jsonl</mark>，包含 100 条任务。v0.1 只保留作 24 条历史回归集。</p></article>
        <article class="important-card"><h3>不要偷看答案</h3><p>Agent 在执行期间<mark>不能读取 event ledger、任务源码或 Oracle</mark>。这些只属于评测器信任区。</p></article>
        <article class="important-card"><h3>答案不等于完成</h3><p>提交文字“已完成”不会得分。必须同时保留<mark>轨迹、最终 URL、截图与环境事件</mark>。</p></article>
      </div>
      <div class="guide-grid">
        <article class="step-card"><span class="step-no">1</span><h3>克隆并安装</h3><p>需要 Python 3.11 或更高版本。开发依赖会安装 schema 校验、测试与格式检查工具。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>git clone https://github.com/FanXuTheRealOne/OmniWebBench.git
cd OmniWebBench
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'</pre></div></article>
        <article class="step-card"><span class="step-no">2</span><h3>检查环境</h3><p><code>doctor</code> 会确认版本、默认任务包和五套评分模型；<code>list</code> 用于查看 100 条任务。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>omniwebbench doctor
omniwebbench list
omniwebbench show owb-dev-092</pre></div></article>
        <article class="step-card"><span class="step-no">3</span><h3>启动可观察网页</h3><p>Fixture 是一个正常网页，同时在评测器侧记录可验证事件。保持这个终端运行。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>omniwebbench serve-fixture --port 8765</pre></div><p class="command-note">默认地址为 http://127.0.0.1:8765，仅在本机使用。</p></article>
        <article class="step-card"><span class="step-no">4</span><h3>先验证任务包</h3><p>运行前锁定任务版本，避免 Agent、任务和评分器之间出现版本漂移。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>omniwebbench validate tasks/core-v0.2.jsonl</pre></div></article>
        <article class="step-card"><span class="step-no">5</span><h3>让 Agent 执行</h3><p>为每次运行生成唯一 RUN_ID，并把任务 URL 里的两个占位符替换为真实值。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>{{{{FIXTURE_URL}}}} → http://127.0.0.1:8765
{{{{RUN_ID}}}}      → your-unique-run-id</pre></div></article>
        <article class="step-card"><span class="step-no">6</span><h3>计分并生成报告</h3><p>Agent 写出 run bundle 后，先计分，再生成可复查的 JSON 与独立 HTML 报告。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>omniwebbench score runs/my-run.json
omniwebbench report runs/my-run.json --output-dir reports/my-run
open reports/my-run/index.html</pre></div></article>
      </div>
    </div></section>

    <section class="wrap" id="integration">
      <div class="section-head"><div><div class="section-kicker">01 / Agent integration</div><h2>你的 Agent，<br>到底要交什么。</h2></div><p>评测器不关心 Agent 内部使用了什么模型或工具；它只关心输入任务、浏览器执行过程和最终证据是否满足统一协议。</p></div>
      <div class="scope"><b>关键边界</b><p><strong>Agent 只看网页和用户任务。</strong>Fixture 的 <code>/api/runs/*</code>、任务 JSON 中的 checkpoint、评分代码和参考证据都必须与 Agent 隔离，否则结果无效。</p></div>
      <div class="guide-grid">
        <article class="step-card"><span class="step-no">A</span><h3>读取任务合同</h3><p>每条任务给出 intent、能力标签、起始 URL、步数与超时预算、允许的副作用范围。Adapter 负责把这些字段转换成你们 Agent 的输入。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>{{
  "task_id": "owb-dev-092",
  "intent": "Inspect, patch and validate…",
  "environment": {{"mode": "deterministic_fixture"}},
  "policy": {{"max_steps": 40, "timeout_seconds": 180}}
}}</pre></div></article>
        <article class="step-card"><span class="step-no">B</span><h3>写标准 Run Bundle</h3><p><mark>task_id、benchmark_version 和 run_id 必须一致</mark>。trajectory 记录动作；evidence 保存网页环境能够证明的事实。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>{{
  "task_id": "owb-dev-092",
  "benchmark_version": "0.2.0",
  "run_id": "agent-a-092-r1",
  "status": "completed",
  "answer": "root cause + evidence + visual result",
  "trajectory": [{{"action": "click", "target": "Run validation"}}],
  "evidence": {{
    "final_url": "http://127.0.0.1:8765/lab?...",
    "screenshots": ["final.png"],
    "server_events": [{{"name": "patch-validated"}}],
    "network": [], "console": [], "artifacts": []
  }}
}}</pre></div></article>
      </div>
    </section>

    <section class="wrap" id="coverage">
      <div class="section-head"><div><div class="section-kicker">02 / Coverage</div><h2>六条轨道，<br>按目标等比例落地。</h2></div><p>v0.2 从原来的 24 条 smoke pack 扩展到 100 条：基础工作流 25、开放研究 18、状态变更 12、安全恢复 15、文件数据 10、Coding/Debug 20。</p></div>
      <div class="scope"><b>100 / 1,000</b><p><strong>100 条</strong>是当前已经生成、可运行和可计分的第一阶段；原始 130 条真实 query 继续作为母题输入。后续 verified 与隐藏 test split 只有完成审计、重复运行和 baseline 校准后才进入 1,000 条正式目标。</p></div>
      <div class="coverage">
        <div class="panel"><h3>六条测试轨道</h3><div class="difficulty-chart"><div class="donut" role="img" aria-label="100条测试的六轨道分布"></div><ul class="legend">{track_rows}</ul></div></div>
        <div class="panel"><h3>出现频率最高的能力标签</h3>{capability_rows}</div>
      </div>
    </section>

    <section class="dark"><div class="wrap">
      <div class="section-head"><div><div class="section-kicker">03 / Evidence</div><h2>从动作，<br>追到真相。</h2></div><p>每条任务都预先声明 checkpoint。评分器读取标准 run bundle，把轨迹与环境证据交给 Oracle；必要条件、安全门槛和维度最低分全部通过，才会判定成功。</p></div>
      <div class="pipeline"><div class="pipe"><h3>任务定义</h3><p>Intent、能力、策略、环境与评分模型。</p></div><div class="pipe"><h3>真实浏览器执行</h3><p>框架中立：DOM、截图、CDP 或 computer use 均可。</p></div><div class="pipe"><h3>证据包</h3><p>URL、状态、事件、截图、网络、控制台与产物。</p></div><div class="pipe"><h3>确定性 Oracle</h3><p>equals、event、subset、regex、count 等可重放判断。</p></div><div class="pipe"><h3>判定与诊断</h3><p>总分 + hard gates + capability coverage。</p></div></div>
      <div class="truth"><div class="truth-visual" role="img" aria-label="任务、轨迹、证据、Oracle 与评分的关系图"><span>TASK</span><i>→</i><span>TRAJECTORY</span><i>→</i><span>EVIDENCE</span><i>→</i><span>ORACLE</span><i>→</i><span>SCORE</span></div><p><strong>核心原则：</strong>答案文本不能替代环境事实。点击、提交、下载、状态变更和网络修复，必须在对应的可观察证据里成立。</p></div>
    </div></section>

    <section class="guide" id="debug-track"><div class="wrap">
      <div class="section-head"><div><div class="section-kicker">04 / Coding & Debug</div><h2>搜网页、看现场、<br>找到根因，再修好。</h2></div><p>这是 OmniWebBench 面向艺术平台 Coding Agent 的专项轨道。它不只测“会不会写代码”，而是测 Agent 能否从浏览器可见故障出发，结合页面、Network、Console 和视觉结果形成闭环。</p></div>
      <div class="scope"><b>20 条专项</b><p><strong>owb-dev-082–091</strong> 测浏览器诊断；<strong>owb-dev-092–100</strong> 测代码修改与视觉回归；再加原始网络故障任务 owb-dev-024。<mark>必须给出 root cause + decisive evidence + validated result</mark>。</p></div>
      <div class="guide-grid">
        <article class="step-card"><span class="step-no">1</span><h3>观察失败现场</h3><p>先打开实际页面，记录错误状态和复现路径。禁止只根据任务文字猜测根因。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>omniwebbench show owb-dev-092
omniwebbench list --capability web_debugging</pre></div></article>
        <article class="step-card"><span class="step-no">2</span><h3>采集浏览器证据</h3><p>诊断任务要求读取 Network 或 Console 中的决定性信号，例如 403 preflight、CSP、429、缓存版本或 WebSocket 升级失败。</p><p><mark>不要通过关闭安全策略“修好”页面。</mark></p></article>
        <article class="step-card"><span class="step-no">3</span><h3>修改并重新验证</h3><p>补丁任务必须执行测试按钮并产生 <code>patch-validated</code> 事件。只提交代码片段、没有重新跑浏览器验证，结果仍然失败。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>FAIL → inspect → edit → rerun
PASS → capture screenshot → write run bundle</pre></div></article>
        <article class="step-card"><span class="step-no">4</span><h3>回答结构</h3><p>最终回答建议固定成三段，便于人工审计和自动 Oracle 同时判断。</p><div class="code-block"><button class="copy-btn" type="button" data-copy>复制</button><pre>Root cause: …
Evidence: Network/Console/DOM …
Validated result: visual check / test result …</pre></div></article>
      </div>
      <div class="important-grid">
        <article class="important-card"><h3>Browser Debug</h3><p>权重集中在 outcome 40%、root cause 25% 和 evidence 15%。适合测“看懂故障”的能力。</p></article>
        <article class="important-card"><h3>Web Debug</h3><p>同时考查 patch、grounding 和 visual。适合你们“艺术平台 + Coding Agent”的特殊形态。</p></article>
        <article class="important-card"><h3>下一阶段</h3><p>当前是确定性浏览器 fixture；后续将升级到<mark>真实 repo + 启动服务 + 浏览器复现 + 自动测试</mark>。</p></article>
      </div>
    </div></section>

    <div class="leaf-divider" role="img" aria-label="彩色剪纸植物装饰"></div>

    <section class="wrap" id="scoring">
      <div class="section-head"><div><div class="section-kicker">05 / Scoring</div><h2>不是一把尺子，<br>硬量所有任务。</h2></div><p>不同风险和任务类型使用不同权重。基础点击强调 outcome；状态变更提高结果门槛；调试额外考查 root cause、证据与 patch；开放研究强调约束、来源与新鲜度。</p></div>
      <div class="profile-layout"><div class="profile-tabs" role="tablist" aria-label="评分模型">{profile_buttons}</div><div class="profile-view" id="profile-view" aria-live="polite"></div></div>
    </section>

    <section class="wrap" id="catalog">
      <div class="section-head"><div><div class="section-kicker">06 / Full catalog</div><h2>全部 100 条，<br>没有藏起来。</h2></div><p>搜索 ID、标题、意图或能力标签；也可以按轨道、任务形态与评分模型过滤。展开任意卡片，可看到全部 Oracle、预期证据和执行预算。</p></div>
      <div class="filters"><label><span hidden>搜索测试</span><input id="search" type="search" placeholder="搜索：debug、research、safety…"></label><label><span hidden>测试轨道</span><select id="track"><option value="">全部测试轨道 · 100</option>{track_options}</select></label><label><span hidden>任务形态</span><select id="difficulty"><option value="">全部任务形态 · 100</option>{difficulty_options}</select></label><label><span hidden>评分模型</span><select id="profile"><option value="">全部评分模型 · 100</option>{profile_options}</select></label></div>
      <div class="result-line" id="result-count">显示 100 / 100 条测试</div>
      <div class="task-grid">{cards}</div>
    </section>

    <section class="wrap" id="roadmap">
      <div class="section-head"><div><div class="section-kicker">07 / Boundary</div><h2>现在有的，<br>和接下来要做的。</h2></div><p>“测试数量”必须绑定可运行状态。路线图里的任务只有经过环境固化、Oracle 审核、重复运行和 baseline 校准后，才会进入正式总数。</p></div>
      <div class="roadmap"><article class="current"><small>shipped · counted</small><h3>v0.2 当前 100 条</h3><ul><li>六轨道严格按 25 / 18 / 12 / 15 / 10 / 20 配额</li><li>100 条任务全部具备确定性 Oracle</li><li>17 条专用研究任务与 20 条 Coding/Debug 任务</li><li>保留原始 24 条 v0.1 pack 供回归比较</li><li>JSON Schema、scorer、fixture、report 与 CI</li></ul></article><article class="future"><small>target · not counted</small><h3>正式目标 1,000 条</h3><ul><li>Public dev 300 条</li><li>Verified 200 条</li><li>Hidden test 500 条</li><li>真实网站、容器化代码仓与视觉参考输入</li><li>多模型 baseline、重复运行与排行榜治理</li></ul></article></div>
    </section>

    <section class="wrap" id="faq">
      <div class="section-head"><div><div class="section-kicker">08 / FAQ</div><h2>跑之前，<br>最常见的几个问题。</h2></div><p>这里解释任务数量、运行成本、重复次数、失败状态和公平比较口径。更完整的协议仍以仓库 docs 与 schema 为准。</p></div>
      <div class="faq">
        <details><summary>100 条需要一次全部跑完吗？</summary><p>不需要。开发阶段先用 <code>--capability</code> 或任务 ID 做小范围回归；准备发布 Agent 版本时，再跑完整 100 条。正式排行榜会按固定任务包和重复次数执行。</p></details>
        <details><summary>为什么有些任务要重复两次？</summary><p>对抗、安全、长链路和 Debug 更容易受偶然因素影响。repeat_count 用于暴露可靠性，而不是让 Agent 不断重试直到成功。</p></details>
        <details><summary>Agent 能直接调用 fixture API 吗？</summary><p><mark>不能。</mark>Agent 只能操作网页。事件 API 和 ledger 属于评测器信任区；直接读取它们等同于访问答案。</p></details>
        <details><summary>什么情况不计分？</summary><p><code>infra_invalid</code>、<code>task_invalid</code> 和 <code>waiting_human</code> 会进入 invalid，不混入成功率。安全违规则不是 invalid，而是明确失败。</p></details>
        <details><summary>不同浏览器 Agent 可以比较吗？</summary><p>可以，但必须披露模型、harness、观察模式、动作空间、重试策略、浏览器版本、成本和人工介入。主要排行榜只接受可复现或官方验证结果。</p></details>
        <details><summary>当前 100 条和最终 1,000 条是什么关系？</summary><p>当前 100 条是确定性 public dev pack，用于开发和诊断。后续 900 条将引入真实网站、容器化状态、repo-to-browser Debug、视觉参考输入以及 verified/hidden split。</p></details>
      </div>
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
    const trackSelect = document.querySelector('#track');
    const difficultySelect = document.querySelector('#difficulty');
    const profileSelect = document.querySelector('#profile');
    function filterTasks() {{
      const query = search.value.trim().toLowerCase();
      let visible = 0;
      cards.forEach(card => {{
        const match = (!query || card.dataset.search.includes(query)) && (!trackSelect.value || card.dataset.track === trackSelect.value) && (!difficultySelect.value || card.dataset.difficulty === difficultySelect.value) && (!profileSelect.value || card.dataset.profile === profileSelect.value);
        card.hidden = !match; if (match) visible++;
      }});
      document.querySelector('#result-count').textContent = `显示 ${{visible}} / ${{cards.length}} 条测试`;
    }}
    [search,trackSelect,difficultySelect,profileSelect].forEach(control => control.addEventListener('input', filterTasks));
    document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {{
      const content = button.parentElement.querySelector('pre').textContent;
      try {{ await navigator.clipboard.writeText(content); }} catch {{
        const area = document.createElement('textarea'); area.value = content; document.body.appendChild(area); area.select(); document.execCommand('copy'); area.remove();
      }}
      button.textContent = '已复制'; button.classList.add('copied');
      setTimeout(() => {{ button.textContent = '复制'; button.classList.remove('copied'); }}, 1400);
    }}));
  </script>
</body>
</html>
"""


if __name__ == "__main__":
    OUTPUT_PATH.write_text(build(), encoding="utf-8")
    print(f"wrote {OUTPUT_PATH.relative_to(ROOT)}")
