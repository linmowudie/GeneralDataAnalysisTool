"""
backend/Infrastructures/llm_gateway/mock.py
MockLLM：返回规则化兜底 JSON，保证无 LLM 环境可运行
"""

from __future__ import annotations

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


class MockLLM:
    """无 LLM 环境下的兜底实现，按 schema_hint 返回规则化默认值"""

    def chat_json(self, prompt: str, schema_hint: Dict[str, Any]) -> Dict[str, Any]:
        logger.debug("MockLLM 收到 prompt=%s... schema=%s", (prompt or "")[:80], schema_hint)
        return self._fill_defaults(schema_hint)

    def _fill_defaults(self, schema_hint: Dict[str, Any]) -> Dict[str, Any]:
        """根据 schema 提示生成默认结构"""
        result: Dict[str, Any] = {}
        if not isinstance(schema_hint, dict):
            return result

        for key, spec in schema_hint.items():
            if isinstance(spec, dict) and "default" in spec:
                result[key] = spec["default"]
            elif isinstance(spec, dict) and spec.get("type") == "list":
                result[key] = spec.get("items_default", [])
            elif isinstance(spec, dict) and spec.get("type") == "number":
                result[key] = 0.0
            elif isinstance(spec, dict) and spec.get("type") == "string":
                result[key] = ""
            else:
                result[key] = spec
        return result
