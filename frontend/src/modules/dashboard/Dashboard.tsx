import React, { useEffect, useState } from 'react';
import { Button } from 'antd';
import {
  ImportOutlined,
  TableOutlined,
  FilterOutlined,
  ExperimentOutlined,
  BarChartOutlined,
  FileTextOutlined,
  RobotOutlined,
  ArrowRightOutlined,
  LockFilled,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { PageHeader, StatCard, StepStatusPill, LimeSquiggle } from '../../components/common/Common';
import { useSession, STEP_ORDER, STEP_LABELS } from '../../context/SessionContext';
import type { StepKey } from '../../context/SessionContext';
import { dataPreviewService } from '../../services/dataPreviewService';
import './Dashboard.css';

const STEP_META: Record<StepKey, { icon: React.ReactNode; route: string; desc: string }> = {
  import: { icon: <ImportOutlined />, route: '/import', desc: '上传文件或从数据库导入' },
  preview: { icon: <TableOutlined />, route: '/preview', desc: '查看数据概览与字段信息' },
  cleaning: { icon: <FilterOutlined />, route: '/cleaning', desc: '处理缺失值、异常值与重复行' },
  analysis: { icon: <ExperimentOutlined />, route: '/analysis', desc: '选择模型执行训练与评估' },
  visualization: { icon: <BarChartOutlined />, route: '/visualization', desc: '生成统计图表与分析图' },
  report: { icon: <FileTextOutlined />, route: '/report', desc: '汇总结果并导出分析报告' },
};

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const { sessionId, ready, stepStatus, isLocked, refreshStatus } = useSession();
  const [dataset, setDataset] = useState<{ rows?: number; cols?: number } | null>(null);

  useEffect(() => {
    if (!ready) return;
    refreshStatus();
    (async () => {
      try {
        const res: any = await dataPreviewService.getDatasetInfo();
        const info = res?.data || res?.info || res || {};
        setDataset({
          rows: info.total_records ?? info.total_rows ?? info.n_rows,
          cols: info.features_count != null ? info.features_count + 1 : info.total_columns,
        });
      } catch {
        setDataset(null);
      }
    })();
  }, [refreshStatus, ready]);

  const completedCount = STEP_ORDER.filter((s) => stepStatus.completed_steps.includes(s)).length;

  return (
    <div className="df-page">
      <PageHeader
        eyebrow="DATAFORGE WORKSPACE"
        title={
          <>
            数据分析<span className="df-lime-chip">流水线</span>工作台
          </>
        }
        description="从数据导入到报表导出的完整闭环。按步骤推进，或直接交给 Agent 自动完成。"
        extra={
          <Button type="primary" icon={<RobotOutlined />} onClick={() => navigate('/agent')}>
            Agent 自动分析
          </Button>
        }
      />

      <div className="df-grid-4">
        <StatCard label="会话 ID" value={ready && sessionId ? sessionId.slice(0, 8) : '····'} accent="violet" hint="本地持久化会话" />
        <StatCard label="已完成步骤" value={`${completedCount}/${STEP_ORDER.length}`} accent="lime" hint="流水线进度" />
        <StatCard label="数据规模" value={dataset?.rows != null ? `${dataset.rows} × ${dataset.cols ?? '?'}` : '未导入'} accent="pink" hint="行 × 列" />
        <StatCard label="分析引擎" value="5 层后端" accent="violet" hint="Interfaces → Cores" />
      </div>

      <div className="df-section-head">
        <div>
          <div className="df-eyebrow">PIPELINE</div>
          <h2 className="df-card-title" style={{ margin: 0 }}>流程步骤</h2>
        </div>
        <LimeSquiggle />
      </div>

      <div className="df-grid-3">
        {STEP_ORDER.map((step, idx) => {
          const meta = STEP_META[step];
          const locked = isLocked(step);
          return (
            <div
              key={step}
              className={`df-card df-step-card ${locked ? 'df-step-locked' : ''}`}
              onClick={() => !locked && navigate(meta.route)}
            >
              <div className="df-step-top">
                <span className="df-step-index df-display">{String(idx + 1).padStart(2, '0')}</span>
                <span className="df-step-icon">{locked ? <LockFilled /> : meta.icon}</span>
                <StepStatusPill step={step} />
              </div>
              <div className="df-step-name">{STEP_LABELS[step]}</div>
              <div className="df-caption">{meta.desc}</div>
              <div className="df-step-go df-micro">
                {locked ? '完成前置步骤后解锁' : '进入'} <ArrowRightOutlined />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default Dashboard;
