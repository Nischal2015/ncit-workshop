import sys
from pathlib import Path

import os
import operator
from typing import Annotated, TypedDict, Literal

from pydantic import BaseModel, Field
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

from langgraph.graph import StateGraph, START
from langgraph.types import Command

sys.path.append(str(Path().resolve().parent))
from core import load_vault_env

load_vault_env()


llm = ChatOpenAI(model="gpt-4.1-mini", temperature=0)
tavily = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])


# Child State
class ResearchState(TypedDict):
    query: str
    findings: Annotated[list, operator.add]
    loop_count: int


# Structured Output
class Evaluation(BaseModel):
    status: Literal["sufficient", "insufficient"] = Field(
        description="Is the info good enough?"
    )
    new_query: str = Field("Refined query if insufficient")


def search_step(state: ResearchState) -> Command[Literal["evaluate_step"]]:
    print(f"  [Child] Searching: {state['query']} (Iter: {state['loop_count']})")
    try:
        result = tavily.search(state["query"], max_results=2, search_depth="basic")
        content = "\n".join([r["content"] for r in result.get("results", [])])
        finding = f"--- Search Iteration {state['loop_count']} ---\n{content}\n"
    except Exception as e:
        finding = f"Error: {e}"

    # Return update and move to evaluation
    return Command(
        update={"findings": [finding], "loop_count": state["loop_count"] + 1},
        goto="evaluate_step",
    )


def evaluate_step(state: ResearchState) -> Command[Literal["search_step", "__end__"]]:
    print("  [Child] Evaluating findings...")

    context = "\n".join(state["findings"])
    evaluator = llm.with_structured_output(Evaluation)

    res = evaluator.invoke(f"Query: {state['query']}\n\nFindings:\n{context}")

    if res.status == "sufficient" or state["loop_count"] >= 3:
        return Command(goto="__end__")
    else:
        return Command(update={"query": res.new_query}, goto="search_step")


# --- BUILD CHILD GRAPH ---
research_builder = StateGraph(ResearchState)
research_builder.add_node("search_step", search_step)
research_builder.add_node("evaluate_step", evaluate_step)
research_builder.add_edge(START, "search_step")

research_graph = research_builder.compile()


# --- PARENT STATE ---
class EditorState(TypedDict):
    topic: str
    subtopics: list[str]
    final_report: str
    research_results: Annotated[dict, lambda a, b: {**a, **b}]


class Plan(BaseModel):
    subtopics: list[str] = Field(
        description="List of 3 distinct sub-questions to research."
    )


def planner_node(state: EditorState) -> Command[Literal["research_orchestrator"]]:
    print(f"\n[Parent] Planning research for: {state['topic']}")

    planner = llm.with_structured_output(Plan)
    res = planner.invoke(f"Topic: {state['topic']}")

    return Command(update={"subtopics": res.subtopics}, goto="research_orchestrator")


def research_orchestrator(state: EditorState) -> Command[Literal["writer_node"]]:
    print("[Parent] Delegating to Researcher Agent...")

    results = {}

    for topic in state["subtopics"]:
        print(f"\n--- Spawning Child Agent for: {topic} ---")

        # Invoke child research graph
        child_result = research_graph.invoke(
            {"query": topic, "findings": [], "loop_count": 0}
        )

        full_text = "\n".join(child_result["findings"])
        results[topic] = full_text

    return Command(update={"research_results": results}, goto="writer_node")


def writer_node(state: EditorState) -> Command[Literal["__end__"]]:
    print("\n[Parent] Synthesizing Final Report...")

    context = ""
    for topic, data in state["research_results"].items():
        context += f"## {topic}\n{data}\n\n"

    prompt = f"Write a comprehensive report on '{state['topic']}' using the following data:\n\n{context}"
    response = llm.invoke(prompt)

    return Command(update={"final_report": response.content}, goto="__end__")


# --- BUILD PARENT GRAPH ---
parent_builder = StateGraph(EditorState)
parent_builder.add_node("planner_node", planner_node)
parent_builder.add_node("research_orchestrator", research_orchestrator)
parent_builder.add_node("writer_node", writer_node)

parent_builder.add_edge(START, "planner_node")

# Compile with Checkpointer (Memory)
# checkpointer = InMemorySaver()
app = parent_builder.compile()


if __name__ == "__main__":
    thread_config = {"configurable": {"thread_id": "workshop_v3_latest"}}

    topic = "Comparison of M4 Apple Silicon vs NVIDIA Blackwell for AI Inference"

    print(f"Starting Multi-Agent Deep Research on: {topic}")

    # Run
    final_state = app.invoke({"topic": topic}, config=thread_config)

    print("\n\n" + "=" * 50)
    print("FINAL DEEP RESEARCH REPORT")
    print("=" * 50)
    print(final_state["final_report"])
