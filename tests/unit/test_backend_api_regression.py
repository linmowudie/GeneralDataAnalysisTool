"""
tests/unit/test_backend_api_regression.py
backend 五层架构 API 回归测试（需先启动服务：uvicorn backend.Interfaces.web.app:app）

覆盖：会话/导入/预览/清洗/分析/可视化/报表/Agent闭环/步骤锁/清理/模型/健康检查
"""

import json
import sys
from pathlib import Path

import requests

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
BASE = "http://127.0.0.1:8000"
PASS = 0
FAIL = 0


def check(name, ok, detail=""):
    global PASS, FAIL
    if ok:
        PASS += 1
        print(f"[PASS] {name}")
    else:
        FAIL += 1
        print(f"[FAIL] {name} {detail}")


def main():
    # 健康检查
    r = requests.get(f"{BASE}/api/health")
    check("健康检查", r.status_code == 200 and r.json().get("status") == "healthy", r.text)

    # 创建会话
    r = requests.post(f"{BASE}/api/session/create")
    sid = r.json().get("session_id")
    check("创建会话", r.status_code == 200 and bool(sid), r.text)

    # 文件导入
    csv_path = PROJECT_ROOT / "Data" / "iris.csv"
    with open(csv_path, "rb") as f:
        r = requests.post(f"{BASE}/api/import/upload-file",
                          data={"session_id": sid}, files={"file": ("iris.csv", f, "text/csv")})
    check("文件导入", r.status_code == 200 and "成功" in r.json().get("message", ""), r.text)

    # 数据预览
    r = requests.get(f"{BASE}/api/preview/data-preview", params={"session_id": sid})
    check("数据预览", r.status_code == 200 and r.json().get("total_rows", 0) > 0, r.text)

    # 数据集信息
    r = requests.get(f"{BASE}/api/preview/dataset-info", params={"session_id": sid})
    check("数据集信息", r.status_code == 200 and r.json().get("total_records", 0) > 0, r.text)

    # 数据列
    r = requests.get(f"{BASE}/api/analysis/data-columns/{sid}")
    check("数据列", r.status_code == 200 and "target" in r.json().get("columns", []), r.text)

    # 数据清洗
    r = requests.post(f"{BASE}/api/cleaning/clean-data", data={
        "session_id": sid, "mode": "standard", "is_custom": "false",
        "parameters": "{}", "target_col": "target",
    })
    check("数据清洗", r.status_code == 200, r.text)

    # 清洗模式
    r = requests.get(f"{BASE}/api/cleaning/cleaning-modes")
    check("清洗模式", r.status_code == 200 and len(r.json().get("modes", [])) == 4, r.text)

    # 可用模型
    r = requests.get(f"{BASE}/api/analysis/available-models")
    check("可用模型", r.status_code == 200 and len(r.json().get("models", [])) > 0, r.text)

    # 模型配置
    r = requests.get(f"{BASE}/api/analysis/model-config")
    check("模型配置", r.status_code == 200 and isinstance(r.json().get("config"), dict), r.text)

    # 数据分析
    r = requests.post(f"{BASE}/api/analysis/run-analysis", data={
        "session_id": sid, "model_type": "logisticregression",
        "parameters": json.dumps({"target_col": "target"}),
    })
    check("数据分析", r.status_code == 200 and "result" in r.json(), r.text[:200])

    # 步骤状态（analysis 应已完成并锁定）
    r = requests.get(f"{BASE}/api/session/step-status", params={"session_id": sid})
    status = r.json().get("status", {})
    check("步骤状态", "analysis" in status.get("completed_steps", [])
          and "analysis" in status.get("locked_steps", []), r.text)

    # 步骤锁解锁/锁定
    r = requests.post(f"{BASE}/api/step/unlock", params={"session_id": sid, "step": "analysis"})
    check("步骤解锁", r.status_code == 200, r.text)
    r = requests.post(f"{BASE}/api/step/lock", params={"session_id": sid, "step": "analysis"})
    check("步骤锁定", r.status_code == 200, r.text)
    r = requests.get(f"{BASE}/api/step/status", params={"session_id": sid})
    check("步骤锁状态", r.status_code == 200 and r.json().get("status") == "success", r.text)

    # 可视化
    r = requests.post(f"{BASE}/api/visualization/generate-chart", data={
        "session_id": sid, "chart_type": "scatter", "parameters": "{}",
    })
    check("生成图表", r.status_code == 200 and r.json().get("status") == "success", r.text[:200])

    r = requests.get(f"{BASE}/api/visualization/available-charts")
    check("可用图表", r.status_code == 200 and r.json().get("count", 0) == 6, r.text)

    # 报表四端点
    r = requests.post(f"{BASE}/api/reporting/generate",
                      params={"session_id": sid, "report_type": "full"})
    report_id = r.json().get("report_id") if r.status_code == 200 else None
    check("报表生成", r.status_code == 200 and bool(report_id), r.text)

    if report_id:
        r = requests.get(f"{BASE}/api/reporting/export/{report_id}", params={"format": "html"})
        check("报表导出", r.status_code == 200 and b"<html" in r.content.lower(), r.text[:200])

    r = requests.get(f"{BASE}/api/reporting/templates")
    check("报表模板", r.status_code == 200 and len(r.json().get("templates", [])) == 4, r.text)

    r = requests.post(f"{BASE}/api/reporting/save-config",
                      json={"report_type": "full", "title": "测试报告"})
    check("报表配置", r.status_code == 200 and r.json().get("status") == "success", r.text)

    # Agent 五端点
    r = requests.get(f"{BASE}/api/agent/data-profile", params={"session_id": sid, "target_col": "target"})
    check("Agent画像", r.status_code == 200 and "profile" in r.json(), r.text[:200])

    r = requests.post(f"{BASE}/api/agent/recommend-methods", params={"session_id": sid, "target_col": "target"})
    check("Agent推荐", r.status_code == 200 and r.json().get("count", 0) > 0, r.text[:200])

    r = requests.post(f"{BASE}/api/agent/auto-analyze",
                      params={"session_id": sid, "max_candidates": 2, "target_col": "target"})
    decision = r.json().get("decision") if r.status_code == 200 else None
    check("Agent自动分析", r.status_code == 200 and decision and decision.get("best"),
          r.text[:200])

    r = requests.post(f"{BASE}/api/agent/evaluate", params={"session_id": sid})
    check("Agent评估", r.status_code == 200 and "evaluation" in r.json(), r.text[:200])

    r = requests.get(f"{BASE}/api/agent/decision", params={"session_id": sid})
    check("Agent决策查询", r.status_code == 200 and r.json().get("decision") is not None, r.text[:200])

    # 模型端点（修复双 prefix 后应可达）
    r = requests.get(f"{BASE}/api/model/list")
    check("模型列表", r.status_code == 200 and r.json().get("success") is True, r.text)
    r = requests.post(f"{BASE}/api/model/manage", params={"max_models": 5})
    check("模型管理", r.status_code == 200 and r.json().get("success") is True, r.text)

    # 清理任务
    r = requests.get(f"{BASE}/api/cleanup/status")
    check("清理状态", r.status_code == 200 and r.json().get("status") == "available", r.text)
    r = requests.post(f"{BASE}/api/cleanup/run-step", params={"step": "visualized"})
    check("按步骤清理", r.status_code == 200 and "stats" in r.json(), r.text)

    # 步骤重置
    r = requests.post(f"{BASE}/api/session/reset-step",
                      data={"session_id": sid, "step": "cleaning"})
    check("步骤重置", r.status_code == 200, r.text)

    # 结束会话
    r = requests.post(f"{BASE}/api/session/end", data={"session_id": sid})
    check("结束会话", r.status_code == 200, r.text)

    # 会话不存在应 404/410
    r = requests.get(f"{BASE}/api/preview/data-preview", params={"session_id": sid})
    check("已删除会话返回4xx", 400 <= r.status_code < 500, f"status={r.status_code}")

    print(f"\n回归结果: {PASS} 通过 / {FAIL} 失败")
    return 1 if FAIL else 0


if __name__ == "__main__":
    sys.exit(main())
