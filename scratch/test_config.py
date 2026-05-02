import os
import sys

# 添加 src 目录所在的父目录到 Python 路径
sys.path.insert(0, os.getcwd())

try:
    from src import load_config, Config
    config = load_config()
    print(f"DeepSeek Key: {config.deepseek_api_key}")
    print(f"Tavily Key: {config.tavily_api_key}")
except Exception as e:
    print(f"Error: {e}")
