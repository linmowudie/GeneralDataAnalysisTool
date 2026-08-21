"""
临时存储模块单元测试（backend.Infrastructures.storage.temp_storage.TempStorage）
"""

import unittest
import sys
import os
import tempfile
import shutil
import uuid
import pandas as pd

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.Infrastructures.storage.temp_storage import TempStorage


class TestTempStorage(unittest.TestCase):
    """测试会话级 TempStorage"""

    def setUp(self):
        """测试前准备：使用独立的临时目录"""
        self.base_path = tempfile.mkdtemp(prefix="temp_storage_test_")
        self.storage = TempStorage(base_path=self.base_path)
        self.session_id = f"test_{uuid.uuid4().hex[:8]}"

    def tearDown(self):
        """测试后清理"""
        shutil.rmtree(self.base_path, ignore_errors=True)

    def test_save_and_load_dataframe(self):
        """测试 DataFrame 保存与读取"""
        df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        key = self.storage.save_dataframe(df, self.session_id, "imported")
        self.assertEqual(key, f"{self.session_id}/imported")

        loaded = self.storage.load_dataframe(self.session_id, "imported")
        self.assertIsNotNone(loaded)
        pd.testing.assert_frame_equal(df, loaded)

    def test_load_missing_dataframe(self):
        """测试读取不存在的阶段返回 None"""
        self.assertIsNone(self.storage.load_dataframe(self.session_id, "not_exist"))

    def test_save_and_load_artifact(self):
        """测试产物保存与读取"""
        from backend.shared.types import ImportedArtifact, StepName
        artifact = ImportedArtifact(step=StepName.IMPORT, shape=(3, 2),
                                    columns=['A', 'B'], source="test.csv")
        key = self.storage.save_artifact(self.session_id, artifact)
        self.assertIn("artifacts/import", key)

        loaded = self.storage.load_artifact(self.session_id, StepName.IMPORT)
        self.assertIsNotNone(loaded)
        self.assertEqual(loaded.shape, (3, 2))
        self.assertEqual(loaded.source, "test.csv")

    def test_clear_stage(self):
        """测试清理单阶段"""
        df = pd.DataFrame({'A': [1]})
        self.storage.save_dataframe(df, self.session_id, "imported")
        stats = self.storage.clear_stage(self.session_id, "imported")
        self.assertEqual(stats["files_removed"], 1)
        self.assertGreater(stats["space_freed"], 0)
        self.assertIsNone(self.storage.load_dataframe(self.session_id, "imported"))

    def test_clear_session(self):
        """测试清理会话全部数据"""
        df = pd.DataFrame({'A': [1]})
        self.storage.save_dataframe(df, self.session_id, "imported")
        self.storage.save_dataframe(df, self.session_id, "cleaned")
        stats = self.storage.clear_session(self.session_id)
        self.assertEqual(stats["files_removed"], 2)
        self.assertIsNone(self.storage.load_dataframe(self.session_id, "imported"))
        self.assertIsNone(self.storage.load_dataframe(self.session_id, "cleaned"))

    def test_clear_stage_globally(self):
        """测试跨会话清理指定阶段"""
        df = pd.DataFrame({'A': [1]})
        s1, s2 = f"{self.session_id}_1", f"{self.session_id}_2"
        self.storage.save_dataframe(df, s1, "imported")
        self.storage.save_dataframe(df, s2, "imported")
        self.storage.save_dataframe(df, s1, "cleaned")

        stats = self.storage.clear_stage_globally("imported")
        self.assertEqual(stats["files_removed"], 2)
        self.assertIsNone(self.storage.load_dataframe(s1, "imported"))
        self.assertIsNone(self.storage.load_dataframe(s2, "imported"))
        # cleaned 阶段不受影响
        self.assertIsNotNone(self.storage.load_dataframe(s1, "cleaned"))

    def test_clear_all(self):
        """测试全量清理"""
        df = pd.DataFrame({'A': [1]})
        self.storage.save_dataframe(df, self.session_id, "imported")
        stats = self.storage.clear_all()
        self.assertEqual(stats["files_removed"], 1)
        self.assertIsNone(self.storage.load_dataframe(self.session_id, "imported"))


if __name__ == '__main__':
    unittest.main()
