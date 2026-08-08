"""backend.Infrastructures.llm_gateway：LLM 网关（首版 mock 兜底）"""
from .base import LLMGateway, get_llm_gateway
from .mock import MockLLM

__all__ = ["LLMGateway", "MockLLM", "get_llm_gateway"]
