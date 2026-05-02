"""
Trace 可视化：生成简单 HTML 流程图
"""

import html
import json
import os
from datetime import datetime
from typing import Any, Dict, List


def _load_trace(trace_path: str) -> Dict[str, Any]:
    with open(trace_path, "r", encoding="utf-8") as f:
        return json.load(f)


def _format_data(data: Dict[str, Any]) -> str:
    if not data:
        return ""
    return "<br>".join(
        f"<span class='key'>{html.escape(str(k))}</span>: {html.escape(str(v))}"
        for k, v in data.items()
    )


def generate_trace_html(trace_path: str, output_path: str = "") -> str:
    """
    将 trace json 渲染为简单 HTML 文件。

    Args:
        trace_path: trace json 路径
        output_path: 输出 html 路径（可选）

    Returns:
        生成后的 html 文件路径
    """
    trace = _load_trace(trace_path)
    events: List[Dict[str, Any]] = trace.get("events", [])
    metadata: Dict[str, Any] = trace.get("metadata", {})
    trace_id = trace.get("trace_id", "")
    started_at = trace.get("started_at", "")
    event_count = trace.get("event_count", len(events))

    if not output_path:
        base, _ = os.path.splitext(trace_path)
        output_path = f"{base}.html"

    event_blocks = []
    for index, event in enumerate(events, start=1):
        cls = html.escape(event.get("event", "info"))
        stage = html.escape(event.get("stage", "unknown"))
        timestamp = html.escape(event.get("timestamp", ""))
        duration_ms = event.get("duration_ms")
        duration_text = f"{duration_ms} ms" if duration_ms is not None else "-"
        data_html = _format_data(event.get("data", {}))
        event_blocks.append(
            f"""
            <div class="event {cls}">
              <div class="row">
                <div class="idx">#{index}</div>
                <div class="stage">{stage}</div>
                <div class="etype">{cls.upper()}</div>
              </div>
              <div class="meta">
                <span>time: {timestamp}</span>
                <span>duration: {duration_text}</span>
              </div>
              {"<div class='data'>" + data_html + "</div>" if data_html else ""}
            </div>
            """
        )

    metadata_html = _format_data(metadata)
    now = datetime.now().isoformat()
    html_content = f"""<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width,initial-scale=1" />
  <title>Research Trace Flow</title>
  <style>
    body {{
      font-family: Arial, sans-serif;
      margin: 24px;
      background: #f5f7fb;
      color: #222;
    }}
    .card {{
      background: #fff;
      border: 1px solid #e6eaf2;
      border-radius: 10px;
      padding: 16px;
      margin-bottom: 16px;
    }}
    .title {{ font-size: 20px; margin: 0 0 8px; }}
    .sub {{ color: #666; font-size: 13px; }}
    .timeline {{
      display: flex;
      flex-direction: column;
      gap: 10px;
    }}
    .event {{
      border: 1px solid #e3e7ef;
      border-left: 5px solid #8ca2ff;
      border-radius: 8px;
      padding: 10px 12px;
      background: #fff;
    }}
    .event.start {{ border-left-color: #3b82f6; }}
    .event.end {{ border-left-color: #16a34a; }}
    .event.error {{ border-left-color: #dc2626; }}
    .event.warn {{ border-left-color: #d97706; }}
    .row {{
      display: flex;
      align-items: center;
      gap: 10px;
    }}
    .idx {{ font-weight: bold; width: 34px; color: #666; }}
    .stage {{ font-weight: 600; flex: 1; }}
    .etype {{
      font-size: 12px;
      color: #334155;
      border: 1px solid #cbd5e1;
      border-radius: 999px;
      padding: 2px 8px;
      background: #f8fafc;
    }}
    .meta {{
      margin-top: 6px;
      display: flex;
      gap: 14px;
      color: #667085;
      font-size: 12px;
    }}
    .data {{
      margin-top: 8px;
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 8px;
      font-size: 12px;
      line-height: 1.5;
    }}
    .key {{ color: #475569; font-weight: 600; }}
  </style>
</head>
<body>
  <div class="card">
    <h1 class="title">Research Trace Flow</h1>
    <div class="sub">generated_at: {html.escape(now)}</div>
    <div class="sub">trace_id: {html.escape(trace_id)}</div>
    <div class="sub">started_at: {html.escape(started_at)}</div>
    <div class="sub">event_count: {event_count}</div>
    {"<div class='data' style='margin-top:10px'>" + metadata_html + "</div>" if metadata_html else ""}
  </div>

  <div class="card">
    <h2 class="title" style="font-size:18px">Timeline</h2>
    <div class="timeline">
      {"".join(event_blocks) if event_blocks else "<div class='sub'>No events found.</div>"}
    </div>
  </div>
</body>
</html>
"""

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    return output_path
