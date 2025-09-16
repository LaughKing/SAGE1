from __future__ import annotations

import importlib
import json
import os
import sys
from typing import Any, Dict, Iterable

from sage.common.utils.config.loader import load_config
from sage.libs.agents.action.mcp_registry import MCPRegistry
from sage.libs.agents.planning.llm_planner import LLMPlanner
from sage.libs.agents.profile.profile import BaseProfile
from sage.libs.agents.runtime.agent import AgentRuntime
from sage.libs.rag.generator import OpenAIGenerator


# ====== 读取 source ======
def iter_queries(source_cfg: Dict[str, Any]) -> Iterable[str]:
    stype = source_cfg.get("type", "local")
    if stype == "local":
        path = source_cfg["data_path"]
        field = source_cfg.get("field_query", "query")
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                obj = json.loads(line)
                q = obj.get(field, "")
                if isinstance(q, str) and q.strip():
                    yield q
    elif stype == "hf":
        from datasets import load_dataset

        name = source_cfg["hf_dataset_name"]
        config = source_cfg.get("hf_dataset_config")
        split = source_cfg.get("hf_split", "dev")
        field = source_cfg.get("field_query", "query")
        ds = load_dataset(name, config, split=split)
        for row in ds:
            q = row.get(field, "")
            if isinstance(q, str) and q.strip():
                yield q
    else:
        raise ValueError(f"Unsupported source.type: {stype}")


def main():
    # ====== 读取配置 ======
    cfg_path = os.path.join(
        os.path.dirname(__file__), "..", "config", "config_agent_min.yaml"
    )
    if not os.path.exists(cfg_path):
        print(f"❌ Configuration file not found: {cfg_path}")
        sys.exit(1)
    config: Dict[str, Any] = load_config(cfg_path)

    # ====== Profile ======
    profile = BaseProfile.from_dict(config["profile"])

    # ====== Generator======
    gen_cfg = config["generator"]["remote"]  # 可改为 "local"/"remote"
    generator = OpenAIGenerator(gen_cfg)

    # ====== Planner ======
    planner_cfg = config["planner"]
    planner = LLMPlanner(
        generator=generator,
        max_steps=planner_cfg.get("max_steps", 6),
        enable_repair=planner_cfg.get("enable_repair", True),
        topk_tools=planner_cfg.get("topk_tools", 6),
    )

    # ====== MCP 工具注册：按配置动态 import 并注册 ======
    registry = MCPRegistry()
    for item in config.get("tools", []):
        mod = importlib.import_module(item["module"])
        cls = getattr(mod, item["class"])
        kwargs = item.get("init_kwargs", {})
        registry.register(cls(**kwargs) if kwargs else cls())

    # ====== Runtime ======
    runtime_cfg = config["runtime"]
    agent = AgentRuntime(
        profile=profile,
        planner=planner,
        tools=registry,
        summarizer=(
            generator if runtime_cfg.get("summarizer") == "reuse_generator" else None
        ),
        # memory=None,  # 如需接入 MemoryServiceAdapter，再按配置打开
        max_steps=runtime_cfg.get("max_steps", 6),
    )

    # ====== 跑一遍 queries======
    for q in iter_queries(config["source"]):
        print("\n==========================")
        print(f"🧑‍💻 User: {q}")
        ans = agent.execute({"query": q})
        print(f"🤖 Agent:\n{ans}")


if __name__ == "__main__":
    # 和 RAG 示例一致的“测试模式”友好输出
    if (
        os.getenv("SAGE_EXAMPLES_MODE") == "test"
        or os.getenv("SAGE_TEST_MODE") == "true"
    ):
        try:
            main()
            print("\n✅ Test passed: Agent pipeline structure validated")
        except Exception as e:
            print(f"❌ Test failed: {e}")
            sys.exit(1)
    else:
        main()
