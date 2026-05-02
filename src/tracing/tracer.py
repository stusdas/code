"""
轻量级 tracing 模块
用于记录 Agent 执行过程中的关键步骤、耗时和上下文信息。
"""

import json
import os
import uuid
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from time import perf_counter
from typing import Any, Dict, Generator, List, Optional


@dataclass
class TraceEvent:
    """单条追踪事件"""
    event: str
    stage: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    duration_ms: Optional[int] = None
    data: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "event": self.event,
            "stage": self.stage,
            "timestamp": self.timestamp,
            "duration_ms": self.duration_ms,
            "data": self.data
        }


class Tracer:
    """研究流程追踪器"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.trace_id = str(uuid.uuid4())
        self.started_at = datetime.now().isoformat()
        self.events: List[TraceEvent] = []
        self.metadata: Dict[str, Any] = {}

    def set_metadata(self, **kwargs):
        """设置 trace 元数据"""
        if not self.enabled:
            return
        self.metadata.update(kwargs)

    def log_event(self, event: str, stage: str, data: Optional[Dict[str, Any]] = None):
        """记录单条事件"""
        if not self.enabled:
            return
        payload = data or {}
        self.events.append(TraceEvent(event=event, stage=stage, data=payload))

    @contextmanager
    def span(self, stage: str, data: Optional[Dict[str, Any]] = None) -> Generator[None, None, None]:
        """
        记录一个有开始/结束的执行区间。
        区间内部抛错会自动记录 error 事件后继续抛出。
        """
        if not self.enabled:
            yield
            return

        start = perf_counter()
        self.log_event("start", stage, data)
        try:
            yield
        except Exception as exc:
            duration_ms = int((perf_counter() - start) * 1000)
            self.events.append(
                TraceEvent(
                    event="error",
                    stage=stage,
                    duration_ms=duration_ms,
                    data={"error": str(exc)}
                )
            )
            raise
        else:
            duration_ms = int((perf_counter() - start) * 1000)
            self.events.append(
                TraceEvent(
                    event="end",
                    stage=stage,
                    duration_ms=duration_ms
                )
            )

    def to_dict(self) -> Dict[str, Any]:
        """导出完整 trace 结构"""
        return {
            "trace_id": self.trace_id,
            "started_at": self.started_at,
            "event_count": len(self.events),
            "metadata": self.metadata,
            "events": [event.to_dict() for event in self.events]
        }

    def save(self, output_dir: str, filename_prefix: str = "trace") -> str:
        """保存 trace 到 JSON 文件"""
        if not self.enabled:
            return ""

        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = os.path.join(output_dir, f"{filename_prefix}_{timestamp}.json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)
        return filepath
