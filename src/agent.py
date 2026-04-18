"""
Deep Search Agent主类 —— Plan-and-Review 版本
最小范围“骨架保留型重构”版

重构原则：
1. DeepSearchAgent 继续一眼看出：
   plan -> structure -> search -> reflection -> report -> review
2. 不拆散主流程
3. 不把入口文件变成空壳
4. 只把每一步内部过长的细节收口为同文件私有 helper
"""

import json
import os
import re
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple

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
from .memory import MemoryStore
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
        self.tracing_output_dir = os.path.join(
            self.config.output_dir,
            self.config.tracing_subdir
        )

        self.memory = MemoryStore(os.path.join(self.config.output_dir, "memory"))
        self.current_search_cache: List[Dict[str, Any]] = []

        print("Deep Search Agent 已初始化（Plan-and-Review 版本）")
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

        主流程骨架必须保持可读：
          Step 0: plan
          Step 1: structure
          Step 2: search + reflection
          Step 3: report
          Step 4: review
          Step 5: save

        Args:
            query: 研究查询
            save_report: 是否保存报告到文件

        Returns:
            最终报告内容
        """
        print(f"\n{'='*60}")
        print(f"开始深度研究（Plan-and-Review）: {query}")
        print(f"{'='*60}")

        self.current_search_cache = []

        try:
            self._start_research_trace(query)

            # Step 0: plan
            with self.tracer.span("step0.make_research_plan"):
                plan = self._get_or_create_research_plan(query)

            # Step 1: structure
            with self.tracer.span("step1.generate_report_structure"):
                self._generate_report_structure(query, plan)
                self._log_structure_generated(query, plan)

            # Step 2: search + reflection
            with self.tracer.span("step2.process_paragraphs"):
                self._process_paragraphs(plan)

            # Step 3: report
            with self.tracer.span("step3.generate_draft_report"):
                draft_report = self._generate_final_report()

            # Step 4: review
            with self.tracer.span("step4.global_review"):
                final_report = self._global_review(query, draft_report, plan)

            # Step 5: save
            if save_report:
                with self.tracer.span("step5.save_report"):
                    self._save_report(final_report)

            self._finalize_research_memory(query, plan, final_report)

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
            self._persist_trace_files()

    # =========================================================
    # Step 0：plan
    # =========================================================

    def _get_or_create_research_plan(self, query: str) -> Dict[str, Any]:
        """
        优先从 memory 复用 plan，否则重新生成 plan。
        """
        memory_record = self.memory.find_similar_query(query, threshold=0.85)
        if memory_record and memory_record.get("plan"):
            plan = memory_record["plan"]
            self.tracer.log_event(
                "info",
                "memory.plan_hit",
                {
                    "query": query,
                    "matched_query": memory_record.get("query", ""),
                    "dimensions_count": len(plan.get("dimensions", []))
                }
            )
            self._print_plan_summary(plan, query)
            return plan

        return self._make_research_plan(query)

    def _make_research_plan(self, query: str) -> Dict[str, Any]:
        """
        生成结构化研究计划（研究施工图）

        Args:
            query: 用户原始研究问题

        Returns:
            plan dict
        """
        print("\n[步骤 0] 生成研究计划...")

        user_prompt = f"研究查询：{query}"

        try:
            raw = self.llm_client.invoke(SYSTEM_PROMPT_RESEARCH_PLAN, user_prompt)
            plan = self._parse_plan_response(raw)

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
            plan = self._default_plan(query)

            self.tracer.log_event(
                "warn",
                "step0.make_research_plan",
                {"status": "fallback", "reason": str(e)}
            )

        self._print_plan_summary(plan, query)
        return plan

    def _parse_plan_response(self, raw: str) -> Dict[str, Any]:
        """
        从 LLM 输出中提取并解析 plan JSON。
        """
        raw = raw.strip()
        json_match = re.search(r"\{.*\}", raw, re.DOTALL)
        if json_match:
            raw = json_match.group(0)
        return json.loads(raw)

    def _default_plan(self, query: str) -> Dict[str, Any]:
        """
        计划生成失败时使用的默认 plan。
        """
        return {
            "goal": f"全面研究：{query}",
            "dimensions": [],
            "search_hints": {},
            "section_requirements": {},
            "risk_points": ["请确保信息准确", "注意引用最新资料"]
        }

    def _print_plan_summary(self, plan: Dict[str, Any], query: str) -> None:
        """
        打印 plan 摘要，保持原有交互感。
        """
        print(f"  研究目标: {plan.get('goal', query)}")

        dims = plan.get("dimensions", [])
        if dims:
            print(f"  规划维度: {' / '.join(dims)}")

        risk = plan.get("risk_points", [])
        if risk:
            print(f"  风险提示: {'; '.join(risk)}")

    # =========================================================
    # Step 1：structure
    # =========================================================

    def _generate_report_structure(self, query: str, plan: Dict[str, Any]):
        """
        生成报告结构，优先覆盖 plan.dimensions 中的维度

        Args:
            query: 原始研究查询
            plan: 研究施工图
        """
        print("\n[步骤 1] 生成报告结构（参考研究计划）...")

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

        print(f"报告结构已生成，共 {len(self.state.paragraphs)} 个段落:")
        for i, paragraph in enumerate(self.state.paragraphs, 1):
            print(f"  {i}. {paragraph.title}")

    # =========================================================
    # Step 2：search + reflection
    # =========================================================

    def _process_paragraphs(self, plan: Dict[str, Any]):
        """
        按研究计划处理所有段落
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
                # search
                self._initial_search_and_summary(i, plan)
                # reflection
                self._reflection_loop(i, plan)

            self.state.paragraphs[i].research.mark_completed()

            progress = (i + 1) / total_paragraphs * 100
            print(f"段落处理完成 ({progress:.1f}%)")

    # -------------------------
    # search
    # -------------------------

    def _initial_search_and_summary(self, paragraph_index: int, plan: Dict[str, Any]):
        """
        初始搜索 + 初始总结
        """
        paragraph = self.state.paragraphs[paragraph_index]
        section_title = paragraph.title

        search_query, reasoning, search_hints = self._resolve_initial_search_query(
            paragraph, plan
        )

        search_results, from_memory_cache = self._run_search_with_cache(
            section_title,
            search_query
        )

        search_results = self._maybe_run_extra_search(
            section_title,
            search_hints,
            search_results,
            from_memory_cache
        )

        self._record_search_cache(search_query, search_results)
        self._print_search_results_preview(search_results)

        self.tracer.log_event(
            "info",
            "step2.initial_search.result",
            {"section": section_title, "result_count": len(search_results or [])}
        )

        paragraph.research.add_search_results(search_query, search_results)

        print("  - 生成初始总结...")
        summary_input = self._build_first_summary_input(
            paragraph,
            plan,
            search_query,
            search_results
        )

        self.state = self.first_summary_node.mutate_state(
            summary_input,
            self.state,
            paragraph_index
        )
        print("  - 初始总结完成")

    def _resolve_initial_search_query(
        self,
        paragraph,
        plan: Dict[str, Any]
    ) -> Tuple[str, str, List[str]]:
        """
        决定本段首次搜索查询：优先用 plan hint，否则走 FirstSearchNode。
        """
        section_title = paragraph.title
        search_hints: List[str] = plan.get("search_hints", {}).get(section_title, [])

        if search_hints:
            search_query = search_hints[0]
            reasoning = f"按研究计划使用预设搜索词（共 {len(search_hints)} 个）"
            print(f"  - [计划搜索] 使用 plan 搜索词: {search_query}")
            return search_query, reasoning, search_hints

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
        return search_query, reasoning, search_hints

    def _run_search_with_cache(
        self,
        section_title: str,
        search_query: str
    ) -> Tuple[List[Dict[str, Any]], bool]:
        """
        执行首次搜索，并优先命中 memory cache。
        """
        print("  - 执行网络搜索...")
        self.tracer.log_event(
            "info",
            "step2.initial_search",
            {"section": section_title, "query": search_query}
        )

        cached_results = self.memory.find_search_cache(search_query, threshold=0.92)
        from_memory_cache = cached_results is not None

        if from_memory_cache:
            search_results = cached_results
            self.tracer.log_event(
                "info",
                "memory.search_hit",
                {
                    "section": section_title,
                    "query": search_query,
                    "result_count": len(search_results)
                }
            )
        else:
            search_results = tavily_search(
                search_query,
                max_results=self.config.max_search_results,
                timeout=self.config.search_timeout,
                api_key=self.config.tavily_api_key
            )
            self.tracer.log_event(
                "info",
                "memory.search_miss",
                {
                    "section": section_title,
                    "query": search_query,
                    "result_count": len(search_results or [])
                }
            )

        return search_results, from_memory_cache

    def _maybe_run_extra_search(
        self,
        section_title: str,
        search_hints: List[str],
        search_results: List[Dict[str, Any]],
        from_memory_cache: bool
    ) -> List[Dict[str, Any]]:
        """
        如果 plan 提供了额外 hint，则追加一次补充搜索。
        """
        if (
            from_memory_cache
            or not search_hints
            or len(search_hints) <= 1
            or search_results is None
        ):
            return search_results

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
            return (search_results or []) + extra_results

        return search_results

    def _record_search_cache(
        self,
        search_query: str,
        search_results: List[Dict[str, Any]]
    ) -> None:
        """
        把本轮搜索记录到当前研究缓存里。
        """
        self.current_search_cache.append({
            "search_query": search_query,
            "results": search_results or []
        })

    def _print_search_results_preview(
        self,
        search_results: List[Dict[str, Any]]
    ) -> None:
        """
        打印搜索结果摘要。
        """
        if search_results:
            print(f"  - 找到 {len(search_results)} 个搜索结果")
            for j, result in enumerate(search_results[:3], 1):
                title = result.get("title", "")
                print(f"    {j}. {title[:50]}...")
        else:
            print("  - 未找到搜索结果")

    def _build_first_summary_input(
        self,
        paragraph,
        plan: Dict[str, Any],
        search_query: str,
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        构造首次总结的输入。
        """
        section_title = paragraph.title
        section_req = plan.get("section_requirements", {}).get(section_title, "")

        content_with_req = paragraph.content
        if section_req:
            content_with_req += f"\n\n[写作要求] {section_req}"

        return {
            "title": section_title,
            "content": content_with_req,
            "search_query": search_query,
            "search_results": format_search_results_for_prompt(
                search_results,
                self.config.max_content_length
            )
        }

    # -------------------------
    # reflection
    # -------------------------

    def _reflection_loop(self, paragraph_index: int, plan: Dict[str, Any]):
        """
        反思循环：保持 reflection 步骤清晰可见。
        """
        paragraph = self.state.paragraphs[paragraph_index]
        section_title = paragraph.title

        for reflection_i in range(self.config.max_reflections):
            print(f"  - 反思 {reflection_i + 1}/{self.config.max_reflections}...")

            reflection_input = self._build_reflection_input(paragraph, plan)
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

            search_results = self._run_reflection_search(search_query)

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

            reflection_summary_input = self._build_reflection_summary_input(
                reflection_input,
                search_query,
                search_results
            )

            self.state = self.reflection_summary_node.mutate_state(
                reflection_summary_input,
                self.state,
                paragraph_index
            )

            print(f"    反思 {reflection_i + 1} 完成")

    def _build_reflection_input(
        self,
        paragraph,
        plan: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        构造反思输入。
        """
        section_title = paragraph.title
        section_req = plan.get("section_requirements", {}).get(section_title, "")
        latest_state = paragraph.research.latest_summary

        content_with_req = paragraph.content
        if section_req:
            content_with_req += f"\n\n[计划要求] {section_req}"

        return {
            "title": section_title,
            "content": content_with_req,
            "paragraph_latest_state": latest_state
        }

    def _run_reflection_search(self, search_query: str) -> List[Dict[str, Any]]:
        """
        执行反思搜索。
        """
        return tavily_search(
            search_query,
            max_results=self.config.max_search_results,
            timeout=self.config.search_timeout,
            api_key=self.config.tavily_api_key
        )

    def _build_reflection_summary_input(
        self,
        reflection_input: Dict[str, Any],
        search_query: str,
        search_results: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        构造反思总结输入。
        """
        return {
            "title": reflection_input["title"],
            "content": reflection_input["content"],
            "search_query": search_query,
            "search_results": format_search_results_for_prompt(
                search_results,
                self.config.max_content_length
            ),
            "paragraph_latest_state": reflection_input["paragraph_latest_state"]
        }

    # =========================================================
    # Step 3：report
    # =========================================================

    def _generate_final_report(self) -> str:
        """
        生成初版最终报告
        """
        print("\n[步骤 3] 生成初版报告...")

        report_data = self._build_report_data()

        try:
            draft = self.report_formatting_node.run(report_data)
        except Exception as e:
            print(f"LLM格式化失败，使用备用方法: {str(e)}")
            draft = self.report_formatting_node.format_report_manually(
                report_data,
                self.state.report_title
            )

        self.state.final_report = draft
        self.state.mark_completed()

        print("初版报告生成完成")
        return draft

    def _build_report_data(self) -> List[Dict[str, str]]:
        """
        将段落最新总结收集为报告格式化输入。
        """
        report_data = []
        for paragraph in self.state.paragraphs:
            report_data.append({
                "title": paragraph.title,
                "paragraph_latest_state": paragraph.research.latest_summary
            })
        return report_data

    # =========================================================
    # Step 4：review
    # =========================================================

    def _global_review(self, query: str, draft: str, plan: Dict[str, Any]) -> str:
        """
        对初版报告进行全文总审
        """
        print("\n[步骤 4] 全文总审（Global Review）...")

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

        self.state.final_report = final
        print("全文总审完成，最终报告已生成")
        return final

    # =========================================================
    # Step 5：save
    # =========================================================

    def _save_report(self, report_content: str):
        """保存报告到文件"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        query_safe = "".join(
            c for c in self.state.query if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        query_safe = query_safe.replace(" ", "_")[:30]

        filename = f"deep_search_report_{query_safe}_{timestamp}.md"
        filepath = os.path.join(self.config.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(report_content)

        print(f"报告已保存到: {filepath}")

        if self.config.save_intermediate_states:
            state_filename = f"state_{query_safe}_{timestamp}.json"
            state_filepath = os.path.join(self.config.output_dir, state_filename)
            self.state.save_to_file(state_filepath)
            print(f"状态已保存到: {state_filepath}")

    # =========================================================
    # tracing / memory / finalize
    # =========================================================

    def _start_research_trace(self, query: str) -> None:
        """
        启动研究 trace 元数据记录。
        """
        self.tracer.set_metadata(
            query=query,
            llm_provider=self.config.default_llm_provider,
            llm_model=self.llm_client.get_model_info()
        )
        self.tracer.log_event("info", "research.start", {"query_length": len(query)})

    def _log_structure_generated(self, query: str, plan: Dict[str, Any]) -> None:
        """
        记录 structure 生成完成事件。
        """
        self.tracer.log_event(
            "info",
            "step1.generate_report_structure",
            {
                "query_preview": query[:80],
                "used_dimensions": len(plan.get("dimensions", [])),
                "paragraph_count": len(self.state.paragraphs)
            }
        )

    def _finalize_research_memory(
        self,
        query: str,
        plan: Dict[str, Any],
        final_report: str
    ) -> None:
        """
        研究结束后更新 memory。
        """
        self.memory.upsert_record(
            query=query,
            plan=plan,
            search_cache=self.current_search_cache,
            final_report_summary={
                "summary": final_report[:500],
                "final_length": len(final_report)
            }
        )
        self.tracer.log_event(
            "info",
            "memory.upsert",
            {
                "query": query,
                "search_cache_count": len(self.current_search_cache),
                "summary_length": min(500, len(final_report))
            }
        )

    def _persist_trace_files(self) -> None:
        """
        保存 trace json，并尽量生成 html。
        """
        trace_path = self.tracer.save(
            self.tracing_output_dir,
            filename_prefix="research_trace"
        )
        if trace_path:
            print(f"Tracing 已保存到: {trace_path}")
            try:
                html_path = generate_trace_html(trace_path)
                print(f"Tracing HTML 流程图已生成: {html_path}")
            except Exception as exc:
                print(f"[警告] Tracing HTML 生成失败: {exc}")

    # =========================================================
    # 辅助方法（保持不变）
    # =========================================================

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
    """
    config = load_config(config_file)
    return DeepSearchAgent(config)
