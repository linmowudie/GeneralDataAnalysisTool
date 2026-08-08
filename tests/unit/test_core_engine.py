"""
手动工作流单元测试（backend.Services.workflows.ManualWorkflow）

原 DataProcessingEngine 已删除，由 ManualWorkflow + 部件体系取代。
"""

import unittest
import sys
import os
import uuid
from unittest.mock import Mock

# 获取项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 将项目根目录添加到sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from backend.Services.workflows.manual_workflow import ManualWorkflow
from backend.Services.workflows.context import WorkflowContext
from backend.shared.types import (
    StepName, StepLocked, WorkflowOrderError, ImportedArtifact, CleanedArtifact,
)


class TestManualWorkflow(unittest.TestCase):
    """测试 ManualWorkflow 步骤调度"""

    def setUp(self):
        """测试前准备"""
        self.workflow = ManualWorkflow()
        self.session_id = f"unit_test_{uuid.uuid4().hex[:8]}"
        self.context = WorkflowContext(self.session_id)

    def tearDown(self):
        """测试后清理临时存储"""
        self.context.get_temp_storage().clear_session(self.session_id)

    def test_initialization(self):
        """测试工作流初始化：六个步骤部件齐全"""
        for step in StepName:
            self.assertIn(step, self.workflow._components)

    def test_order_enforcement_without_import(self):
        """测试未完成导入时执行清洗抛出顺序错误"""
        with self.assertRaises(WorkflowOrderError) as context:
            self.workflow.execute_step(self.context, StepName.CLEANING)
        self.assertIn("前置步骤未完成", str(context.exception))

    def test_import_success_and_lock(self):
        """测试导入步骤执行成功后自动锁定"""
        mock_component = Mock()
        mock_component.execute.return_value = ImportedArtifact(
            step=StepName.IMPORT, shape=(3, 2), columns=['A', 'B'], source="test.csv"
        )
        self.workflow._components[StepName.IMPORT] = mock_component

        artifact = self.workflow.execute_step(self.context, StepName.IMPORT,
                                              {"resource": "test.csv"})

        self.assertEqual(artifact.step, StepName.IMPORT)
        self.assertTrue(self.context.steps.is_completed(StepName.IMPORT))
        self.assertTrue(self.context.steps.is_locked(StepName.IMPORT))
        mock_component.execute.assert_called_once()

    def test_locked_step_rejects_reexecution(self):
        """测试锁定步骤不可重复执行"""
        mock_component = Mock()
        mock_component.execute.return_value = ImportedArtifact(step=StepName.IMPORT)
        self.workflow._components[StepName.IMPORT] = mock_component
        self.workflow.execute_step(self.context, StepName.IMPORT)

        with self.assertRaises(StepLocked) as context:
            self.workflow.execute_step(self.context, StepName.IMPORT)
        self.assertIn("已锁定", str(context.exception))

    def test_cleaning_after_import(self):
        """测试导入后可执行清洗"""
        import_component = Mock()
        import_component.execute.return_value = ImportedArtifact(step=StepName.IMPORT)
        clean_component = Mock()
        clean_component.execute.return_value = CleanedArtifact(step=StepName.CLEANING)
        self.workflow._components[StepName.IMPORT] = import_component
        self.workflow._components[StepName.CLEANING] = clean_component

        self.workflow.execute_step(self.context, StepName.IMPORT)
        artifact = self.workflow.execute_step(self.context, StepName.CLEANING)

        self.assertEqual(artifact.step, StepName.CLEANING)
        self.assertTrue(self.context.steps.is_completed(StepName.CLEANING))

    def test_reset_step_cascade(self):
        """测试级联重置：重置导入会清空后续状态与产物"""
        mock_component = Mock()
        mock_component.execute.return_value = ImportedArtifact(step=StepName.IMPORT)
        self.workflow._components[StepName.IMPORT] = mock_component
        self.workflow.execute_step(self.context, StepName.IMPORT)

        reset_steps = self.context.reset_step(StepName.IMPORT)

        self.assertIn(StepName.IMPORT, reset_steps)
        self.assertFalse(self.context.steps.is_completed(StepName.IMPORT))
        self.assertFalse(self.context.steps.is_locked(StepName.IMPORT))
        self.assertIsNone(self.context.get_artifact(StepName.IMPORT))


if __name__ == '__main__':
    unittest.main()
