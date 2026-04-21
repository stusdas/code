# 最小改动 AI Memory 方案
## 目标
让系统对**相同或相似问题**，第二次运行时能：

+  复用上一次的 `plan`
+  复用上一次的搜索结果 
+  少查一点、少想一点 
+  比原来快一点 

不做数据库，不做向量，不做复杂长期记忆。  
只做一个**本地 JSON 记忆缓存**。

---

# 一、只改 2 个文件
## 新增
+ `src/memory.py`

## 修改
+ `src/agent.py`

就这两个。

---

# 二、memory 的核心思路
每次任务结束后，把这次任务的关键内容存下来：

+  用户 query 
+  生成的 plan 
+  搜索 query 和搜索结果 
+  最终报告前 500 字摘要 

下次来一个新 query 时：

1.  先看历史里有没有**相似 query**
2.  有的话，直接复用它的 `plan`
3.  搜索前先看历史里有没有**相似 search_query**
4.  有的话，直接复用历史搜索结果 
5.  没有再调用 Tavily 

这就已经算最小可用的 AI memory 了。

---

# 三、memory 存储文件
在输出目录下新增：

```plain
output/memory/memory_store.json
```

格式如下：

```plain
{
  "records": [
    {
      "query": "AI agent 在教育中的应用",
      "query_normalized": "ai agent 在教育中的应用",
      "plan": {
        "goal": "...",
        "dimensions": ["背景", "问题", "案例", "趋势"],
        "search_hints": {},
        "section_requirements": {},
        "risk_points": []
      },
      "search_cache": [
        {
          "search_query": "AI agent education overview",
          "results": [
            {
              "title": "...",
              "url": "...",
              "content": "..."
            }
          ]
        }
      ],
      "final_report_summary": {
        "summary": "......",
        "final_length": 8000
      }
    }
  ]
}
```

---

# 四、新增文件：`src/memory.py`
直接实现下面这个类。

```plain
import json
import os
from datetime import datetime
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional


class MemoryStore:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.filepath = os.path.join(self.base_dir, "memory_store.json")

    def _empty_store(self) -> Dict[str, Any]:
        return {
            "records": []
        }

    def load_store(self) -> Dict[str, Any]:
        if not os.path.exists(self.filepath):
            return self._empty_store()

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self._empty_store()

    def save_store(self, store: Dict[str, Any]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)

    def normalize_text(self, text: str) -> str:
        return " ".join(text.lower().strip().split())

    def similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, self.normalize_text(a), self.normalize_text(b)).ratio()

    def find_similar_query(self, query: str, threshold: float = 0.85) -> Optional[Dict[str, Any]]:
        store = self.load_store()
        best_record = None
        best_score = 0.0

        for record in store["records"]:
            score = self.similarity(query, record.get("query_normalized", record.get("query", "")))
            if score > best_score:
                best_score = score
                best_record = record

        if best_record and best_score >= threshold:
            return best_record
        return None

    def find_search_cache(self, search_query: str, threshold: float = 0.92) -> Optional[List[Dict[str, Any]]]:
        store = self.load_store()
        best_results = None
        best_score = 0.0

        for record in store["records"]:
            for cache in record.get("search_cache", []):
                score = self.similarity(search_query, cache.get("search_query", ""))
                if score > best_score:
                    best_score = score
                    best_results = cache.get("results", [])

        if best_results is not None and best_score >= threshold:
            return best_results
        return None

    def upsert_record(
        self,
        query: str,
        plan: Dict[str, Any],
        search_cache: List[Dict[str, Any]],
        final_report_summary: Dict[str, Any]
    ) -> None:
        store = self.load_store()
        normalized_query = self.normalize_text(query)

        for record in store["records"]:
            if record.get("query_normalized") == normalized_query:
                record["plan"] = plan
                record["search_cache"] = search_cache
                record["final_report_summary"] = final_report_summary
                record["updated_at"] = datetime.now().isoformat()
                self.save_store(store)
                return

        store["records"].append({
            "query": query,
            "query_normalized": normalized_query,
            "created_at": datetime.now().isoformat(),
            "plan": plan,
            "search_cache": search_cache,
            "final_report_summary": final_report_summary
        })
        self.save_store(store)
```

---

# 五、修改 `src/agent.py`
## 1. 顶部新增 import
```plain
from .memory import MemoryStore
```

---

## 2. 在 `__init__()` 里新增
加在初始化 `self.state` 和 `self.tracer` 附近都可以：

```plain
self.memory = MemoryStore(os.path.join(self.config.output_dir, "memory"))
self.current_search_cache = []
```

---

## 3. 在 `research()` 一开始清空本次搜索缓存
在函数开头、真正开始流程前加：

```plain
self.current_search_cache = []
```

---

## 4. 在 `research()` 里优先复用旧 plan
找到原来的：

```plain
plan = self._make_research_plan(query)
```

改成：

```plain
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
else:
    plan = self._make_research_plan(query)
```

---

## 5. 在 `_initial_search_and_summary()` 里优先复用搜索缓存
找到你最终确定 `search_query` 之后、调用 Tavily 之前的位置。

原来可能是：

```plain
search_results = tavily_search(
    search_query,
    max_results=self.config.max_search_results,
    timeout=self.config.search_timeout,
    api_key=self.config.tavily_api_key
)
```

改成：

```plain
cached_results = self.memory.find_search_cache(search_query, threshold=0.92)

if cached_results is not None:
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
```

然后紧接着加：

```plain
self.current_search_cache.append({
    "search_query": search_query,
    "results": search_results or []
})
```

---

## 6. 在 `research()` 成功结束前写入 memory
在最终 `return final_report` 之前加：

```plain
self.memory.upsert_record(
    query=query,
    plan=plan,
    search_cache=self.current_search_cache,
    final_report_summary={
        "summary": final_report[:500],
        "final_length": len(final_report)
    }
)
```

---

# 六、改完之后系统行为
## 第一次跑
+  没有 memory 
+  正常走原流程 
+  跑完后把结果写进 `memory_store.json`

## 第二次跑相同或相似问题
+  命中旧 plan 
+  命中旧 search_cache 
+  减少 Tavily 调用 
+  速度更快一点 

---

# 七、需要验证的结果
技术人员改完后，只需要验证这 4 件事：

## 1.
第一次运行后，目录里生成：

```plain
output/memory/memory_store.json
```

## 2.
第二次运行相同 query 时，trace 里出现：

```plain
memory.plan_hit
memory.search_hit
```

## 3.
第二次运行比第一次少调了一部分 Tavily

## 4.
系统正常出报告，不报错

---

# 八、阈值就用这两个，不要再折腾
直接定死：

```plain
query_threshold = 0.85
search_threshold = 0.92
```

够用了。

---

# 九、这个方案的本质
这不是复杂 memory。  
它就是：

**把已经做过的 plan 和 search 结果存下来，下次别重复做。**

但它已经满足你说的要求：

+  最小改动 
+  只做一次 
+  有 AI memory 效果 
+  不求完美 
+  有效果就行 

---

# 十、给技术人员的最终执行清单
按这个顺序做：

1.  新建 `src/memory.py`
2.  实现 `MemoryStore`
3. `agent.py` 引入 `MemoryStore`
4. `__init__()` 增加： 
    - `self.memory`
    - `self.current_search_cache`
5. `research()` 开头清空 `self.current_search_cache`
6. `research()` 里给 `plan` 增加 memory 命中逻辑 
7. `_initial_search_and_summary()` 里给 `search_results` 增加 memory 命中逻辑 
8. `research()` 结束前调用 `self.memory.upsert_record(...)`

这就是最终方案。

优先复用旧 plan

对于memory我还没有改动呢，所以你说优先服用旧的plan是什么意思？我还没有把任何一版改动memory的方案发给别人过。所以请你站在一个第一次见到改动memory这个方案的角度重新写一版

Thought for a couple of seconds

明白了。这里我重新按**第一次做 memory** 来写，不假设你已经做过任何 memory 改动。

“优先复用旧 plan”的意思不是说你现在已经有旧 plan 了，而是说：

**等你把 memory 功能加上以后，系统第一次运行会先把 plan 存起来；第二次再遇到相同或相似问题时，才有“旧 plan”可以复用。**

也就是说：

+ **第一次运行**：没有任何 memory，正常生成 plan、正常搜索、正常出报告，同时把这些内容存下来 
+ **后面的运行**：如果问题相似，才尝试从 memory 里拿以前存过的 plan 或搜索结果 

所以你现在要做的是：**先把“存”和“取”的能力加进去**。  
下面这版就是从零开始、第一次见到 memory 方案时该给技术人员的版本。

---

# 最小改动 AI Memory 方案（从零开始版）
## 目标
在现有项目中增加一个**最小可用 memory**，让系统具备最基本的“记住以前做过什么”的能力。

达到的效果：

+  第一次运行某个问题时，正常执行全流程 
+  运行结束后，把关键结果保存到本地 
+  第二次运行相同或相似问题时，优先尝试使用之前保存过的内容 
+  尽量减少重复搜索和重复生成 

不追求复杂，不追求完美，只要：

+  能存 
+  能取 
+  有一点效果 
+  不容易报错 

---

# 一、这次 memory 到底存什么
第一次做 memory，只存 3 类东西：

## 1. 用户问题
例如：

```plain
AI agent 在教育中的应用
```

## 2. 这次生成的 plan
例如：

```plain
{
  "goal": "...",
  "dimensions": ["背景", "问题", "案例", "趋势"]
}
```

## 3. 这次做过的搜索
例如：

```plain
[
  {
    "search_query": "AI agent education overview",
    "results": [...]
  }
]
```

这就够了。

---

# 二、第一次运行和第二次运行分别发生什么
## 第一次运行
因为还没有 memory，所以：

1.  正常生成 plan 
2.  正常搜索 
3.  正常出报告 
4.  结束时把这次的： 
    -  query 
    -  plan 
    -  search cache  
存到本地 JSON 文件里 

## 第二次运行相同或相似问题
这时候 memory 已经有内容了，所以：

1.  先查历史里有没有相似 query 
2.  如果找到，就可以直接拿它之前存的 plan 
3.  搜索前，先查历史里有没有相似 search_query 
4.  如果找到，就直接用旧搜索结果 
5.  没找到再正常调用 Tavily 

---

# 三、这次只改两个文件
## 新增
```plain
src/memory.py
```

## 修改
```plain
src/agent.py
```

---

# 四、memory 存在哪
建议存在你原来的输出目录下：

```plain
output/memory/memory_store.json
```

---

# 五、memory 文件长什么样
```plain
{
  "records": [
    {
      "query": "AI agent 在教育中的应用",
      "query_normalized": "ai agent 在教育中的应用",
      "plan": {
        "goal": "写一份关于 AI agent 在教育中的应用的研究报告",
        "dimensions": ["背景", "问题", "案例", "趋势"],
        "search_hints": {},
        "section_requirements": {},
        "risk_points": []
      },
      "search_cache": [
        {
          "search_query": "AI agent education overview",
          "results": [
            {
              "title": "...",
              "url": "...",
              "content": "..."
            }
          ]
        }
      ]
    }
  ]
}
```

---

# 六、新增文件：`src/memory.py`
技术人员直接新建这个文件，并实现下面这个类。

```plain
import json
import os
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional


class MemoryStore:
    def __init__(self, base_dir: str):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)
        self.filepath = os.path.join(self.base_dir, "memory_store.json")

    def _empty_store(self) -> Dict[str, Any]:
        return {"records": []}

    def load_store(self) -> Dict[str, Any]:
        if not os.path.exists(self.filepath):
            return self._empty_store()

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return self._empty_store()

    def save_store(self, store: Dict[str, Any]) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(store, f, ensure_ascii=False, indent=2)

    def normalize_text(self, text: str) -> str:
        return " ".join(text.lower().strip().split())

    def similarity(self, a: str, b: str) -> float:
        return SequenceMatcher(None, self.normalize_text(a), self.normalize_text(b)).ratio()

    def find_similar_query(self, query: str, threshold: float = 0.85) -> Optional[Dict[str, Any]]:
        store = self.load_store()
        best_record = None
        best_score = 0.0

        for record in store["records"]:
            score = self.similarity(query, record.get("query_normalized", record.get("query", "")))
            if score > best_score:
                best_score = score
                best_record = record

        if best_record and best_score >= threshold:
            return best_record
        return None

    def find_search_cache(self, search_query: str, threshold: float = 0.92) -> Optional[List[Dict[str, Any]]]:
        store = self.load_store()
        best_results = None
        best_score = 0.0

        for record in store["records"]:
            for cache in record.get("search_cache", []):
                score = self.similarity(search_query, cache.get("search_query", ""))
                if score > best_score:
                    best_score = score
                    best_results = cache.get("results", [])

        if best_results is not None and best_score >= threshold:
            return best_results
        return None

    def upsert_record(
        self,
        query: str,
        plan: Dict[str, Any],
        search_cache: List[Dict[str, Any]]
    ) -> None:
        store = self.load_store()
        normalized_query = self.normalize_text(query)

        for record in store["records"]:
            if record.get("query_normalized") == normalized_query:
                record["plan"] = plan
                record["search_cache"] = search_cache
                self.save_store(store)
                return

        store["records"].append({
            "query": query,
            "query_normalized": normalized_query,
            "plan": plan,
            "search_cache": search_cache
        })
        self.save_store(store)
```

---

# 七、修改 `src/agent.py`
## 1. 顶部新增 import
```plain
from .memory import MemoryStore
```

---

## 2. 在 `__init__()` 里新增两行
```plain
self.memory = MemoryStore(os.path.join(self.config.output_dir, "memory"))
self.current_search_cache = []
```

---

## 3. 在 `research()` 开头清空本次搜索缓存
```plain
self.current_search_cache = []
```

---

## 4. 在 `research()` 里加“查 memory”的逻辑
### 原来
```plain
plan = self._make_research_plan(query)
```

### 改成
```plain
memory_record = self.memory.find_similar_query(query, threshold=0.85)

if memory_record and memory_record.get("plan"):
    plan = memory_record["plan"]
else:
    plan = self._make_research_plan(query)
```

这里要注意：

+ **第一次运行时**，`memory_store.json` 还是空的 
+  所以 `find_similar_query()` 会返回 `None`
+  系统就会正常走 `_make_research_plan(query)`

这就是“从零开始”的正常行为

---

## 5. 在 `_initial_search_and_summary()` 里加“查搜索缓存”的逻辑
### 原来
```plain
search_results = tavily_search(
    search_query,
    max_results=self.config.max_search_results,
    timeout=self.config.search_timeout,
    api_key=self.config.tavily_api_key
)
```

### 改成
```plain
cached_results = self.memory.find_search_cache(search_query, threshold=0.92)

if cached_results is not None:
    search_results = cached_results
else:
    search_results = tavily_search(
        search_query,
        max_results=self.config.max_search_results,
        timeout=self.config.search_timeout,
        api_key=self.config.tavily_api_key
    )
```

然后在后面加上：

```plain
self.current_search_cache.append({
    "search_query": search_query,
    "results": search_results or []
})
```

注意：

+ **第一次运行时**，因为 memory 里没有任何搜索记录 
+  所以 `cached_results` 会是 `None`
+  系统还是正常调用 Tavily 
+  然后把这次搜索结果记下来 

---

## 6. 在 `research()` 结束前把本次内容写入 memory
在最终返回前加：

```plain
self.memory.upsert_record(
    query=query,
    plan=plan,
    search_cache=self.current_search_cache
)
```

这一步很关键，因为：

+  没有这一步，第一次运行完也不会留下任何 memory 
+  那第二次自然也没法复用 

---

# 八、整个流程现在变成什么样
## 第一次运行
```plain
输入 query
→ memory 里没有
→ 正常生成 plan
→ 正常搜索
→ 正常出报告
→ 把 query / plan / search_cache 存入 memory
```

## 第二次运行
```plain
输入 query
→ 先查 memory
→ 如果 query 相似，就直接拿旧 plan
→ 搜索前先查 memory
→ 如果 search_query 相似，就直接拿旧搜索结果
→ 不够的部分再正常搜索
→ 继续出报告
```

---

# 九、技术人员只需要做这 6 步
1.  新建 `src/memory.py`
2.  实现 `MemoryStore`
3.  在 `agent.py` 里引入 `MemoryStore`
4.  在 `__init__()` 里初始化 `self.memory` 和 `self.current_search_cache`
5.  在 `research()` 开头查 query memory，结束前写入 memory 
6.  在 `_initial_search_and_summary()` 里查 search cache 

---

# 十、怎么判断这套 memory 成功了
只看这三件事：

## 1.
第一次跑完后，目录里出现：

```plain
output/memory/memory_store.json
```

## 2.
第二次跑相同问题时，不会从零开始，而是能复用一部分以前的内容

## 3.
系统仍然正常出报告，不报错

