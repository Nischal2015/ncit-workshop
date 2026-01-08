## 2 – Deep Research (Multi-Agent LangGraph Demo)

This folder contains the **Deep Research** example used in the workshop. It shows how to build a small multi-agent system with **LangGraph**, **OpenAI**, and **Tavily** that plans research, runs multiple web-search loops, and then synthesizes a final report.

### What this example does

- Takes a high-level `topic` (e.g. *"Comparison of M4 Apple Silicon vs NVIDIA Blackwell for AI Inference"*).
- Uses a **Planner agent** to break the topic into 3 focused sub-questions.
- For each sub-question, spawns a **Child Research graph** that:
	- runs several Tavily web searches (`search_step`),
	- evaluates if the findings are sufficient (`evaluate_step`),
	- optionally refines the query and loops up to 3 times.
- Collects all findings and passes them to a **Writer agent** that generates a structured final report.

All of this coordination is wired together using LangGraph `StateGraph` and `Command` objects.

### Files in this folder

- `deep_research.py` – Main example script and LangGraph definitions (planner, researcher, writer) plus a `__main__` entry point to run the demo.
- `1.ipynb` – Notebook version of the example (step‑by‑step / interactive walk‑through).
- `.langgraph_api/` – Checkpoints and vector store used by LangGraph during runs (automatically created; you normally don’t edit these by hand).

### How the graph is structured

**Child research graph (`ResearchState`)**
- `search_step` – Calls Tavily (`tavily.search`) with the current query, appends the textual findings, increments `loop_count`, and routes to `evaluate_step`.
- `evaluate_step` – Uses the LLM with structured output (`Evaluation`) to decide:
	- `status = "sufficient"` → stop,
	- `status = "insufficient"` and `loop_count < 3` → update `query` with `new_query` and loop back to `search_step`.

**Parent editor graph (`EditorState`)**
- `planner_node` – Uses an LLM with structured output (`Plan`) to propose 3 subtopics for the high-level `topic`.
- `research_orchestrator` – Iterates over subtopics, calling the child `research_graph` for each and aggregating the findings into `research_results`.
- `writer_node` – Feeds all aggregated findings into the LLM to produce a final narrative `final_report`.

### Running the example

From the repository root (or this folder), run:

```bash
cd 2_deep_research
python deep_research.py
```

You should see logs from the parent and child graphs, followed by a **FINAL DEEP RESEARCH REPORT** printed to the console.

### Required configuration

This example relies on configuration loaded via `core.load_vault_env()`:

- `OPENAI_API_KEY` – for `ChatOpenAI` (model `gpt-4.1-mini`).
- `TAVILY_API_KEY` – for `TavilyClient` web search.

Make sure these values are set in your vault/environment before running.

### How to reuse in your own projects

- Replace the `topic` in `if __name__ == "__main__":` with your own research question.
- Customize the `Plan`, `Evaluation`, or prompt in `writer_node` to change how the system plans, evaluates, or writes.
- Use the parent/child pattern as a template for other multi-step agent workflows (planner → worker loops → final synthesis).

This example is designed to be a clear, minimal reference for **deep research workflows with LangGraph** in this workshop.
