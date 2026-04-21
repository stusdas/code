### git
1. 开始改代码前 → git add . && git commit -m "改动前的稳定版本"

2. 改一段代码，测试OK → git add . && git commit -m "加了XX功能"  

3. 继续改...

4. 改坏了 → git reset --hard HEAD~1  （回到上一步）

agent.py里面的函数：research，_generate_report_structure，_generate_report_structure， _process_paragraphs，_initial_search_and_summary，_reflection_loop等等，这些函数有对应着步骤？是对应着一个个的文件？ 

你这个问题问到点子上了 👍 ——其实已经触到 **Agent 系统设计的核心思想：流程 vs 模块**。

我直接给你讲清楚结论：

---

# 👉 **DeepResearchAgent = 一个“多智能体协作系统”，用来自动完成复杂任务（尤其是调研/分析类）**
---

# 🧩 它到底在干嘛？
它的核心目标是：

**把一个复杂问题 → 自动拆分 → 分给多个 AI agent → 协作完成 → 输出结果**

比如你让它做：

“帮我调研 AI Agent 最新论文并总结”

它不会直接用一个模型硬答，而是：

### 实际执行流程（重点）
1. **Planning Agent（总指挥）**
    -  先理解任务 
    -  拆成子任务  
👉 “查论文 → 分析 → 总结” 
2. **多个子 Agent 分工**
    -  🔍 Researcher：查资料 
    -  🧠 Analyzer：分析信息 
    -  🌐 Browser：上网抓数据 
    -  🛠 Tool Agent：调用工具/API 
3. **协作执行**
    -  自动串联流程 
    -  结果不断反馈 & 修正 

👉 最终输出一个完整结果（报告 / 答案）

这就是它的核心价值：  
**“自动化复杂任务执行”**

---

# 🏗️ 架构（很关键）
它是典型的 **分层多 Agent 架构**：

## 上层（大脑）
+  Planning Agent（规划 + 调度） 

## 下层（执行者）
+  DeepResearcher（调研） 
+  DeepAnalyzer（分析） 
+  Browser Agent（爬网页） 
+  Tool Agent（调用工具） 

👉 类似：

```plain
老板（Planning）
  ↓
员工A / 员工B / 工具系统
```

这比普通 ChatGPT 强的地方在于：

👉 **不是一次性回答，而是“过程化执行”**

---

# 🚀 它能做什么（实际用途）
这个项目主要适合这些场景：

### 1️⃣ 自动调研（核心）
+  查论文 
+  查资料 
+  生成报告 
+  做综述 

👉 类似 “AI 版研究助理”

---

### 2️⃣ 自动任务执行
比如：

+  写代码 + 调 API 
+  分析数据 
+  调用外部工具 

---

### 3️⃣ Agent 系统开发框架
你也可以拿它来：

+  自己搭 AI Agent 系统 
+  做自动化 workflow 
+  做 AI 产品 

---

# ⚙️ 技术特点（比较硬核）
几个关键点你要注意：

### ✅ 1. 多 Agent 协作
不是单 LLM，而是系统化调度  
👉 更接近 AutoGPT / Devin 思路

---

### ✅ 2. 可扩展
可以加：

+  新 agent 
+  新工具 
+  新模型 

---

### ✅ 3. 支持多模型
+  OpenAI 
+  Anthropic 
+  Google 
+  本地模型 

---

### ✅ 4. 有“自进化”机制
它有 optimizer / memory / tracing：

👉 可以：

+  记录执行过程 
+  反思 
+  优化下一次结果 

（这一点是比较前沿的）

---

# 🧠 本质定位（很重要）
你可以把它理解为：

### ❌ 不是：
+  一个简单 AI 工具 
+  一个聊天机器人 

### ✅ 而是：
👉 **一个 AI 操作系统 / Agent 框架**

---

# 🔥 类比一下更好理解
| 项目 | 类比 |
| --- | --- |
| ChatGPT | 一个聪明的人 |
| DeepResearchAgent | 一个公司（有分工、有流程） |


---

# 🧾 总结
👉 这个项目本质是：

+  一个 **多智能体系统（Multi-Agent System）**
+  专门用来 **自动完成复杂任务**
+  核心能力是： 
    -  任务拆解 
    -  agent 协作 
    -  工具调用 
    -  自动执行

**DeepSearchAgent-Demo = 从0实现的一个“深度搜索Agent示例项目”**

重点是：  
**演示原理，不是工业级系统**

---

# 🧩 它到底在干嘛？
这个项目的核心功能是：

**输入一个问题 → 自动多轮搜索 → 反思优化 → 生成一份研究报告**

---

# 🔍 它的核心流程（很重要）
它不像普通 AI 一次回答，而是一个“循环系统”：

### 整体流程：
1.  用户输入问题 
2.  生成报告结构（大纲） 
3.  对每个段落： 
    -  搜索资料 
    -  写初稿 
    -  反思（发现缺啥） 
    -  再搜索补充 
4.  最终输出完整报告 

👉 本质是：

```plain
问题
 → 拆结构
 → 搜索
 → 总结
 → 反思
 → 再搜索
 → 优化
 → 输出报告
```

这就是所谓的：

👉 **Deep Search（深度搜索）**

---

# ⚙️ 核心特点（和你刚才那个项目对比关键点）
## ✅ 1. “无框架”实现（重点）
这个项目非常强调：

❌ 不用 LangChain / AutoGPT  
✅ 全部自己写

👉 目的：

+  更简单 
+  更透明 
+  更适合学习 Agent 原理 

---

## ✅ 2. 多轮反思机制（核心亮点）
它不是搜一次，而是：

👉 **循环优化内容**

+  找漏洞 
+  补搜索 
+  重写 

👉 这点和 DeepResearchAgent 是同一个思想

---

## ✅ 3. 多模型支持
支持：

+  DeepSeek 
+  OpenAI 

---

## ✅ 4. 集成搜索引擎
+  用 Tavily 做搜索 

---

## ✅ 5. 输出是“研究报告”
不是聊天，而是：

👉 Markdown 报告（结构化、多段落）

---

# 🏗️ 代码结构（程序员重点）
它比你刚看的项目简单很多：

```plain
src/
 ├── agent.py        # 核心Agent
 ├── nodes/          # 各阶段逻辑（搜索、总结、反思）
 ├── llms/           # 模型封装
 ├── tools/          # 搜索工具
 ├── state/          # 状态管理
 ├── prompts/        # 提示词
```

👉 核心是：

一个 Agent + 多个“处理节点（nodes）” 

---

# 🔥 它的定位（非常关键）
## ❌ 不是：
+  完整 AI Agent 系统 
+  复杂多 agent 协作平台 

## ✅ 是：
👉 **一个“Deep Research Agent 的最小实现 Demo”**

---

# 🆚 和你刚才那个项目对比
| 项目 | DeepResearchAgent | DeepSearchAgent-Demo |
| --- | --- | --- |
| 复杂度 | ⭐⭐⭐⭐ | ⭐⭐ |
| 是否多 Agent | ✅ 多 agent协作 | ❌ 单 agent |
| 是否框架化 | 偏工程化 | 极简 |
| 用途 | 产品 / 系统 | 学习 / Demo |
| 核心思想 | 多 agent orchestration | 单 agent + 反思循环 |


---

# 🧠 更直白一点
你可以这样理解：

+  DeepResearchAgent  
👉 **公司级 AI 系统（多人协作）**
+  DeepSearchAgent-Demo  
👉 **一个聪明实习生（自己查资料 + 写报告）**

---

# 🧾 总结
👉 这个项目本质是：

+  一个 **“从0实现的深度搜索 Agent Demo”**
+  用来展示： 
    -  多轮搜索 
    -  反思机制 
    -  报告生成 
+  非常适合： 
    -  学习 Agent 原理 
    -  自己改造/二开

**第一个项目是一个更加复杂的项目，第二项目是一个稍微简单的项目，我想对第二个项目进行二创**



这个方向是对的，而且说实话——**从第二个 Demo 下手二创，比直接改第一个项目聪明很多**。

不过我先给你泼一点冷水（友好版）👇  
👉 **这个 Demo 虽然“看起来简单”，但它已经是一个完整 Agent pipeline 了**  
你要二创，不是“加点功能”，而是要**动流程设计**。

下面我帮你把路子讲清楚。

---

# 🧠 一、你到底在“改什么”？（关键认知）
你要改的不是某个函数，而是这条链：

```plain
research()
 → 生成大纲
 → 逐段处理
 → 搜索
 → 总结
 → 反思
 → 再搜索
 → 输出
```

👉 **二创本质 = 改这条 pipeline**

---

# 🏗️ 二、推荐你改的 5 个方向（从简单到高级）
我按“性价比”给你排好了 👇

---

## ✅ 方向1：改搜索策略（最容易、最实用）
现在大概率是：

```plain
关键词 → 搜一次 → 总结
```

你可以升级成：

### 🔥 改进点
+  多 query 并行搜索 
+  query rewrite（自动改写搜索词） 
+  加时间过滤（最新论文） 
+  分源搜索（论文 / 新闻 / 博客） 

👉 改哪里：

+ `_initial_search_and_summary`
+ `tools/search`

👉 价值：  
**效果立竿见影**

---

## ✅ 方向2：改“反思机制”（核心升级）
现在的 `_reflection_loop` 通常是：

```plain
模型：这段哪里不好？
→ 再补搜索
```

你可以改成：

### 🔥 更强版本
+  拆成多个 critic： 
    -  factual critic（事实） 
    -  coverage critic（覆盖面） 
    -  logic critic（逻辑） 
+  或者： 
    -  给评分（score-based refinement） 

👉 改哪里：

+ `_reflection_loop`

👉 价值：  
👉 这是“从玩具 → 稍微像产品”的关键

---

## ✅ 方向3：改“结构生成”（非常重要）
现在：

```plain
_generate_report_structure → LLM 一次生成大纲
```

问题：  
👉 很容易垃圾结构

---

### 🔥 你可以做：
+  iterative outline（多轮优化大纲） 
+  retrieval-aware outline（先搜再生成结构） 
+  用户可控结构（比如指定格式） 

👉 改哪里：

+ `_generate_report_structure`

👉 价值：  
👉 决定最终报告质量上限

---

## ✅ 方向4：并行化（工程提升）
现在流程大概率是：

```plain
for paragraph in paragraphs:
    逐个处理
```

👉 你可以改成：

### 🔥 并发执行
+  asyncio / thread pool 
+  每段同时跑 

👉 改哪里：

+ `_process_paragraphs`

👉 价值：  
👉 性能直接提升一个量级

---

## ✅ 方向5：变成“多 Agent”（进阶玩法）
现在是：

👉 单 Agent + 多函数

你可以升级成：

```plain
Planner Agent
Research Agent
Writer Agent
Critic Agent
```

👉 本质就是向第一个项目靠拢

👉 改哪里：

+  把函数拆成 agent class 

👉 价值：  
👉 这是最接近“工业级”的改法

---

# 🧠 三、推荐你一个“最优二创路径”（别乱改）
我给你一个很实用的路线：

---

## 🚀 Step 1（必做）
👉 读懂这 3 个函数：

+ `research`（主流程） 
+ `_process_paragraphs`
+ `_reflection_loop`

---

## 🚀 Step 2（优先改）
👉 改这两个：

1. `_initial_search_and_summary`
2. `_reflection_loop`

👉 这是效果提升最大、改动最小的地方

---

## 🚀 Step 3（再升级）
👉 加一个新模块：

```plain
def multi_query_search(query):
    queries = rewrite(query)
    results = []
    for q in queries:
        results += search(q)
    return results
```

---

## 🚀 Step 4（可选）
👉 并发执行段落

---

# 🧨 四、你千万别踩的坑
### ❌ 1. 一上来就改 agent.py 全流程
👉 会直接炸（逻辑链太长）

---

### ❌ 2. 只改 prompt 不改逻辑
👉 提升有限

---

### ❌ 3. 乱加 Agent
👉 没有调度系统会变乱

---

# 🧠 五、给你一个“二创定位建议”（很重要）
你可以选一个明确方向：

### 🧪 学术方向
👉 做“论文调研 Agent”

---

### 🧰 工具方向
👉 做“自动写报告工具”

---

### 🤖 Agent方向
👉 做“轻量多 Agent 框架”

---

# 🧾 总结
👉 第二个项目适合二创，因为：

+  结构清晰（pipeline） 
+  没有复杂框架 
+  每一步都可替换 

👉 二创核心不是“加功能”，而是：

**重构 pipeline 的某一段能力**

** | 函数 | 对应现实步骤 | | --------------------------- | ------ | | research | 开始做论文 | | _generate_report_structure | 列大纲 | | _process_paragraphs | 写每一段 | | _initial_search_and_summary | 查资料写初稿 | | _reflection_loop | 修改润色 | **👉** 这些是“步骤”，不是“文件” 这里流程里面的步骤可能会用到： 模块可替换比如： 换搜索引擎 → 改 tools 换模型 → 改 llms 换 prompt → 改 prompts 这些东西对吧 然后我要改的话改哪里？改流程还是改模块  **

****

对，你理解得对。

**流程****是“先做什么、后做什么”。  
****模块****是“这一步具体怎么做”。**

**所以你要改哪里，取决于你想改的是：**

### **1. 只想让效果变好，但整体工作流不变**
**那就****优先改模块****，不要先动流程。**

**比如：**

+ ** 搜得不够准 → 改 **`**tools**`
+ ** 总结写得不好 → 改 **`**llms**`** / **`**prompts**`
+ ** 反思提示不够强 → 改 **`**prompts**`
+ ** 结果格式不满意 → 改生成文本的 prompt 或输出模块 **

**这个思路最稳，因为：**

+ ** 风险小 **
+ ** 容易测试 **
+ ** 不容易把整条链改崩 **

---

### **2. 想让系统“做事方式”变了**
**那就要****改流程****。**

**比如你想把现在的：**

```plain
先生成大纲
→ 每段搜一次
→ 每段反思
→ 输出
```

**改成：**

```plain
先粗搜全局资料
→ 再生成大纲
→ 每段并行处理
→ 最后统一总审
```

**这就不是模块替换了，这是****pipeline 重构****。**

---

## **最实用的判断标准**
**你可以用一句话判断：**

### **如果你问的是：**
**“这一步还用原来的顺序，只是做得更好一点吗？”****  
****那改****模块**

### **如果你问的是：**
**“这一步该不该提前、合并、拆开、增加、删除？”****  
****那改****流程**

---

# **对你现在这个二创，我建议这样做**
## **第一阶段：先改模块**
**因为你现在是在二创一个 Demo，不建议一上来重写流程。**

**优先改这几类：**

### **改搜索**
**位置通常是：**

+ `**tools/search...**`
+ `**_initial_search_and_summary**`** 里调用搜索的地方 **

**你可以做：**

+ ** 多 query 搜索 **
+ ** 去重 **
+ ** 按时间筛选 **
+ ** 按来源筛选 **

---

### **改模型调用**
**位置通常是：**

+ `**llms/...**`
+ ** 各函数里调 LLM 的封装层 **

**你可以做：**

+ ** 换模型 **
+ ** 区分“写作模型”和“反思模型” **
+ ** 加 temperature / max tokens 控制 **

---

### **改 prompts**
**位置通常是：**

+ `**prompts/...**`
+ ** 或函数内部拼 prompt 的地方 **

**你可以做：**

+ ** 让大纲更稳定 **
+ ** 让总结更像报告 **
+ ** 让 reflection 更严格 **

---

## **第二阶段：再小改流程**
**等你把模块改顺了，再动流程。**

**最值得改的流程点通常有 3 个：**

### **A. 改大纲生成时机**
**现在可能是先大纲再搜索。  
****你可以改成先做一次全局搜索，再出大纲。**

### **B. 改 paragraph 处理方式**
**现在可能是串行逐段写。  
****你可以改成并行，或者先全部搜资料再分别写。**

### **C. 改 reflection 的层级**
**现在可能是“每段自己反思”。  
****你可以加一个“全文总反思”。**

---

# **给你一个非常明确的建议**
## **你现在最应该做的是：**
**先改模块，后改流程。**

**原因很简单：**

+ ** Demo 项目里，流程是骨架 **
+ ** 模块是器官 **
+ ** 一开始先换器官，比先拆骨架安全得多 **

---

# **我建议你的实际改法**
## **最稳路线**
### **第一步**
**先不动 **`**research()**`** 主流程**

### **第二步**
**改这两个点：**

+ `**_initial_search_and_summary**`
+ `**_reflection_loop**`

**因为这两个地方最影响质量**

---

## **具体分工可以这样看**
### **流程层**
**这些地方一般负责“编排”：**

+ `**research**`
+ `**_generate_report_structure**`
+ `**_process_paragraphs**`
+ `**_reflection_loop**`** 的循环结构本身 **

**你改这里，就是在改步骤顺序或阶段设计。**

---

### **模块层**
**这些地方一般负责“能力实现”：**

+ `**tools**`
+ `**llms**`
+ `**prompts**`
+ ** 某些 **`**nodes**`

**你改这里，就是在改某一步的具体执行质量。**

---

# **一句话结论**
**先改模块，因为这是“同样流程下提升效果”；  
****等你跑通并理解了，再改流程，因为那是在“重新设计 Agent”。**

**你现在最适合的做法是：**

1. ** 不动主流程 **
2. ** 先升级搜索模块 **
3. ** 再升级 reflection prompt 或逻辑 **
4. ** 最后再考虑重构流程 **

**如果你愿意，我可以下一步直接帮你把这个项目拆成两张表：哪些文件属于流程层，哪些文件属于模块层。**

****

如果我想用一点点项目1的工作去改项目2，怎么改？我没有想法

**我先对照这两个仓库的结构，给你一条“能落地、改动不至于太炸”的迁移路线。重点会放在：从项目1借什么思想最值、放到项目2的哪里最自然。**

**Thought for 5s**

**可以，而且****最稳的做法不是把项目1整套搬过来****，而是只借它的 ****“规划层思想”****，塞进项目2现有流程里。项目1本质上是“顶层 planning agent + 多个下层专用 agent”的分层多智能体系统；项目2则是一个更简洁的 deep search pipeline。**

**你现在最适合的方向是：**

**不要把项目2改成“完整多 Agent”****，  
****而是改成：**

**单主 Agent + 一个轻量 Planner 层 + 原有搜索/总结/反思执行层**

**这算“借项目1的一点点工作”，但又不会把项目2改炸。**

---

## **你可以直接借项目1的 3 个思想**
### **1. 先规划，再执行**
**项目1最核心的是：先由顶层 agent 做任务理解、拆解、分配，再让下层 agent 执行。**

**放到项目2里，就变成：**

**原来大概是：**

```plain
research
→ 生成报告结构
→ 每段搜索
→ 每段总结
→ 每段反思
→ 输出
```

**你可以改成：**

```plain
research
→ planner 先生成“执行计划”
→ 再生成报告结构
→ 按计划处理每段
→ 每段搜索/总结/反思
→ 全文总审
→ 输出
```

**这里新增的不是大系统，只是一个很轻的步骤：**

`**_make_research_plan(query)**`

**它输出的不是最终大纲，而是：**

+ ** 研究目标 **
+ ** 重点维度 **
+ ** 每段要回答什么 **
+ ** 哪些段落需要更多证据 **
+ ** 搜索优先级 **

**这一步非常像项目1里的 planning，只不过你把它压缩成一个函数。**

---

### **2. 让“段落处理”带角色意识**
**项目1强调 specialized lower-level agents，也就是不同角色干不同的事。**

**你不用真的建四五个 agent。  
****你只要在项目2里做“伪多 Agent”就够了：**

**把原来的一个 **`**_process_paragraphs**`**，拆成 3 类角色函数：**

+ `**researcher_step**`**：只负责搜资料 **
+ `**writer_step**`**：只负责写段落 **
+ `**critic_step**`**：只负责挑毛病 **

**这样做的本质是：  
****函数级角色分离，而不是系统级 agent 分离。**

**这是最适合二创的方式。**

---

### **3. 加一个“全文级反思”**
**项目2本来就偏重搜索、总结、反思循环；这一点从它的 README 和节点结构就能看出来。**

**但很多 Demo 只做到“段落级反思”，没有真正的“全局规划 + 全文审校”。**

**你可以借项目1的层级感，新增一个：**

`**_global_review(report, plan)**`

**它负责检查：**

+ ** 各段有没有重复 **
+ ** 有没有漏掉计划里的关键点 **
+ ** 逻辑顺序顺不顺 **
+ ** 结论有没有和前文证据对齐 **

**这个改动很像项目1里“上层 agent 对下层结果做再组织”，但实现很轻。**

---

## **最推荐你的改法：只加一层 Planner**
**这是最值的版本。**

### **你现在的项目2流程**
```plain
research(query):
    structure = _generate_report_structure(query)
    paragraphs = _process_paragraphs(structure)
    return merge(paragraphs)
```

### **你可以改成**
```plain
research(query):
    plan = _make_research_plan(query)
    structure = _generate_report_structure(query, plan)
    paragraphs = _process_paragraphs(structure, plan)
    draft = merge(paragraphs)
    final = _global_review(draft, plan)
    return final
```

---

## **这样改时，每个函数做什么**
### `**_make_research_plan(query)**`
**借项目1的 planning 思想，但做轻量版。**

**输出例子：**

```plain
{
  "goal": "写一份关于 XXX 的研究报告",
  "dimensions": [
    "背景与定义",
    "现状与关键问题",
    "代表性案例",
    "趋势与争议"
  ],
  "search_hints": {
    "背景与定义": ["XXX 是什么", "XXX overview"],
    "现状与关键问题": ["XXX latest challenges", "XXX recent developments"]
  },
  "risk_points": ["容易空话", "需要最新资料支撑"]
}
```

### `**_generate_report_structure(query, plan)**`
**不是直接凭空列大纲，而是参考 plan 生成更稳的结构。**

### `**_process_paragraphs(structure, plan)**`
**每段处理时，读取对应的 **`**search_hints**`** 和 **`**dimension goal**`**。**

### `**_global_review(draft, plan)**`
**检查最终稿是否覆盖 plan 里的所有重点。**

---

## **你改代码时，先动哪些地方**
### **第一优先级**
**改 **`**research**`**  
****新增 **`**_make_research_plan**`**  
****让 **`**_generate_report_structure**`** 接收 **`**plan**`

**这是最小可落地闭环。**

---

### **第二优先级**
**改 **`**_process_paragraphs**`**  
****让每段不再“盲搜”，而是“按计划搜”**

**比如：**

```plain
for section in structure.sections:
    hints = plan.search_hints.get(section.title, [])
    paragraph = self._initial_search_and_summary(section, hints=hints)
```

**这样效果会明显比“只拿段落标题去搜”更好。**

---

### **第三优先级**
**在 **`**_reflection_loop**`** 之外，加一个 **`**_global_review**`

**这会让你的项目2开始有一点项目1那种“层级调度感”。**

---

## **你先别借项目1的这些东西**
**下面这些对你现在来说，收益没那么高，复杂度却上升很快：**

### **不建议一开始就借**
+ ** 真正多 agent 调度 **
+ ** 太复杂的工具调用系统 **
+ ** 完整 memory / trace / optimizer **
+ ** 太重的异步并行 orchestration **

**项目1是 hierarchical multi-agent system，适合复杂通用任务；而项目2是简洁 deep search agent。你现在如果直接照搬项目1的完整架构，项目2会从“好改的 Demo”变成“半残的复杂系统”。**

---

## **我替你定一个最稳的“二创主题”**
**你可以把你的版本定位成：**

**Plan-and-Review DeepSearchAgent**

**也就是：**

+ ** 保留项目2的简洁搜索报告流 **
+ ** 借项目1的 planning 思想 **
+ ** 加一个全局 review 层 **

**这个方向特别适合你现在的阶段，因为：**

+ ** 改动不大 **
+ ** 逻辑清晰 **
+ ** 很像“从 Demo 升级成稍微成熟一点的系统” **

---

## **一句话说透**
**不要把项目1的“多 Agent 形态”搬过来，先搬它的“先规划、再执行、最后总审”的思想。**

**这样你实际要做的只有三件事：**

1. ** 新增 **`**plan**`
2. ** 让大纲和段落处理都参考 **`**plan**`
3. ** 新增 **`**global review**`

**这就是最自然、最稳、也最像“借项目1去升级项目2”的方式。**

**如果你愿意，我下一条可以直接帮你画出这版二创后的****函数调用图****，并告诉你每个函数该改什么参数。**

**你的意思是： research → 生成报告结构 → 每段搜索 → 每段总结 → 每段反思 → 输出 可以改成： research → planner 先生成“执行计划” → 再生成报告结构 → 按计划处理每段 → 每段搜索/总结/反思 → 全文总审 → 输出 画出这版二创后的函数调用图，并告诉每个函数该改什么参数。**

**Thought for a few seconds**

**对，就是这个意思。**

**我直接给你一版****能落地的函数调用图****，然后把每个函数该加什么参数、参数是干嘛的，都列清楚。**

---

# **二创后的函数调用图**
```plain
research(query, config=None)
│
├── _make_research_plan(query, config=None)
│     └── 输出 plan
│
├── _generate_report_structure(query, plan, config=None)
│     └── 输出 structure
│
├── _process_paragraphs(structure, plan, config=None)
│     │
│     ├── for section in structure.sections:
│     │
│     ├── _initial_search_and_summary(
│     │       query=query,
│     │       section=section,
│     │       plan=plan,
│     │       search_hints=plan.search_hints[section.title],
│     │       config=config
│     │   )
│     │     └── 输出 initial_draft, search_results
│     │
│     ├── _reflection_loop(
│     │       query=query,
│     │       section=section,
│     │       draft=initial_draft,
│     │       evidence=search_results,
│     │       plan=plan,
│     │       config=config
│     │   )
│     │     └── 输出 refined_paragraph
│     │
│     └── 收集所有 refined_paragraph
│
├── _merge_paragraphs(paragraphs, structure, plan)
│     └── 输出 full_draft
│
├── _global_review(
│       query=query,
│       draft=full_draft,
│       structure=structure,
│       plan=plan,
│       config=config
│   )
│     └── 输出 final_report
│
└── return final_report
```

---

# **你可以怎么理解这条新链**
**原来是：**

```plain
问题 -> 大纲 -> 分段写 -> 每段修 -> 输出
```

**现在是：**

```plain
问题 -> 先做计划 -> 再列大纲 -> 按计划分段写 -> 全文审查 -> 输出
```

**所以新增的核心只有两个：**

+ `**plan**`
+ `**global_review**`

---

# **每个函数该改什么参数**
**我按“旧函数 / 新函数”给你拆。**

---

## **1. **`**research**`
### **原来**
```plain
def research(self, query: str):
    ...
```

### **建议改成**
```plain
def research(self, query: str, config: dict | None = None):
    ...
```

### **新增参数**
#### `**config**`
**用来统一控制整个流程，比如：**

+ ** 最大搜索轮数 **
+ ** 每段最多反思几次 **
+ ** 模型选择 **
+ ** 是否启用全文总审 **

### **为什么加**
**因为后面所有子函数都可能要共享这些设置。  
****你不想每个函数都单独写一堆硬编码。**

---

## **2. **`**_make_research_plan**`
### **新增函数**
```plain
def _make_research_plan(self, query: str, config: dict | None = None) -> dict:
    ...
```

### **输入参数**
#### `**query**`
**用户问题本身。**

#### `**config**`
**控制 planner 的行为，比如：**

+ ** plan 要生成几个维度 **
+ ** 是否强调时间敏感信息 **
+ ** 是否要求加入案例/对比/趋势 **

### **输出建议**
**返回一个 **`**plan**`**，格式可以先简单一点：**

```plain
plan = {
    "goal": "...",
    "dimensions": [
        "背景",
        "核心问题",
        "案例",
        "趋势"
    ],
    "search_hints": {
        "背景": ["xxx 是什么", "xxx overview"],
        "核心问题": ["xxx challenges", "xxx issues"]
    },
    "section_requirements": {
        "背景": "定义清楚概念，不展开争议",
        "核心问题": "至少列出 3 个问题"
    },
    "risk_points": [
        "容易空泛",
        "需要最新资料",
        "需要案例支撑"
    ]
}
```

### **作用**
**它不是报告内容，而是“施工图”。**

---

## **3. **`**_generate_report_structure**`
### **原来**
```plain
def _generate_report_structure(self, query: str):
    ...
```

### **改成**
```plain
def _generate_report_structure(
    self,
    query: str,
    plan: dict,
    config: dict | None = None
):
    ...
```

### **新增参数**
#### `**plan**`
**最关键的新参数。**

**因为现在大纲不能只靠 query 瞎生，要参考：**

+ ** plan 里的 **`**dimensions**`
+ ** 每部分的目标 **
+ ** 每部分需要什么证据 **

#### `**config**`
**控制大纲长度、层级深度等。**

### **你在函数里怎么用**
**比如以前 prompt 是：**

**请根据 query 生成报告大纲**

**现在改成：**

**请根据 query 和以下研究计划生成报告大纲，优先覆盖 plan.dimensions 中的维度，并满足 section_requirements。**

---

## **4. **`**_process_paragraphs**`
### **原来**
```plain
def _process_paragraphs(self, structure):
    ...
```

### **改成**
```plain
def _process_paragraphs(
    self,
    query: str,
    structure,
    plan: dict,
    config: dict | None = None
):
    ...
```

### **新增参数**
#### `**query**`
**后面段落搜索和反思时常常还要用到原始问题。**

#### `**plan**`
**让每段处理不是“只看标题”，而是“看计划中的这一段该写什么”。**

#### `**config**`
**控制每段处理策略，比如：**

+ ** 是否并发 **
+ ** 每段最多引用多少搜索结果 **
+ ** 是否强制每段反思 **

### **作用**
**这是整个升级里最关键的函数之一。  
****因为这里决定了“按计划处理每段”是不是真的落地。**

---

## **5. **`**_initial_search_and_summary**`
### **原来**
**可能像这样：**

```plain
def _initial_search_and_summary(self, section):
    ...
```

### **改成**
```plain
def _initial_search_and_summary(
    self,
    query: str,
    section,
    plan: dict,
    search_hints: list[str] | None = None,
    config: dict | None = None
):
    ...
```

### **新增参数**
#### `**query**`
**原始总问题。**

#### `**section**`
**当前正在写的段落/章节。**

#### `**plan**`
**用于读取这一段的目标和要求。**

#### `**search_hints**`
**这是最实用的新参数。**

**比如：**

```plain
search_hints = plan["search_hints"].get(section.title, [])
```

**这样搜索时就不只是搜 **`**section.title**`**，而是搜：**

+ ** 段落标题 **
+ ** planner 给的提示词 **
+ ** 原始 query 的上下文 **

#### `**config**`
**控制：**

+ ** 搜几轮 **
+ ** 每轮取几个结果 **
+ ** 是否做去重/重排 **

### **建议输出**
**不要只返回一个 draft，建议返回两个东西：**

```plain
return initial_draft, search_results
```

**或者更规范一点：**

```plain
return {
    "draft": initial_draft,
    "evidence": search_results,
    "queries_used": queries_used
}
```

### **为什么**
**因为后面的 **`**_reflection_loop**`** 需要证据，不然它只能对着文字空反思。**

---

## **6. **`**_reflection_loop**`
### **原来**
```plain
def _reflection_loop(self, section, draft):
    ...
```

### **改成**
```plain
def _reflection_loop(
    self,
    query: str,
    section,
    draft: str,
    evidence: list,
    plan: dict,
    config: dict | None = None
):
    ...
```

### **新增参数**
#### `**query**`
**确保反思时不偏题。**

#### `**section**`
**当前段落对象。**

#### `**draft**`
**当前初稿。**

#### `**evidence**`
**这次一定要加。  
****因为 reflection 最怕“只挑文风，不看事实”。**

**有了 **`**evidence**`** 之后，它可以检查：**

+ ** 有没有漏掉搜索结果中的关键信息 **
+ ** 有没有和证据不一致 **
+ ** 有没有该引用但没引用的点 **

#### `**plan**`
**用来检查“这段是否满足计划要求”。**

**比如：**

+ ** 这一段是不是应该包含案例 **
+ ** 这一段是不是应该强调趋势 **
+ ** 这一段是不是应该避免展开背景 **

#### `**config**`
**控制反思轮数、评分阈值等。**

### **你可以让它输出什么**
```plain
return refined_paragraph
```

**或者更完整：**

```plain
return {
    "paragraph": refined_paragraph,
    "reflection_notes": notes,
    "score": score
}
```

---

## **7. **`**_merge_paragraphs**`
### **原来**
**可能就是简单拼接。**

### **建议改成**
```plain
def _merge_paragraphs(
    self,
    paragraphs: list[str],
    structure,
    plan: dict
) -> str:
    ...
```

### **新增参数**
#### `**structure**`
**保证拼接顺序和标题层级正确。**

#### `**plan**`
**在合并时可以顺便检查：**

+ ** 有没有某个 planned dimension 完全没出现 **
+ ** 段落顺序是否和计划一致 **

### **为什么要改**
**虽然这不是最重要的函数，但它是连接“分段写”和“全文审”的桥。**

---

## **8. **`**_global_review**`
### **新增函数**
```plain
def _global_review(
    self,
    query: str,
    draft: str,
    structure,
    plan: dict,
    config: dict | None = None
) -> str:
    ...
```

### **输入参数**
#### `**query**`
**确保全文仍然围绕原问题。**

#### `**draft**`
**完整初稿。**

#### `**structure**`
**用来检查章节结构是否一致。**

#### `**plan**`
**这是核心。**

**因为全文审查的标准不是“写得顺不顺”，而是：**

+ ** 是否覆盖了 plan 的维度 **
+ ** 是否满足 plan 的 section requirements **
+ ** 是否避开了 risk points **

#### `**config**`
**控制：**

+ ** 是否做一次全文重写 **
+ ** 只做审查还是审查后改写 **
+ ** 是否输出 review notes **

### **这个函数的职责**
**检查 4 类东西：**

#### **覆盖性**
**有没有漏掉 plan 里的重点。**

#### **重复性**
**不同段落是不是在说同样的话。**

#### **连贯性**
**段落之间有没有断裂。**

#### **结论一致性**
**结论是否真的被前文证据支持。**

---

# **参数传递关系，你可以这样写**
```plain
def research(self, query: str, config: dict | None = None):
    plan = self._make_research_plan(query, config=config)

    structure = self._generate_report_structure(
        query=query,
        plan=plan,
        config=config,
    )

    paragraphs = self._process_paragraphs(
        query=query,
        structure=structure,
        plan=plan,
        config=config,
    )

    draft = self._merge_paragraphs(
        paragraphs=paragraphs,
        structure=structure,
        plan=plan,
    )

    final_report = self._global_review(
        query=query,
        draft=draft,
        structure=structure,
        plan=plan,
        config=config,
    )

    return final_report
```

---

# **你最少需要改哪些函数签名**
**如果你想先做“最小可运行版本”，只改这几个就够了：**

```plain
research(query, config=None)

_make_research_plan(query, config=None)

_generate_report_structure(query, plan, config=None)

_process_paragraphs(query, structure, plan, config=None)

_initial_search_and_summary(query, section, plan, search_hints=None, config=None)

_reflection_loop(query, section, draft, evidence, plan, config=None)

_global_review(query, draft, structure, plan, config=None)
```

---

# **你可以先分两步改**
## **第一步，先让它跑起来**
**只新增：**

+ `**_make_research_plan**`
+ `**_global_review**`

**并且只给旧函数多传一个 **`**plan**`

**这样你先把骨架接上。**

---

## **第二步，再把每段处理做细**
**把 **`**_initial_search_and_summary**`** 和 **`**_reflection_loop**`** 真的改成“按计划处理”。**

**这个时候效果才会明显提升。**

---

# **最后我帮你压成一句话**
**这版二创最核心的变化就是：**

**从“query 驱动的段落写作”变成“plan 驱动的段落写作”。**

**所以参数层面最重要的新变量只有一个：**

## `**plan**`
**它会一路往下传：**

+ ** 传给大纲生成 **
+ ** 传给段落处理 **
+ ** 传给段落反思 **
+ ** 传给全文总审 **

**它就是你从项目1借来的“轻量 planning 层”。**

