# Deep Search Agent 配置文件
# 请在这里填入您的API密钥

# DeepSeek API Key
DEEPSEEK_API_KEY = "sk-88f13750cdce483ba1c2d7444781dba1"

# OpenAI API Key (可选)
OPENAI_API_KEY = "your_openai_api_key_here"

# Tavily搜索API Key
TAVILY_API_KEY = "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"

# 配置参数
DEFAULT_LLM_PROVIDER = "deepseek"
DEEPSEEK_MODEL = "deepseek-chat"
OPENAI_MODEL = "gpt-4o-mini"

MAX_REFLECTIONS = 2
SEARCH_RESULTS_PER_QUERY = 3
SEARCH_CONTENT_MAX_LENGTH = 20000
OUTPUT_DIR = "reports"
SAVE_INTERMEDIATE_STATES = True
ENABLE_TRACING = True
TRACING_SUBDIR = "traces"
