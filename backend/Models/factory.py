"""
backend/Models/factory.py
ModelFactory：模型工厂

参数治理（简化落地版，对齐设计文档四层机制）：
1. 注册表白名单收敛暴露面（init_params）
2. 默认值全覆盖 + 局部覆盖合并（defaults | user_params）
3. 白名单校验拦截非法参数（validate_params）
4. Agent 自动调参预留（PlanCandidate.suggested_params 传入 create）

create() 合并顺序：注册表默认参数 -> Planner 推荐值 -> 用户覆盖值，后者覆盖前者。
"""

from __future__ import annotations

import sys
import importlib
import logging
from pathlib import Path
from typing import Any, Dict, Optional

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import InvalidModelParams  # noqa: E402
from .registry import model_registry  # noqa: E402

logger = logging.getLogger(__name__)


class ModelFactory:
    """模型工厂：按注册表合并参数并实例化 sklearn 模型"""

    def __init__(self, registry=None):
        self._registry = registry or model_registry

    # ---------------------------------------------------------------- 校验
    def validate_params(self, model_type: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        白名单校验：不在 init_params 白名单的参数丢弃并告警。
        返回过滤后的合法参数字典；模型不存在抛 InvalidModelParams。
        """
        meta = self._registry.get_meta(model_type)
        whitelist = set(meta.init_params)
        valid: Dict[str, Any] = {}
        for key, value in (params or {}).items():
            if key in whitelist:
                valid[key] = value
            else:
                logger.warning("参数 %s 不在模型 %s 白名单中，已丢弃", key, model_type)
        return valid

    # ---------------------------------------------------------------- 创建
    def create(self, model_type: str, params: Optional[Dict[str, Any]] = None):
        """
        合并默认参数后实例化 sklearn 模型。

        :param model_type: 注册表模型 key
        :param params: 用户/Planner 覆盖参数（仅覆盖想改的参数）
        :return: sklearn 估计器实例
        :raises InvalidModelParams: 模型不存在或无法实例化
        """
        meta = self._registry.get_meta(model_type)

        # 合并顺序：注册表默认 -> 用户覆盖（后者覆盖前者）
        merged: Dict[str, Any] = dict(meta.default_params)
        if params:
            valid_user = self.validate_params(model_type, params)
            merged.update(valid_user)

        class_path = self._registry.get_class_path(meta.class_name)
        if not class_path:
            raise InvalidModelParams(
                f"模型 {model_type}({meta.class_name}) 未在 model_mapping_config 中登记 sklearn 类路径"
            )

        try:
            module_path, class_name = class_path.rsplit(".", 1)
            module = importlib.import_module(module_path)
            estimator_cls = getattr(module, class_name)
            return estimator_cls(**merged)
        except InvalidModelParams:
            raise
        except Exception as e:
            logger.error("模型实例化失败 %s: %s", model_type, e, exc_info=True)
            raise InvalidModelParams(f"模型实例化失败 {model_type}: {str(e)}") from e


# 全局单例
model_factory = ModelFactory()
