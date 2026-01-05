抱歉，我明白你的意思了。在重构页面结构（将 `index.html` 移动到 `pages/ai_sec_conf.html`）的过程中，可能导致了数据文件路径引用的失效，使得页面变为了“空壳”。同时，论文抓取确实目前只做到了“静态展示”，还没实现真正的“抓取”。

我将分两步彻底解决这些问题：

### 1. 修复 AI+安全会议页面内容 (数据路径修正)

**问题诊断**：
之前 `index.html` 在根目录，引用数据是 `fetch('data/conferences.json')`。
现在它变成了 `pages/ai_sec_conf.html`，在 `pages/` 目录下，引用路径需要改为 `fetch('../data/conferences.json')`。同理，`arch_conf.html` 也需要检查路径。

**行动**：
*   修改 `pages/ai_sec_conf.html` 中的 JS 请求路径，确保能正确读取到 `../data/conferences.json`。
*   同时检查 `pages/arch_conf.html` 确保其路径也是正确的 `../data/arch_conf.json`。

### 2. 实现真正的论文抓取 (arXiv API + 自动化)

**方案设计**：
为了实现你想要的“实时抓取相关论文”，我将编写一个 Python 脚本 `scripts/fetch_papers.py`。

*   **数据源**：使用 **arXiv API**。这是一个免费且权威的计算机科学论文源。
*   **筛选策略**：
    *   **关键词**：针对你的方向，定义一组关键词，例如 `(cat:cs.CR AND (ti:"LLM" OR ti:"Large Language Model" OR ti:"Adversarial"))` 用于 AI+安全，以及 `(cat:cs.AR OR cat:quant-ph)` 用于体系结构/超导。
    *   **时效性**：只抓取最近 24-48 小时的论文。
*   **总结功能**：
    *   *理想情况*：调用 LLM API (GPT/DeepSeek) 生成中文摘要。
    *   *无 Key 情况（当前）*：为了保证脚本现在就能跑通，我会先实现一个**基于规则的“伪总结”**（提取 Abstract 的前两句 + 翻译占位符），或者直接展示原始 Abstract。**代码结构中会预留 `def summarize_with_llm(text)` 接口**，你填入 Key 就能立刻升级为 AI 总结。
*   **更新逻辑**：
    *   脚本运行后，读取现有的 `data/papers.json`。
    *   将新抓取的论文插入头部。
    *   保留最新的 N 篇（例如 50 篇），防止文件无限膨胀。
    *   保存回 JSON。

**自动化**：
*   更新 `.github/workflows/daily-update.yml`，增加一步 `Run paper fetcher`，让 GitHub Actions 每天不仅更新会议时间，还顺便帮你抓最新的论文。

### 3. 执行顺序

1.  **Fix**: 修正 HTML 中的 fetch 路径，立刻恢复页面显示。
2.  **Code**: 编写 `scripts/fetch_papers.py`。
3.  **Config**: 更新 GitHub Actions 配置文件。

这样既修好了显示问题，又补上了真正的后端抓取能力。