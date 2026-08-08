"""
backend/Models/registry.py
ModelRegistry：模型注册表

数据源：model_config.json（嵌套，按任务类型分组） + model_mapping_config.json。
提供任务类型 / 模型列表 / 元信息 / 全量配置查询，供前端动态表单与 Agent 候选集使用。
"""

from __future__ import annotations

import json
import sys
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import InvalidModelParams  # noqa: E402

logger = logging.getLogger(__name__)

# 原始嵌套配置目录（唯一来源在 backend/Infrastructures/Configs）
_CONFIG_DIR = _PROJECT_ROOT / "backend" / "Infrastructures" / "Configs"


@dataclass
class ModelMeta:
    """单个模型的元信息"""
    key: str
    class_name: str
    task_type: str
    init_params: List[str] = field(default_factory=list)
    default_params: Dict[str, Any] = field(default_factory=dict)


class ModelRegistry:
    """模型注册表"""

    def __init__(self, config_dir: Optional[Path] = None):
        self._config_dir = config_dir or _CONFIG_DIR
        # 嵌套结构：{task_type: {model_key: {class, type, init_params, default_params}}}
        self._nested: Dict[str, Dict[str, Any]] = self._load_nested_config()
        self._mapping: Dict[str, Any] = self._load_mapping_config()
        logger.info("ModelRegistry 初始化完成，任务类型: %s", list(self._nested.keys()))

    # ---------------------------------------------------------------- 加载
    def _load_nested_config(self) -> Dict[str, Dict[str, Any]]:
        path = self._config_dir / "model_config.json"
        if not path.exists():
            raise FileNotFoundError(f"模型配置文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _load_mapping_config(self) -> Dict[str, Any]:
        path = self._config_dir / "model_mapping_config.json"
        if not path.exists():
            raise FileNotFoundError(f"模型映射配置文件不存在: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    # ---------------------------------------------------------------- 查询
    def list_task_types(self) -> List[str]:
        """回归/分类/聚类/降维/关联"""
        return list(self._nested.keys())

    def list_models(self, task_type: Optional[str] = None) -> List[str]:
        """模型 key 列表（对应前端 available-models 端点）"""
        if task_type is None:
            keys: List[str] = []
            for models in self._nested.values():
                keys.extend(models.keys())
            return keys
        models = self._nested.get(task_type, {})
        return list(models.keys())

    def get_meta(self, model_type: str) -> ModelMeta:
        """按模型 key 获取元信息（class / type / init_params / default_params）"""
        model_key = model_type.lower()
        for task_type, models in self._nested.items():
            if model_key in models:
                info = models[model_key]
                return ModelMeta(
                    key=model_key,
                    class_name=info.get("class", ""),
                    task_type=info.get("type", task_type),
                    init_params=list(info.get("init_params", [])),
                    default_params=dict(info.get("default_params", {})),
                )
        raise InvalidModelParams(f"注册表中不存在模型: {model_type}")

    def get_class_path(self, class_name: str) -> Optional[str]:
        """sklearn 类全路径（来自 model_mapping_config）"""
        return self._mapping.get("model_mapping", {}).get(class_name)

    def get_metrics(self, task_type: str) -> List[str]:
        """任务类型对应的默认指标列表"""
        return list(self._mapping.get("metrics_mapping", {}).get(task_type, []))

    def get_full_config(self) -> Dict[str, Any]:
        """对应前端 model-config 端点：扁平化 {model_key: info}"""
        flat: Dict[str, Any] = {}
        for models in self._nested.values():
            for model_name, model_info in models.items():
                flat[model_name] = model_info
        return flat


# 全局单例
model_registry = ModelRegistry()
