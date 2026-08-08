"""
backend/Services/components/import_component.py
ImportComponent：数据导入部件（无前置依赖）
"""

from __future__ import annotations

import sys
import logging
from pathlib import Path
from typing import Any, Dict, List

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.shared.types import ImportedArtifact, StepName, ImportError_  # noqa: E402
from backend.Infrastructures.importers import FileImporter, DbImporter  # noqa: E402
from backend.Services.components.base_component import BaseComponent  # noqa: E402

logger = logging.getLogger(__name__)


class ImportComponent(BaseComponent):
    """数据导入部件"""

    name = StepName.IMPORT
    required_inputs: List[StepName] = []

    def __init__(self):
        self._file_importer = FileImporter()
        self._db_importer = DbImporter()

    def execute(self, context, params: Dict[str, Any]) -> ImportedArtifact:
        resource_path = params.get("resource_path")
        resource_type = params.get("resource_type", "csv")
        is_database = params.get("is_database", False)
        db_connection_string = params.get("db_connection_string")
        query = params.get("query")
        chunksize = params.get("chunksize")

        if not resource_path:
            raise ImportError_("缺少 resource_path，无法导入数据")

        if is_database:
            df = self._db_importer.read(
                source=resource_path,
                db_type=resource_type,
                db_connection_string=db_connection_string,
                query=query,
            )
            source = f"db:{resource_path}"
        else:
            df = self._file_importer.read(
                source=resource_path,
                file_type=resource_type,
                chunksize=chunksize,
            )
            source = str(resource_path)

        # 落 temp_storage（stage=imported）
        storage = self._storage(context)
        storage_key = storage.save_dataframe(df, self._session(context), "imported")

        artifact = ImportedArtifact(
            step=StepName.IMPORT,
            storage_key=storage_key,
            shape=df.shape,
            columns=list(df.columns),
            dtypes={col: str(df[col].dtype) for col in df.columns},
            source=source,
        )
        logger.info("ImportComponent: 导入完成 shape=%s source=%s", df.shape, source)
        return artifact
