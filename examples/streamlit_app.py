import os
import sys
import streamlit as st
from datetime import datetime

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import DeepSearchAgent, Config

STAGE_PROGRESS = {
    "plan": 10, "structure": 25, "search": 45, "reflection": 65, 
    "report": 85, "review": 95, "save": 100
}

def render_progress_event(event, current_stage_box, progress_bar, timeline_placeholder, detail_placeholder):
    """渲染 Agent 执行进度事件"""
    stage = event.get("stage", "unknown")
    message = event.get("message", "")
    data = event.get("data", {})

    current_stage_box.info(f"当前阶段：{stage} | {message}")
    progress_bar.progress(STAGE_PROGRESS.get(stage, 0))

    if "event_logs" not in st.session_state:
        st.session_state.event_logs = []
    st.session_state.event_logs.append(event)

    # 渲染时间线
    with timeline_placeholder.container():
        st.subheader("Agent 执行时间线")
        recent_logs = st.session_state.event_logs[-30:]
        # reversed 保证最新的在最上面
        for idx, log in enumerate(reversed(recent_logs), 1):
            # idx == 1 是最新的一条，代表正在运行
            status_icon = "🔄" if idx == 1 else "✅"
            st.markdown(f"**{len(recent_logs) - idx + 1}. [{log['stage']}]** {log['message']} {status_icon}")

    # 渲染细节
    with detail_placeholder.container():
        st.subheader("当前步骤细节")
        if stage == "plan":
            goal = data.get("goal", "")
            if goal: st.markdown(f"**研究目标：** {goal}")
        elif stage == "structure":
            paragraphs = data.get("paragraphs", [])
            if paragraphs:
                st.markdown("**报告结构：**")
                for p in paragraphs: st.write(f"- {p['title']}")
        elif stage in ("search", "reflection"):
            if data.get("section_title"): st.markdown(f"**当前段落：** {data['section_title']}")
            if data.get("search_query"): st.markdown(f"**搜索词：** `{data['search_query']}`")
            results = data.get("results", [])
            if results:
                st.markdown("**搜索结果：**")
                for r in results[:3]:
                    st.markdown(f"- **{r.get('title', '无标题')}**")
        elif stage in ("report", "review"):
            preview = data.get("report_preview") or data.get("final_report_preview")
            if preview:
                with st.expander("报告预览", expanded=True): st.write(preview)

def main():
    st.set_page_config(page_title="Deep Search Agent", page_icon="🔍", layout="wide")
    st.title("Deep Search Agent")
    st.markdown("基于 DeepSeek 的可视化深度搜索 Agent")

    with st.sidebar:
        st.header("配置")
        deepseek_key = st.text_input("DeepSeek API Key", type="password")
        tavily_key = st.text_input("Tavily API Key", type="password")
        llm_provider = st.selectbox("LLM提供商", ["deepseek", "openai"])
        
        openai_key = ""
        if llm_provider == "openai":
            openai_key = st.text_input("OpenAI API Key", type="password")
            model_name = st.selectbox("OpenAI模型", ["gpt-4o", "gpt-4o-mini"])
        else:
            model_name = st.selectbox("DeepSeek模型", ["deepseek-chat", "deepseek-reasoner"])
            
        max_reflections = st.slider("反思次数", 1, 5, 2)
        max_search_results = st.slider("搜索结果数", 1, 10, 3)

    query = st.text_area("请输入您要研究的问题", height=100)

    # 核心修复：点击按钮时的严格校验逻辑
    if st.button("开始研究", type="primary", use_container_width=True):
        # 1. 输入校验
        if not query.strip():
            st.error("请输入研究查询内容")
            st.stop() # 强制中断
        if not tavily_key.strip():
            st.error("请提供 Tavily API Key")
            st.stop()
        if llm_provider == "deepseek" and not deepseek_key.strip():
            st.error("请提供 DeepSeek API Key")
            st.stop()
        if llm_provider == "openai" and not openai_key.strip():
            st.error("请提供 OpenAI API Key")
            st.stop()

        # 2. 如果通过校验，执行研究
        config = Config(
            deepseek_api_key=deepseek_key if llm_provider == "deepseek" else None,
            openai_api_key=openai_key if llm_provider == "openai" else None,
            tavily_api_key=tavily_key,
            default_llm_provider=llm_provider,
            deepseek_model=model_name if llm_provider == "deepseek" else "deepseek-chat",
            openai_model=model_name if llm_provider == "openai" else "gpt-4o",
            max_reflections=max_reflections,
            max_search_results=max_search_results
        )
        execute_research(query, config)

def execute_research(query: str, config: Config):
    st.header("执行过程")
    st.session_state.event_logs = []
    
    current_stage_box = st.empty()
    progress_bar = st.progress(0)
    timeline_placeholder = st.empty()
    detail_placeholder = st.empty()

    try:
        agent = DeepSearchAgent(
            config, 
            progress_callback=lambda event: render_progress_event(
                event, current_stage_box, progress_bar, timeline_placeholder, detail_placeholder
            )
        )
        st.session_state.agent = agent
        final_report = agent.research(query, save_report=True)
        current_stage_box.success("研究完成！")
        st.markdown("---")
        st.header("最终报告")
        st.markdown(final_report)
    except Exception as e:
        st.error(f"执行过程中发生错误: {str(e)}")

if __name__ == "__main__":
    main()