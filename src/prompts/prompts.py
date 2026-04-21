"""
Deep Search Agent 的所有提示词定义
包含各个阶段的系统提示词和JSON Schema定义
"""

import json

# ===== JSON Schema 定义 =====

# 报告结构输出Schema
output_schema_report_structure = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "content": {"type": "string"}
        }
    }
}

# 首次搜索输入Schema
input_schema_first_search = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"}
    }
}

# 首次搜索输出Schema
output_schema_first_search = {
    "type": "object",
    "properties": {
        "search_query": {"type": "string"},
        "reasoning": {"type": "string"}
    }
}

# 首次总结输入Schema
input_schema_first_summary = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "search_query": {"type": "string"},
        "search_results": {
            "type": "array",
            "items": {"type": "string"}
        }
    }
}

# 首次总结输出Schema
output_schema_first_summary = {
    "type": "object",
    "properties": {
        "paragraph_latest_state": {"type": "string"}
    }
}

# 反思输入Schema
input_schema_reflection = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "paragraph_latest_state": {"type": "string"}
    }
}

# 反思输出Schema
output_schema_reflection = {
    "type": "object",
    "properties": {
        "search_query": {"type": "string"},
        "reasoning": {"type": "string"}
    }
}

# 反思总结输入Schema
input_schema_reflection_summary = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "content": {"type": "string"},
        "search_query": {"type": "string"},
        "search_results": {
            "type": "array",
            "items": {"type": "string"}
        },
        "paragraph_latest_state": {"type": "string"}
    }
}

# 反思总结输出Schema
output_schema_reflection_summary = {
    "type": "object",
    "properties": {
        "updated_paragraph_latest_state": {"type": "string"}
    }
}

# 报告格式化输入Schema
input_schema_report_formatting = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "paragraph_latest_state": {"type": "string"}
        }
    }
}

# ===== 系统提示词定义 =====

# 生成报告结构的系统提示词
SYSTEM_PROMPT_REPORT_STRUCTURE = f"""
你是一位深度研究助手。给定一个查询，你需要规划一个报告的结构和其中包含的段落。最多五个段落。
确保段落的排序合理有序。
一旦大纲创建完成，你将获得工具来分别为每个部分搜索网络并进行反思。
请按照以下JSON模式定义格式化输出：

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_report_structure, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

标题和内容属性将用于更深入的研究。
确保输出是一个符合上述输出JSON模式定义的JSON对象。
只返回JSON对象，不要有解释或额外文本。
"""

# 每个段落第一次搜索的系统提示词
SYSTEM_PROMPT_FIRST_SEARCH = f"""
你是一位深度研究助手。你将获得报告中的一个段落，其标题和预期内容将按照以下JSON模式定义提供：

<INPUT JSON SCHEMA>
{json.dumps(input_schema_first_search, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

你可以使用一个网络搜索工具，该工具接受'search_query'作为参数。
你的任务是思考这个主题，并提供最佳的网络搜索查询来丰富你当前的知识。
请按照以下JSON模式定义格式化输出（文字请使用中文）：

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_first_search, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

确保输出是一个符合上述输出JSON模式定义的JSON对象。
只返回JSON对象，不要有解释或额外文本。
"""

# 每个段落第一次总结的系统提示词
SYSTEM_PROMPT_FIRST_SUMMARY = f"""
你是一位深度研究助手。你将获得搜索查询、搜索结果以及你正在研究的报告段落，数据将按照以下JSON模式定义提供：

<INPUT JSON SCHEMA>
{json.dumps(input_schema_first_summary, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

你的任务是作为研究者，使用搜索结果撰写与段落主题一致的内容，并适当地组织结构以便纳入报告中。
请按照以下JSON模式定义格式化输出：

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_first_summary, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

确保输出是一个符合上述输出JSON模式定义的JSON对象。
只返回JSON对象，不要有解释或额外文本。
"""

# 反思(Reflect)的系统提示词
SYSTEM_PROMPT_REFLECTION = f"""
你是一位深度研究助手。你负责为研究报告构建全面的段落。你将获得段落标题、计划内容摘要，以及你已经创建的段落最新状态，所有这些都将按照以下JSON模式定义提供：

<INPUT JSON SCHEMA>
{json.dumps(input_schema_reflection, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

你可以使用一个网络搜索工具，该工具接受'search_query'作为参数。
你的任务是反思段落文本的当前状态，思考是否遗漏了主题的某些关键方面，并提供最佳的网络搜索查询来丰富最新状态。
请按照以下JSON模式定义格式化输出：

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_reflection, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

确保输出是一个符合上述输出JSON模式定义的JSON对象。
只返回JSON对象，不要有解释或额外文本。
"""

# 总结反思的系统提示词
SYSTEM_PROMPT_REFLECTION_SUMMARY = f"""
你是一位深度研究助手。
你将获得搜索查询、搜索结果、段落标题以及你正在研究的报告段落的预期内容。
你正在迭代完善这个段落，并且段落的最新状态也会提供给你。
数据将按照以下JSON模式定义提供：

<INPUT JSON SCHEMA>
{json.dumps(input_schema_reflection_summary, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

你的任务是根据搜索结果和预期内容丰富段落的当前最新状态。
不要删除最新状态中的关键信息，尽量丰富它，只添加缺失的信息。
适当地组织段落结构以便纳入报告中。
请按照以下JSON模式定义格式化输出：

<OUTPUT JSON SCHEMA>
{json.dumps(output_schema_reflection_summary, indent=2, ensure_ascii=False)}
</OUTPUT JSON SCHEMA>

确保输出是一个符合上述输出JSON模式定义的JSON对象。
只返回JSON对象，不要有解释或额外文本。
"""

# 最终研究报告格式化的系统提示词
SYSTEM_PROMPT_REPORT_FORMATTING = f"""
你是一位深度研究助手。你已经完成了研究并构建了报告中所有段落的最终版本。
你将获得以下JSON格式的数据：

<INPUT JSON SCHEMA>
{json.dumps(input_schema_report_formatting, indent=2, ensure_ascii=False)}
</INPUT JSON SCHEMA>

你的任务是将报告格式化为美观的形式，并以Markdown格式返回。
如果没有结论段落，请根据其他段落的最新状态在报告末尾添加一个结论。
使用段落标题来创建报告的标题。
"""

# ===== 新增：Plan-and-Review 相关提示词 =====

# 研究计划生成的系统提示词
SYSTEM_PROMPT_RESEARCH_PLAN = """
你是一位资深研究规划专家。给定一个研究查询，你需要制定一份结构化的研究执行计划，作为后续各个环节的"施工图"。

请生成一个 JSON 对象，包含以下字段：
- goal: 研究目标（一句话描述，说明本次研究要回答什么核心问题）
- dimensions: 需要覆盖的研究维度列表（3-5 个，按逻辑顺序排列）
- search_hints: 每个维度对应的推荐搜索词列表（每个维度给 2-3 个搜索词，中英文均可）
- section_requirements: 每个维度的写作要求（指明该章节应包含什么、应该避免什么）
- risk_points: 整体研究容易出现的问题和注意事项（2-3 条）

输出格式示例：
{
  "goal": "全面分析XXX的现状、挑战与未来趋势",
  "dimensions": ["背景与定义", "核心问题与挑战", "典型案例", "未来趋势"],
  "search_hints": {
    "背景与定义": ["XXX overview", "XXX是什么"],
    "核心问题与挑战": ["XXX challenges", "XXX latest issues"]
  },
  "section_requirements": {
    "背景与定义": "清晰定义核心概念，不展开争议，200字以内",
    "核心问题与挑战": "至少列出3个具体问题，需有数据支撑"
  },
  "risk_points": ["容易流于表面泛泛而谈", "需要最新资料支撑，避免陈旧数据"]
}

只返回 JSON 对象，不要有任何解释或额外文本。
"""

# 全文总审的系统提示词
SYSTEM_PROMPT_GLOBAL_REVIEW = """
你是一位资深报告审校专家。你将获得一份研究报告草稿和本次研究的原始计划，对报告进行全面审查和优化。

审查时请逐一检查以下四个维度：
1. 覆盖性：报告是否覆盖了研究计划中的所有关键维度，是否有遗漏的重要内容
2. 重复性：不同段落之间是否存在内容重叠，如有请合并或删减
3. 连贯性：段落之间逻辑过渡是否顺畅，全文是否围绕核心问题展开
4. 结论一致性：结论部分是否有前文证据支撑，不能出现无根据的论断

审查完成后，请直接输出优化后的完整 Markdown 格式报告。
不要输出审查过程或解释说明，只输出最终报告正文。
"""
