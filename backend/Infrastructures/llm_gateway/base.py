"""
backend/Infrastructures/llm_gateway/base.py
LLMGateway 协议与网关工厂

配置项 config/llm_config.json：provider / api_key / model / timeout / enabled。
enabled=false 时 Agents 层强制使用规则实现（返回 MockLLM）。
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Protocol

logger = logging.getLogger(__name__)

_CONFIG_PATH = Path(__file__).resolve().parent.parent / "config" / "llm_config.json"


class LLMGateway(Protocol):
    """LLM 网关协议：输入 prompt + schema 提示，返回结构化 JSON"""

    def chat_json(self, prompt: str, schema_hint: Dict[str, Any]) -> Dict[str, Any]:
        ...


def load_llm_config() -> Dict[str, Any]:
    """加载 LLM 配置，缺失时给出安全默认值"""
    defaults = {
        "provider": "mock",
        "api_key": "",
        "model": "",
        "timeout": 30,
        "enabled": False,
    }
    try:
        if _CONFIG_PATH.exists():
            with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
                loaded = json.load(f)
            defaults.update(loaded)
    except Exception as e:
        logger.warning("加载 llm_config.json 失败，使用默认配置: %s", e)
    return defaults


def get_llm_gateway(config: Optional[Dict[str, Any]] = None) -> LLMGateway:
    """
    网关工厂：enabled=false 或无可用 provider 时返回 MockLLM 兜底
    """
    from .mock import MockLLM

    cfg = config or load_llm_config()
    if not cfg.get("enabled", False):
        logger.info("LLM 未启用，使用 MockLLM 兜底")
        return MockLLM()

    provider = cfg.get("provider", "mock")
    # 首版仅实现 mock；其余 provider 预留，回落 mock
    if provider != "mock":
        logger.warning("provider=%s 暂未实现，回落 MockLLM", provider)
    return MockLLM()
