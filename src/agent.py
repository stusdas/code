"""
Deep Search Agent主类 —— Plan-and-Review 版本
新增：_make_research_plan（研究施工图）+ _global_review（全文总审）
plan 贯穿所有子流程，搜索由"盲搜"升级为"按计划搜"
"""

import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any, List

from .llms import DeepSeekLLM, OpenAILLM, BaseLLM
from .nodes import (
    ReportStructureNode,
    FirstSearchNode,
    ReflectionNode,
    FirstSummaryNode,
    ReflectionSummaryNode,
    ReportFormattingNode
)
from .state import State
from .tools import tavily_search
from .tracing import Tracer, generate_trace_html
from .utils import Config, load_config, format_search_results_for_prompt
from .prompts.prompts import SYSTEM_PROMPT_RESEARCH_PLAN, SYSTEM_PROMPT_GLOBAL_REVIEW


class DeepSearchAgent:
    """Deep Search Agent主类 —— Plan-and-Review 版本"""

    def __init__(self, config: Optional[Config] = None):
        """
        初始化Deep Search Agent

        Args:
            config: 配置对象，如果不提供则自动加载
        """
        self.config = config or load_config()
        self.llm_client = self._initialize_llm()
        self._initialize_nodes()
        self.state = State()
        os.makedirs(self.config.output_dir, exist_ok=True)
        self.tracer = Tracer(enabled=self.config.enable_tracing)
        self.tracing_output_dir = os.path.join(self.config.output_dir, self.config.tracing_subdir)

        print(f"Deep Search Agent 已初始化（Plan-and-Review 版本）")
        print(f"使用LLM: {self.llm_client.get_model_info()}")

    def _initialize_llm(self) -> BaseLLM:
        """初始化LLM客户端"""
        if self.config.default_llm_provider == "deepseek":
            return DeepSeekLLM(
                api_key=self.config.deepseek_api_key,
                model_name=self.config.deepseek_model
            )
        elif self.config.default_llm_provider == "openai":
            return OpenAILLM(
                api_key=self.config.openai_api_key,
                model_name=self.config.openai_model
            )
        else:
            raise ValueError(f"不支持的LLM提供商: {self.config.default_llm_provider}")

    def _initialize_nodes(self):
        """初始化处理节点"""
        self.first_search_node = FirstSearchNode(self.llm_client)
        self.reflection_node = ReflectionNode(self.llm_client)
        self.first_summary_node = FirstSummaryNode(self.llm_client)
        self.reflection_summary_node = ReflectionSummaryNode(self.llm_client)
        self.report_formatting_node = ReportFormattingNode(self.llm_client)

    # =========================================================
    # 主流程入口
    # =========================================================

    def research(self, query: str, save_report: bool = True) -> str:
        """
        执行深度研究 —— Plan-and-Review 流程

        新流程：
          Step 0: 生成研究计划（plan）
          Step 1: 依据 plan 生成报告结构
          Step 2: 按 plan 处理每个段落（搜索/总结/反思）
          Step 3: 生成初版最终报告
          Step 4: 全文总审（global review）
          Step 5: 保存报告

        Args:
            query: 研究查询
            save_report: 是否保存报告到文件

        Returns:
            最终报告内容
        """
        print(f"\n{'='*60}")
        print(f"开始深度研究（Plan-and-Review）: {query}")
        print(f"{'='*60}")

        try:
            self.tracer.set_metadata(
                query=query,
                llm_provider=self.config.default_llm_provider,
                llm_model=self.llm_client.get_model_info()
            )
            self.tracer.log_event("info", "research.start", {"query_length": len(query)})

            with self.tracer.span("step0.make_research_plan"):
                plan = self._make_research_plan(query)

            with self.tracer.span("step1.generate_report_structure"):
                self._generate_report_structure(query, plan)
                self.tracer.log_event(
                    "info",
                    "step1.generate_report_structure",
                    {"paragraph_count": len(self.state.paragraphs)}
                )

            with self.tracer.span("step2.process_paragraphs"):
                self._process_paragraphs(plan)

            with self.tracer.span("step3.generate_draft_report"):
                draft_report = self._generate_final_report()

            with self.tracer.span("step4.global_review"):
                final_report = self._global_review(query, draft_report, plan)

            if save_report:
                with self.tracer.span("step5.save_report"):
                    self._save_report(final_report)

            print(f"\n{'='*60}")
            print("深度研究完成！")
            print(f"{'='*60}")
            self.tracer.log_event("info", "research.finish", {"status": "success"})

            return final_report

        except Exception as e:
            self.tracer.log_event("error", "research.fail", {"error": str(e)})
            print(f"研究过程中发生错误: {str(e)}")
            raise e
        finally:
            trace_path = self.tracer.save(self.tracing_output_dir, filename_prefix="research_trace")
            if trace_path:
                print(f"Tracing 已保存到: {trace_path}")
                try:
                    html_path = generate_trace_html(trace_path)
                    print(f"Tracing HTML 流程图已生成: {html_path}")
                except Exception as exc:
                    print(f"[警告] Tracing HTML 生成失败: {exc}")

    # =========================================================
    # Step 0：生成研究计划
    # =========================================================

    def _make_research_plan(self, query: str) -> Dict[str, Any]:
        """
        生成结构化研究计划（研究施工图）

        Args:
            query: 用户原始研究问题

        Returns:
            plan dict，包含 goal / dimensions / search_hints /
            section_requirements / risk_points
        """
        print(f"\n[步骤 0] 生成研究计划...")

        user_prompt = f"研究查询：{query}"

        try:
            raw = self.llm_client.invoke(SYSTEM_PROMPT_RESEARCH_PLAN, user_prompt)
            # 提取 JSON（防止 LLM 输出多余文字）
            raw = raw.strip()
            json_match = re.search(r'\{.*\}', raw, re.DOTALL)
            if json_match:
                raw = json_match.group(0)
            plan = json.loads(raw)
            self.tracer.log_event(
                "info",
                "step0.make_research_plan",
                {
                    "status": "success",
                    "dimensions_count": len(plan.get("dimensions", []))
                }
            )
        except Exception as e:
            print(f"  [警告] 研究计划生成失败，使用默认计划: {e}")
            plan = {
                "goal": f"全面研究：{query}",
                "dimensions": [],
                "search_hints": {},
                "section_requirements": {},
                "risk_points": ["请确保信息准确", "注意引用最新资料"]
            }
            self.tracer.log_event(
                "warn",
                "step0.make_research_plan",
                {"status": "fallback", "reason": str(e)}
            )

        print(f"  研究目标: {plan.get('goal', query)}")
        dims = plan.get("dimensions", [])
        if dims:
            print(f"  规划维度: {' / '.join(dims)}")
        risk = plan.get("risk_points", [])
        if risk:
            print(f"  风险提示: {'; '.join(risk)}")

        return plan

    # =========================================================
    # Step 1：依据 plan 生成报告结构
    # =========================================================

    def _generate_report_structure(self, query: str, plan: Dict[str, Any]):
        """
        生成报告结构，优先覆盖 plan.dimensions 中的维度

        Args:
            query: 原始研究查询
            plan:  研究施工图
        """
        print(f"\n[步骤 1] 生成报告结构（参考研究计划）...")

        # 将 plan 的维度信息拼入 query，引导 LLM 生成更稳定的大纲
        dims = plan.get("dimensions", [])
        if dims:
            enhanced_query = (
                f"{query}\n\n"
                f"[研究计划要求] 报告结构请优先覆盖以下维度（按顺序）：\n"
                + "\n".join(f"- {d}" for d in dims)
            )
        else:
            enhanced_query = query

        report_structure_node = ReportStructureNode(self.llm_client, enhanced_query)
        self.state = report_structure_node.mutate_state(state=self.state)
        self.tracer.log_event(
            "info",
            "step1.generate_report_structure",
            {
                "query_preview": query[:80],
                "used_dimensions": len(dims),
                "paragraph_count": len(self.state.paragraphs)
            }
        )

        print(f"报告结构已生成，共 {len(self.state.paragraphs)} 个段落:")
        for i, paragraph in enumerate(self.state.paragraphs, 1):
            print(f"  {i}. {paragraph.title}")

    # =========================================================
    # Step 2：按 plan 处理每个段落
    # =========================================================

    def _process_paragraphs(self, plan: Dict[str, Any]):
        """
        按研究计划处理所有段落

        Args:
            plan: 研究施工图
        """
        total_paragraphs = len(self.state.paragraphs)

        for i in range(total_paragraphs):
            print(f"\n[步骤 2.{i+1}] 处理段落: {self.state.paragraphs[i].title}")
            print("-" * 50)
            paragraph_title = self.state.paragraphs[i].title
            with self.tracer.span(
                "step2.process_single_paragraph",
                {"paragraph_index": i, "title": paragraph_title}
            ):
                self._initial_search_and_summary(i, plan)
                self._reflection_loop(i, plan)

            self.state.paragraphs[i].research.mark_completed()

            progress = (i + 1) / total_paragraphs * 100
            print(f"段落处理完成 ({progress:.1f}%)")

    def _initial_search_and_summary(self, paragraph_index: int, plan: Dict[str, Any]):
        """
        执行初始搜索和总结，优先使用 plan.search_hints 中的搜索词

        Args:
            paragraph_index: 当前段落索引
            plan: 研究施工图
        """
        paragraph = self.state.paragraphs[paragraph_index]
        section_title = paragraph.title

        # 从 plan 中获取当前段落的搜索提示词
        search_hints: List[str] = plan.get("search_hints", {}).get(section_title, [])

        if search_hints:
            # 有计划搜索词时，直接用第一个 hint 作为主查询
            search_query = search_hints[0]
            reasoning = f"按研究计划使用预设搜索词（共 {len(search_hints)} 个）"
            print(f"  - [计划搜索] 使用 plan 搜索词: {search_query}")
        else:
            # 无 hint 时退回到原有逻辑：让 LLM 自主生成搜索词
            print("  - [自由搜索] 生成搜索查询...")
            search_input = {
                "title": section_title,
                "content": paragraph.content
            }
            search_output = self.first_search_node.run(search_input)
            search_query = search_output["search_query"]
            reasoning = search_output["reasoning"]
            print(f"  - 搜索查询: {search_query}")
            print(f"  - 推理: {reasoning}")

        # 执行搜索
        print("  - 执行网络搜索...")
        self.tracer.log_event(
            "info",
            "step2.initial_search",
            {"section": section_title, "query": search_query}
        )
        search_results = tavily_search(
            search_query,
            max_results=self.config.max_search_results,
            timeout=self.config.search_timeout,
            api_key=self.config.tavily_api_key
        )

        # 如果有额外 hint，追加搜索（最多再搜 1 次）
        if search_hints and len(search_hints) > 1 and search_results is not None:
            extra_query = search_hints[1]
            print(f"  - [补充搜索] {extra_query}")
            self.tracer.log_event(
                "info",
                "step2.initial_search.extra_query",
                {"section": section_title, "query": extra_query}
            )
            extra_results = tavily_search(
                extra_query,
                max_results=max(1, self.config.max_search_results // 2),
                timeout=self.config.search_timeout,
                api_key=self.config.tavily_api_key
            )
            if extra_results:
                search_results = (search_results or []) + extra_results

        if search_results:
            print(f"  - 找到 {len(search_results)} 个搜索结果")
            for j, result in enumerate(search_results[:3], 1):
                print(f"    {j}. {result['title'][:50]}...")
        else:
            print("  - 未找到搜索结果")
        self.tracer.log_event(
            "info",
            "step2.initial_search.result",
            {"section": section_title, "result_count": len(search_results or [])}
        )

        # 更新搜索历史
        paragraph.research.add_search_results(search_query, search_results)

        # 生成初始总结，额外附加 section_requirements 作为写作要求
        print("  - 生成初始总结...")
        section_req = plan.get("section_requirements", {}).get(section_title, "")
        content_with_req = paragraph.content
        if section_req:
            content_with_req += f"\n\n[写作要求] {section_req}"

        summary_input = {
            "title": section_title,
            "content": content_with_req,
            "search_query": search_query,
            "search_results": format_search_results_for_prompt(
                search_results, self.config.max_content_length
            )
        }

        self.state = self.first_summary_node.mutate_state(
            summary_input, self.state, paragraph_index
        )
        print("  - 初始总结完成")

    def _reflection_loop(self, paragraph_index: int, plan: Dict[str, Any]):
        """
        执行反思循环，结合 plan 的 section_requirements 检查覆盖是否达标

        Args:
            paragraph_index: 当前段落索引
            plan: 研究施工图
        """
        paragraph = self.state.paragraphs[paragraph_index]
        section_title = paragraph.title
        section_req = plan.get("section_requirements", {}).get(section_title, "")

        for reflection_i in range(self.config.max_reflections):
            print(f"  - 反思 {reflection_i + 1}/{self.config.max_reflections}...")

            # 构建反思输入，附加计划要求让反思更有针对性
            latest_state = paragraph.research.latest_summary
            content_with_req = paragraph.content
            if section_req:
                content_with_req += f"\n\n[计划要求] {section_req}"

            reflection_input = {
                "title": section_title,
                "content": content_with_req,
                "paragraph_latest_state": latest_state
            }

            reflection_output = self.reflection_node.run(reflection_input)
            search_query = reflection_output["search_query"]
            reasoning = reflection_output["reasoning"]
            self.tracer.log_event(
                "info",
                "step2.reflection.search_query",
                {
                    "section": section_title,
                    "iteration": reflection_i + 1,
                    "query": search_query
                }
            )

            print(f"    反思查询: {search_query}")
            print(f"    反思推理: {reasoning}")

            # 执行反思搜索
            search_results = tavily_search(
                search_query,
                max_results=self.config.max_search_results,
                timeout=self.config.search_timeout,
                api_key=self.config.tavily_api_key
            )

            if search_results:
                print(f"    找到 {len(search_results)} 个反思搜索结果")
            self.tracer.log_event(
                "info",
                "step2.reflection.search_result",
                {
                    "section": section_title,
                    "iteration": reflection_i + 1,
                    "result_count": len(search_results or [])
                }
            )

            paragraph.research.add_search_results(search_query, search_results)

            # 生成反思总结
            reflection_summary_input = {
                "title": section_title,
                "content": content_with_req,
                "search_query": search_query,
                "search_results": format_search_results_for_prompt(
                    search_results, self.config.max_content_length
                ),
                "paragraph_latest_state": latest_state
            }

            self.state = self.reflection_summary_node.mutate_state(
                reflection_summary_input, self.state, paragraph_index
            )
            print(f"    反思 {reflection_i + 1} 完成")

    # =========================================================
    # Step 3：生成初版最终报告（保持原有逻辑）
    # =========================================================

    def _generate_final_report(self) -> str:
        """生成初版最终报告"""
        print(f"\n[步骤 3] 生成初版报告...")

        report_data = []
        for paragraph in self.state.paragraphs:
            report_data.append({
                "title": paragraph.title,
                "paragraph_latest_state": paragraph.research.latest_summary
            })

        try:
            draft = self.report_formatting_node.run(report_data)
        except Exception as e:
            print(f"LLM格式化失败，使用备用方法: {str(e)}")
            draft = self.report_formatting_node.format_report_manually(
                report_data, self.state.report_title
            )

        self.state.final_report = draft
        self.state.mark_completed()

        print("初版报告生成完成")
        return draft

    # =========================================================
    # Step 4：全文总审（新增）
    # =========================================================

    def _global_review(self, query: str, draft: str, plan: Dict[str, Any]) -> str:
        """
        对初版报告进行全文总审，对照 plan 检查：
          1. 覆盖性（是否覆盖所有维度）
          2. 重复性（去除冗余段落）
          3. 连贯性（段落间逻辑过渡）
          4. 结论一致性（结论有无证据支撑）

        Args:
            query:  原始研究查询
            draft:  初版报告全文
            plan:   研究施工图

        Returns:
            优化后的最终报告
        """
        print(f"\n[步骤 4] 全文总审（Global Review）...")

        plan_summary = json.dumps(plan, ensure_ascii=False, indent=2)
        user_prompt = (
            f"【原始研究查询】\n{query}\n\n"
            f"【研究计划】\n{plan_summary}\n\n"
            f"【报告草稿】\n{draft}"
        )

        try:
            final = self.llm_client.invoke(SYSTEM_PROMPT_GLOBAL_REVIEW, user_prompt)
            final = final.strip()
            if not final:
                print("  [警告] 全文总审返回空内容，保留初版报告")
                final = draft
                self.tracer.log_event(
                    "warn",
                    "step4.global_review",
                    {"status": "fallback_empty_response"}
                )
        except Exception as e:
            print(f"  [警告] 全文总审失败，保留初版报告: {e}")
            final = draft
            self.tracer.log_event(
                "warn",
                "step4.global_review",
                {"status": "fallback_exception", "reason": str(e)}
            )

        # 更新状态中的最终报告
        self.state.final_report = final
        print("全文总审完成，最终报告已生成")
        return final

    # =========================================================
    # 辅助方法（保持不变）
    # =========================================================

    def _save_report(self, report_content: str):
        """保存报告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = "".join(
            c for c in self.state.query if c.isalnum() or c in (' ', '-', '_')
        ).rstrip()
        query_safe = query_safe.replace(' ', '_')[:30]

        filename = f"deep_search_report_{query_safe}_{timestamp}.md"
        filepath = os.path.join(self.config.output_dir, filename)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"报告已保存到: {filepath}")

        if self.config.save_intermediate_states:
            state_filename = f"state_{query_safe}_{timestamp}.json"
            state_filepath = os.path.join(self.config.output_dir, state_filename)
            self.state.save_to_file(state_filepath)
            print(f"状态已保存到: {state_filepath}")

    def get_progress_summary(self) -> Dict[str, Any]:
        """获取进度摘要"""
        return self.state.get_progress_summary()

    def load_state(self, filepath: str):
        """从文件加载状态"""
        self.state = State.load_from_file(filepath)
        print(f"状态已从 {filepath} 加载")

    def save_state(self, filepath: str):
        """保存状态到文件"""
        self.state.save_to_file(filepath)
        print(f"状态已保存到 {filepath}")


def create_agent(config_file: Optional[str] = None) -> DeepSearchAgent:
    """
    创建Deep Search Agent实例的便捷函数

    Args:
        config_file: 配置文件路径

    Returns:
        DeepSearchAgent实例
    """
    config = load_config(config_file)
    return DeepSearchAgent(config)
