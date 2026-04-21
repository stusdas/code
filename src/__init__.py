"""
Deep Search Agent
一个无框架的深度搜索AI代理实现
"""

from .agent import DeepSearchAgent, create_agent
from .tracing import Tracer, generate_trace_html
from .utils.config import Config, load_config

__version__ = "1.0.0"
__author__ = "Deep Search Agent Team"

__all__ = ["DeepSearchAgent", "create_agent", "Tracer", "generate_trace_html", "Config", "load_config"]
