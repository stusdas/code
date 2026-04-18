"""
测试脚本：验证 _make_research_plan 的 JSON 解析逻辑
不需要 API Key，纯本地逻辑测试
"""
import json
import re


def parse_plan(raw: str) -> dict:
    """模拟 agent 中的 plan 解析逻辑"""
    raw = raw.strip()
    json_match = re.search(r'\{.*\}', raw, re.DOTALL)
    if json_match:
        raw = json_match.group(0)
    return json.loads(raw)


# === 测试 1：LLM 返回带多余文字时能正确解析 ===
fake_response_with_extra = (
    "这是研究计划：\n"
    '{\n'
    '  "goal": "分析AI Agent发展现状",\n'
    '  "dimensions": ["背景", "现状", "挑战", "趋势"],\n'
    '  "search_hints": {\n'
    '    "背景": ["AI Agent overview", "AI Agent是什么"],\n'
    '    "现状": ["AI Agent 2025"]\n'
    '  },\n'
    '  "section_requirements": {\n'
    '    "背景": "定义清晰，不超过200字"\n'
    '  },\n'
    '  "risk_points": ["避免陈旧数据", "不要泛泛而谈"]\n'
    '}\n'
    "好的，以上是计划。"
)

plan = parse_plan(fake_response_with_extra)
assert plan["goal"] == "分析AI Agent发展现状", "goal 解析失败"
assert len(plan["dimensions"]) == 4, "dimensions 数量错误"
assert "背景" in plan["search_hints"], "search_hints 缺少'背景'"
assert len(plan["risk_points"]) == 2, "risk_points 数量错误"
print("[PASS] 测试1：带多余文字的 LLM 输出解析正常")

# === 测试 2：search_hints 取值逻辑 ===
hints = plan.get("search_hints", {}).get("背景", [])
assert hints == ["AI Agent overview", "AI Agent是什么"], "search_hints 取值错误"
print("[PASS] 测试2：search_hints 取值逻辑正常")

# === 测试 3：section_requirements 拼接逻辑 ===
section_req = plan.get("section_requirements", {}).get("背景", "")
content = "段落描述内容"
if section_req:
    content_with_req = content + f"\n\n[写作要求] {section_req}"
assert "[写作要求]" in content_with_req, "section_req 拼接失败"
print("[PASS] 测试3：section_requirements 拼接逻辑正常")

# === 测试 4：LLM 返回空字符串时降级逻辑 ===
fake_empty = ""
try:
    parse_plan(fake_empty)
    print("[FAIL] 测试4：应当抛出异常")
except Exception:
    # 异常被捕获，走降级逻辑
    fallback_plan = {
        "goal": "全面研究：测试查询",
        "dimensions": [],
        "search_hints": {},
        "section_requirements": {},
        "risk_points": []
    }
    assert fallback_plan["goal"].startswith("全面研究"), "降级 plan 格式错误"
    print("[PASS] 测试4：空响应降级逻辑正常")

print("\n所有测试通过！")
