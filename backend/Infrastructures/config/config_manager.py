"""
backend/Infrastructures/config/config_manager.py
配置管理（转发 backend/Infrastructures/Configs/config_manager，接口不变）

说明：配置文件（model_config.json / model_mapping_config.json / database_config.json）
的唯一来源在 backend/Infrastructures/Configs，此处仅做转发，避免双份配置不一致。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保项目根目录在 sys.path 中
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.Infrastructures.Configs.config_manager import (  # noqa: E402
    MODEL_CONFIG,
    DATABASE_CONFIG,
    MODEL_MAPPING_CONFIG,
    load_model_config,
    load_database_config,
    load_model_mapping_config,
)

__all__ = [
    "MODEL_CONFIG", "DATABASE_CONFIG", "MODEL_MAPPING_CONFIG",
    "load_model_config", "load_database_config", "load_model_mapping_config",
]
