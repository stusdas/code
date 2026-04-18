"""
Streamlit Web界面

为 Deep Search Agent 提供友好的 Web 界面
"""

import os
import sys
import streamlit as st
from datetime import datetime

# 添加 src 目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src import DeepSearchAgent, Config


def main():
    """主函数"""
    st.set_page_config(
        page_title="Deep Search Agent",
        page_icon="🔎",
        layout="wide",
    )

    st.title("Deep Search Agent")
    st.markdown("基于 DeepSearchAgent 的研究报告生成界面")

    # 侧边栏配置
    with st.sidebar:
        st.header("配置")

        # API 密钥配置
        st.subheader("API 密钥")
        deepseek_key = st.text_input("DeepSeek API Key", type="password", value="")
        tavily_key = st.text_input("Tavily API Key", type="password", value="")

        # 高级配置
        st.subheader("高级配置")
        max_reflections = st.slider("反思次数", 1, 5, 2)
        max_search_results = st.slider("搜索结果数", 1, 10, 3)
        max_content_length = st.number_input("最大内容长度", 1000, 50000, 20000)

        # 模型选择
        llm_provider = st.selectbox("LLM 提供商", ["deepseek", "openai"])
        if llm_provider == "deepseek":
            model_name = st.selectbox("DeepSeek 模型", ["deepseek-chat"])
            openai_key = ""
        else:
            model_name = st.selectbox("OpenAI 模型", ["gpt-4o-mini", "gpt-4o"])
            openai_key = st.text_input("OpenAI API Key", type="password", value="")

    # 主界面
    col1, col2 = st.columns([2, 1])

    with col1:
        st.header("研究查询")
        query = st.text_area(
            "请输入您要研究的问题",
            placeholder="例如：2025年人工智能发展趋势",
            height=100,
        )

        st.subheader("示例查询")
        example_queries = [
            "2025年人工智能发展趋势",
            "深度学习在医疗领域的应用",
            "区块链技术的最新发展",
            "可持续能源技术趋势",
            "量子计算的发展现状",
        ]
        selected_example = st.selectbox("选择示例查询", ["自定义"] + example_queries)
        if selected_example != "自定义":
            query = selected_example

    with col2:
        st.header("状态信息")
        if "agent" in st.session_state and hasattr(st.session_state.agent, "state"):
            progress = st.session_state.agent.get_progress_summary()
            st.metric("总段落数", progress["total_paragraphs"])
            st.metric("已完成", progress["completed_paragraphs"])
            st.progress(progress["progress_percentage"] / 100)
        else:
            st.info("尚未开始研究")

    # 执行按钮
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
    with col_btn2:
        start_research = st.button("开始研究", type="primary", use_container_width=True)

    if start_research:
        if not query.strip():
            st.error("请输入研究查询")
            return

        if llm_provider == "deepseek" and not deepseek_key:
            st.error("请提供 DeepSeek API Key")
            return

        if not tavily_key:
            st.error("请提供 Tavily API Key")
            return

        if llm_provider == "openai" and not openai_key:
            st.error("请提供 OpenAI API Key")
            return

        config = Config(
            deepseek_api_key=deepseek_key if llm_provider == "deepseek" else None,
            openai_api_key=openai_key if llm_provider == "openai" else None,
            tavily_api_key=tavily_key,
            default_llm_provider=llm_provider,
            deepseek_model=model_name if llm_provider == "deepseek" else "deepseek-chat",
            openai_model=model_name if llm_provider == "openai" else "gpt-4o-mini",
            max_reflections=max_reflections,
            max_search_results=max_search_results,
            max_content_length=max_content_length,
            output_dir="streamlit_reports",
        )

        execute_research(query, config)


def execute_research(query: str, config: Config):
    """执行研究"""
    try:
        progress_bar = st.progress(0)
        status_text = st.empty()

        status_text.text("正在初始化 Agent...")
        agent = DeepSearchAgent(config)
        st.session_state.agent = agent
        progress_bar.progress(10)

        status_text.text("正在执行完整研究流程...")
        progress_bar.progress(30)

        final_report = agent.research(query, save_report=True)

        progress_bar.progress(100)
        status_text.text("研究完成！")

        display_results(agent, final_report)

    except Exception as e:
        st.error(f"研究过程中发生错误: {str(e)}")


def display_results(agent: DeepSearchAgent, final_report: str):
    """显示研究结果"""
    st.header("研究结果")

    tab1, tab2, tab3, tab4 = st.tabs(["最终报告", "详细信息", "下载", "Tracing"])

    with tab1:
        st.markdown(final_report)

    with tab2:
        st.subheader("段落详情")
        for i, paragraph in enumerate(agent.state.paragraphs):
            with st.expander(f"段落 {i + 1}: {paragraph.title}"):
                st.write("**预期内容：**", paragraph.content)

                latest_summary = getattr(paragraph.research, "latest_summary", "") or ""
                if latest_summary:
                    display_summary = (
                        latest_summary[:300] + "..."
                        if len(latest_summary) > 300
                        else latest_summary
                    )
                    st.write("**最终内容：**", display_summary)
                else:
                    st.write("**最终内容：** 暂无")

                st.write("**搜索次数：**", paragraph.research.get_search_count())
                st.write("**反思次数：**", paragraph.research.reflection_iteration)

        st.subheader("搜索历史")
        all_searches = []
        for paragraph in agent.state.paragraphs:
            all_searches.extend(paragraph.research.search_history)

        if all_searches:
            for i, search in enumerate(all_searches):
                title = getattr(search, "query", f"搜索 {i + 1}")
                with st.expander(f"搜索 {i + 1}: {title}"):
                    if getattr(search, "url", None):
                        st.write("**URL：**", search.url)
                    if getattr(search, "title", None):
                        st.write("**标题：**", search.title)
                    if getattr(search, "content", None):
                        preview = (
                            search.content[:200] + "..."
                            if len(search.content) > 200
                            else search.content
                        )
                        st.write("**内容预览：**", preview)
                    if getattr(search, "score", None) is not None:
                        st.write("**相关度评分：**", search.score)
        else:
            st.info("暂无搜索历史")

    with tab3:
        st.subheader("下载报告")

        st.download_button(
            label="下载 Markdown 报告",
            data=final_report,
            file_name=f"deep_search_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md",
            mime="text/markdown",
        )

        state_json = agent.state.to_json()
        st.download_button(
            label="下载状态文件",
            data=state_json,
            file_name=f"deep_search_state_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

    with tab4:
        st.subheader("Tracing 文件")

        tracing_dir = getattr(agent, "tracing_output_dir", None)

        if tracing_dir and os.path.exists(tracing_dir):
            trace_files = sorted(
                [
                    f
                    for f in os.listdir(tracing_dir)
                    if f.endswith(".json") or f.endswith(".html")
                ],
                reverse=True,
            )

            if trace_files:
                st.write("最近生成的 tracing 文件：")
                for filename in trace_files[:10]:
                    full_path = os.path.join(tracing_dir, filename)
                    st.write(f"- {filename}")

                    with open(full_path, "rb") as f:
                        st.download_button(
                            label=f"下载 {filename}",
                            data=f.read(),
                            file_name=filename,
                            mime="text/html"
                            if filename.endswith(".html")
                            else "application/json",
                            key=f"trace_download_{filename}",
                        )
            else:
                st.info("当前没有 tracing 文件")
        else:
            st.info("Tracing 目录不存在")


if __name__ == "__main__":
    main()