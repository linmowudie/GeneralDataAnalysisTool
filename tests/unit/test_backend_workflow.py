"""
backend 工作流冒烟测试：
1. ManualWorkflow：import -> preview -> cleaning -> analysis（iris 分类）
2. AgentWorkflow：画像 -> 推荐 -> 执行 -> 评估 -> 择优闭环
"""

import sys
import uuid
from pathlib import Path

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from backend.Services import WorkflowContext, ManualWorkflow, AgentWorkflow  # noqa: E402
from backend.shared.types import StepName, TaskType  # noqa: E402

IRIS_CSV = str(_PROJECT_ROOT / "Data" / "iris.csv")


def _new_context() -> WorkflowContext:
    return WorkflowContext(f"smoke_{uuid.uuid4().hex[:8]}")


def test_manual_workflow():
    ctx = _new_context()
    wf = ManualWorkflow()

    # import
    artifact = wf.execute_step(ctx, StepName.IMPORT, {
        "resource_path": IRIS_CSV,
        "resource_type": "csv",
    })
    assert artifact.shape[0] > 0, "导入数据为空"
    print("[import]", artifact.shape, artifact.columns[:3], "...")

    # preview
    preview = wf.execute_step(ctx, StepName.PREVIEW, {"head_n": 5})
    assert len(preview.head_records) > 0
    print("[preview] rows=", preview.dataset_info["total_rows"])

    # cleaning
    cleaned = wf.execute_step(ctx, StepName.CLEANING, {
        "select_mode": "standard",
        "target_col": "target",
    })
    print("[cleaning]", cleaned.shape)

    # analysis（分类）
    analysis = wf.execute_step(ctx, StepName.ANALYSIS, {
        "model_type": "logisticregression",
        "target_col": "target",
    })
    assert analysis.task_type == TaskType.CLASSIFICATION
    assert analysis.metrics, "分类应产生指标"
    print("[analysis] metrics=", analysis.metrics)

    # 状态机：import/cleaning/analysis 自动锁定
    status = ctx.steps.status()
    assert "import" in status["locked_steps"]
    assert "cleaning" in status["locked_steps"]
    assert "analysis" in status["locked_steps"]
    print("[status]", status)

    ctx.reset_all()
    print("ManualWorkflow OK\n")


def test_agent_workflow():
    ctx = _new_context()
    wf_manual = ManualWorkflow()
    wf_manual.execute_step(ctx, StepName.IMPORT, {
        "resource_path": IRIS_CSV,
        "resource_type": "csv",
    })
    wf_manual.execute_step(ctx, StepName.CLEANING, {
        "select_mode": "standard",
        "target_col": "target",
    })

    agent = AgentWorkflow(max_candidates=3, timeout_sec=120)
    decision = agent.run(ctx, target_col="target")

    assert decision.profile is not None
    assert decision.attempts, "至少有一次尝试"
    assert decision.best is not None, "应选出最优候选"
    print("[agent] task=", decision.profile.inferred_task_type.value)
    for a in decision.attempts:
        print("  attempt:", a.model_type,
              "status=", a.evaluation.status.value if a.evaluation else None,
              "error=", a.error)
    print("[agent] best=", decision.best.model_type, decision.best.metrics)

    # 最优产物应写入上下文
    assert ctx.get_artifact(StepName.ANALYSIS) is not None
    ctx.reset_all()
    print("AgentWorkflow OK\n")


if __name__ == "__main__":
    test_manual_workflow()
    test_agent_workflow()
    print("ALL WORKFLOW SMOKE TESTS PASSED")
