import React, { useEffect, useState } from 'react';
import { Button, InputNumber, Table, Spin, message } from 'antd';
import {
  RobotOutlined,
  RadarChartOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  AuditOutlined,
} from '@ant-design/icons';
import { PageHeader, StatCard } from '../../components/common/Common';
import { useSession } from '../../context/SessionContext';
import { agentService } from '../../services/agentService';
import type { AgentProfile, PlanCandidate, EvaluationReport, AgentDecision } from '../../services/agentService';
import './AgentPage.css';

const AgentPage: React.FC = () => {
  const { refreshStatus } = useSession();
  const [loading, setLoading] = useState<string | null>(null);
  const [profile, setProfile] = useState<AgentProfile | null>(null);
  const [candidates, setCandidates] = useState<PlanCandidate[]>([]);
  const [evaluation, setEvaluation] = useState<EvaluationReport | null>(null);
  const [decision, setDecision] = useState<AgentDecision | null>(null);
  const [maxCandidates, setMaxCandidates] = useState(3);

  useEffect(() => {
    agentService.getDecision().then(setDecision).catch(() => undefined);
  }, []);

  const run = async (key: string, fn: () => Promise<void>) => {
    setLoading(key);
    try {
      await fn();
    } catch (e: any) {
      message.error(`${e?.message || e}`);
    } finally {
      setLoading(null);
    }
  };

  const handleProfile = () => run('profile', async () => {
    const p = await agentService.dataProfile();
    setProfile(p);
    message.success('数据画像完成');
  });

  const handleRecommend = () => run('recommend', async () => {
    const c = await agentService.recommendMethods();
    setCandidates(c);
    message.success(`推荐了 ${c.length} 个候选方法`);
  });

  const handleEvaluate = () => run('evaluate', async () => {
    const ev = await agentService.evaluate();
    setEvaluation(ev);
    message.success('评估完成');
  });

  const handleAuto = () => run('auto', async () => {
    const d = await agentService.autoAnalyze(undefined, { maxCandidates });
    setDecision(d);
    message.success('自动分析完成');
    await refreshStatus();
  });

  const attemptColumns = [
    { title: '模型', dataIndex: 'model_type', key: 'model_type', render: (v: string) => <span className="df-code">{v}</span> },
    { title: '任务类型', dataIndex: 'task_type', key: 'task_type' },
    {
      title: '指标', dataIndex: 'metrics', key: 'metrics',
      render: (m: Record<string, number>) =>
        m && Object.keys(m).length
          ? Object.entries(m).map(([k, v]) => `${k}: ${typeof v === 'number' ? v.toFixed(4) : v}`).join(' · ')
          : '—',
    },
    {
      title: '状态', key: 'state',
      render: (_: any, r: any) =>
        r.error ? <span className="df-pill df-pill-locked">失败</span> : <span className="df-pill df-pill-done">成功</span>,
    },
  ];

  return (
    <div className="df-page">
      <PageHeader
        eyebrow="AGENT · AUTONOMOUS"
        title={
          <>
            Agent <span className="df-lime-chip">自动分析</span>
          </>
        }
        description="Agent 将完成数据画像 → 方法推荐 → 多模型尝试 → 评估择优的完整闭环，无需手动配置。"
        extra={
          <div className="df-agent-run">
            <span className="df-caption">候选数</span>
            <InputNumber min={1} max={8} value={maxCandidates} onChange={(v) => setMaxCandidates(v || 3)} />
            <Button type="primary" icon={<ThunderboltOutlined />} loading={loading === 'auto'} onClick={handleAuto}>
              一键自动分析
            </Button>
          </div>
        }
      />

      <div className="df-grid-4">
        <div className="df-card df-agent-action" onClick={handleProfile}>
          <RadarChartOutlined className="df-agent-icon" />
          <div className="df-agent-name">数据画像</div>
          <div className="df-caption">分析数据规模、字段与任务类型</div>
        </div>
        <div className="df-card df-agent-action" onClick={handleRecommend}>
          <BulbOutlined className="df-agent-icon" />
          <div className="df-agent-name">方法推荐</div>
          <div className="df-caption">按画像推荐候选分析方法</div>
        </div>
        <div className="df-card df-agent-action" onClick={handleEvaluate}>
          <AuditOutlined className="df-agent-icon" />
          <div className="df-agent-name">结果评估</div>
          <div className="df-caption">评估当前分析并给出建议</div>
        </div>
        <div className="df-card df-agent-action df-agent-action-primary" onClick={handleAuto}>
          <RobotOutlined className="df-agent-icon" />
          <div className="df-agent-name">自动闭环</div>
          <div className="df-caption">多模型尝试并自动择优</div>
        </div>
      </div>

      <Spin spinning={loading !== null} tip="Agent 工作中…">
        <div className="df-stack">
          {profile && (
            <div className="df-card df-card-lg">
              <div className="df-eyebrow df-card-eyebrow">DATA PROFILE</div>
              <h3 className="df-card-title">数据画像</h3>
              <div className="df-grid-4">
                <StatCard label="行数" value={profile.n_rows} accent="lime" />
                <StatCard label="列数" value={profile.n_cols} accent="violet" />
                <StatCard label="任务类型" value={profile.task_type || '—'} accent="pink" />
                <StatCard label="目标列" value={profile.target_col || '—'} accent="violet" />
              </div>
            </div>
          )}

          {candidates.length > 0 && (
            <div className="df-card df-card-lg">
              <div className="df-eyebrow df-card-eyebrow">RECOMMENDATIONS</div>
              <h3 className="df-card-title">推荐方法（按优先级）</h3>
              <div className="df-candidate-list">
                {candidates.map((c, i) => (
                  <div key={i} className="df-candidate">
                    <span className="df-candidate-rank df-display">{String(i + 1).padStart(2, '0')}</span>
                    <span className="df-code df-candidate-model">{c.model_type}</span>
                    <span className="df-pill df-pill-violet">{c.task_type}</span>
                    <span className="df-caption df-candidate-reason">{c.reason || ''}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {evaluation && (
            <div className="df-card df-card-lg">
              <div className="df-eyebrow df-card-eyebrow">EVALUATION</div>
              <h3 className="df-card-title">评估报告</h3>
              <div className="df-grid-3">
                <StatCard label="评分" value={evaluation.score ?? '—'} accent="lime" hint={evaluation.status} />
                <div className="df-card">
                  <div className="df-micro df-stat-label">建议</div>
                  <div className="df-caption">{evaluation.suggestion || '—'}</div>
                </div>
                <div className="df-card">
                  <div className="df-micro df-stat-label">下一步</div>
                  <div className="df-caption">{evaluation.next_action || '—'}</div>
                </div>
              </div>
            </div>
          )}

          {decision && (
            <div className="df-card df-card-lg">
              <div className="df-eyebrow df-card-eyebrow">DECISION</div>
              <h3 className="df-card-title">
                最终决策：{decision.best ? <span className="df-code">{decision.best.model_type}</span> : '无可用结果'}
              </h3>
              {decision.best && (
                <div className="df-best-row">
                  {Object.entries(decision.best.metrics || {}).map(([k, v]) => (
                    <span key={k} className="df-pill df-pill-done df-code">{k} = {typeof v === 'number' ? v.toFixed(4) : String(v)}</span>
                  ))}
                </div>
              )}
              <Table
                size="small"
                rowKey={(r, i) => `${r.model_type}-${i}`}
                pagination={false}
                columns={attemptColumns}
                dataSource={decision.attempts || []}
                style={{ marginTop: 16 }}
              />
            </div>
          )}

          {!profile && !candidates.length && !evaluation && !decision && (
            <div className="df-card df-empty">
              <RobotOutlined style={{ fontSize: 32 }} />
              <div>点击上方操作卡片，或直接点击「一键自动分析」启动 Agent 闭环</div>
            </div>
          )}
        </div>
      </Spin>
    </div>
  );
};

export default AgentPage;
